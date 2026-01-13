"""
Portfolio Module

Manages portfolio holdings, cash, and trading operations.

Author: Mauro S. Maza - mauromaza8@gmail.com
Version: 0.3.2
Date: 2026-01-09

Changelog:
- 0.3.2: Improved rebalancing to account for sell commissions; relaxed cash validation
- 0.3.1: Added convert_values_to_shares() for commission-adjusted calculations
- 0.3.0: Initial Portfolio implementation

TODO:
- Refactor to work entirely with monetary values instead of mixing values and shares.
  Current design mixes values ($) and shares, complicating commission calculations.
  Proposed: All internal calculations in values, convert to shares only at final trade execution.
"""

import pandas as pd
import warnings
from datetime import datetime


class Portfolio:
    """
    Manages a trading portfolio with holdings, cash, and transaction history.
    
    Attributes:
        initial_capital (float): Starting capital
        cash (float): Current cash available
        holdings (dict): Current positions {ticker: shares}
        commission_buy (float): Buy commission rate (e.g., 0.001 = 0.1%)
        commission_sell (float): Sell commission rate
        trades (list): History of all trades
        total_value (float): Current total portfolio value (cash + holdings)
    """
    
    def __init__(self, initial_capital, commission_buy=0.001, commission_sell=0.001):
        """
        Initialize Portfolio.
        
        Args:
            initial_capital (float): Starting capital
            commission_buy (float): Commission rate for buys (default 0.1%)
            commission_sell (float): Commission rate for sells (default 0.1%)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.holdings = {}  # {ticker: shares}
        self.commission_buy = commission_buy
        self.commission_sell = commission_sell
        self.trades = []
        self.total_value = initial_capital
    
    # =========================
    # CORE OPERATIONS
    # =========================
    
    def buy(self, ticker, shares, price, date=None):
        """
        Buy shares of a ticker.
        
        Args:
            ticker (str): Ticker symbol
            shares (float): Number of shares to buy (can be fractional)
            price (float): Price per share
            date (datetime, optional): Trade date for record keeping
        
        Raises:
            ValueError: If insufficient cash available
        """
        if shares <= 0:
            raise ValueError(f"Cannot buy non-positive shares: {shares}")
        
        cost = shares * price
        commission = cost * self.commission_buy
        total_cost = cost + commission
        
        # TODO: Review - should we raise exception or adjust shares to fit cash?
        if total_cost > self.cash:
            # Only warn if difference is significant (> $1, not just floating point error)
            if total_cost - self.cash > 1:
                warnings.warn(
                    f"Insufficient cash for {ticker}: need ${total_cost:.2f}, have ${self.cash:.2f}. "
                    f"Difference is ${total_cost - self.cash:.2f}. "
                    f"Buying maximum possible."
                )
            # Buy maximum possible
            max_cost = self.cash / (1 + self.commission_buy)
            shares = max_cost / price
            cost = shares * price
            commission = cost * self.commission_buy
            total_cost = cost + commission
        
        self.cash -= total_cost
        self.holdings[ticker] = self.holdings.get(ticker, 0) + shares
        
        self._record_trade(date, ticker, 'buy', shares, price, commission, cost)
    
    def sell(self, ticker, price, date=None):
        """
        Sell entire position of a ticker.
        
        Args:
            ticker (str): Ticker symbol
            price (float): Price per share
            date (datetime, optional): Trade date for record keeping
        
        Raises:
            ValueError: If ticker not in holdings
        """
        if ticker not in self.holdings:
            raise ValueError(f"Cannot sell {ticker}: not in holdings")
        
        shares = self.holdings[ticker]
        self.sell_partial(ticker, shares, price, date)
    
    def sell_partial(self, ticker, shares, price, date=None):
        """
        Sell a specific number of shares of a ticker.
        
        Args:
            ticker (str): Ticker symbol
            shares (float): Number of shares to sell
            price (float): Price per share
            date (datetime, optional): Trade date for record keeping
        
        Raises:
            ValueError: If insufficient shares or ticker not in holdings
        """
        if ticker not in self.holdings:
            raise ValueError(f"Cannot sell {ticker}: not in holdings")
        
        if shares <= 0:
            raise ValueError(f"Cannot sell non-positive shares: {shares}")
        
        if shares > self.holdings[ticker]:
            raise ValueError(
                f"Cannot sell {shares} shares of {ticker}: only {self.holdings[ticker]} available"
            )
        
        proceeds = shares * price
        commission = proceeds * self.commission_sell
        net_proceeds = proceeds - commission
        
        self.cash += net_proceeds
        self.holdings[ticker] -= shares
        
        # Remove ticker if position is now zero (or very close to zero)
        if abs(self.holdings[ticker]) < 1e-10:
            del self.holdings[ticker]
        
        self._record_trade(date, ticker, 'sell', shares, price, commission, proceeds)
    
    def update_value(self, prices_dict, date=None):
        """
        Update total portfolio value based on current prices.
        
        Args:
            prices_dict (dict): {ticker: current_price}
            date (datetime, optional): Date for the valuation
        
        Returns:
            float: Total portfolio value
        """
        holdings_value = self.get_holdings_value(prices_dict)
        self.total_value = self.cash + holdings_value
        return self.total_value
    
    # =========================
    # REBALANCING
    # =========================
    
    def calculate_target_holdings(self, selected_assets, total_value, allocation_method='equal'):
        """
        Calculate target holdings based on allocation method.
        
        Args:
            selected_assets (list): List of (ticker, score) tuples
            total_value (float): Total value to allocate
            allocation_method (str): 'equal' or 'score_proportional'
        
        Returns:
            dict: {ticker: target_value} (in dollars, not shares)
        
        Raises:
            ValueError: If allocation_method is unknown
        """
        if allocation_method == 'equal':
            return self._equal_weight(selected_assets, total_value)
        elif allocation_method == 'score_proportional':
            return self._score_proportional(selected_assets, total_value)
        else:
            raise ValueError(f"Unknown allocation method: {allocation_method}")
    
    def rebalance(self, target_holdings, prices_dict, date=None):
        """
        Rebalance portfolio to match target holdings.
        
        Uses incremental approach:
        1. Sell positions not in target or that need reduction
        2. Adjust buy quantities to account for value lost to sell commissions
        3. Buy new positions or increase existing ones
        
        Args:
            target_holdings (dict): {ticker: target_shares}
            prices_dict (dict): {ticker: current_price}
            date (datetime, optional): Trade date
        
        Note:
            TODO: Review rebalancing logic - current implementation is incremental.
            May need optimization for transaction costs or more sophisticated ordering.
            
            TODO (CRITICAL): Refactor to work with monetary values throughout instead of
            mixing shares and values. This would simplify commission handling significantly.
        """
        
        # Track portfolio value to calculate commission impact
        self.update_value(prices_dict, date)
        portfolio_value_initial = self.total_value
        cash_initial = self.cash
        
        # Step 1: Sell what we don't need or need to reduce
        for ticker in list(self.holdings.keys()):
            current_shares = self.holdings[ticker]
            target_shares = target_holdings.get(ticker, 0)
            
            if target_shares == 0:
                # Sell entire position
                self.sell(ticker, prices_dict[ticker], date)
            elif target_shares < current_shares:
                # Reduce position
                shares_to_sell = current_shares - target_shares
                self.sell_partial(ticker, shares_to_sell, prices_dict[ticker], date)
        
        # Calculate value lost to sell commissions
        self.update_value(prices_dict, date)
        portfolio_value_after_sell = self.total_value
        value_lost = portfolio_value_initial - portfolio_value_after_sell
        
        # Debug output for commission tracking (can be commented out if too verbose)
        if value_lost > 0.01:  # Only print if meaningful (> 1 cent)
            print(f"Value lost to sell commissions on {date}: ${value_lost:.2f}")
        
        # Adjust buy quantities to account for sell commission losses
        if value_lost > 0.01:  # Use 1 cent threshold to avoid floating point issues
            cash_after_sell = self.cash
            cash_intended_to_buy = cash_after_sell - cash_initial + value_lost
            fraction_to_buy = (cash_intended_to_buy - value_lost) / cash_intended_to_buy
        else:
            fraction_to_buy = 1.0
        
        # Step 2: Buy what we need or need to increase
        for ticker, target_shares in target_holdings.items():
            current_shares = self.holdings.get(ticker, 0)
            
            if target_shares > current_shares:
                # Buy new or increase position
                shares_to_buy = (target_shares - current_shares) * fraction_to_buy
                
                # Check if we have enough cash
                cost = shares_to_buy * prices_dict[ticker]
                total_cost = cost * (1 + self.commission_buy)
                
                if total_cost <= self.cash:
                    self.buy(ticker, shares_to_buy, prices_dict[ticker], date)
                else:
                    # Buy what we can afford
                    if (total_cost - self.cash) > 1:
                        warnings.warn(
                            f"Insufficient cash to buy {shares_to_buy:.2f} shares of {ticker}. "
                            f"Difference is ${total_cost - self.cash:.2f}. "
                            f"Buying maximum possible with remaining cash."
                        )
                    if self.cash > 0:
                        max_shares = self.cash / (prices_dict[ticker] * (1 + self.commission_buy))
                        if max_shares > 0:
                            self.buy(ticker, max_shares, prices_dict[ticker], date)
    
    # =========================
    # ALLOCATION METHODS
    # =========================
    
    def _equal_weight(self, selected_assets, total_value):
        """
        Distribute value equally among selected assets.
        
        Args:
            selected_assets (list): List of (ticker, score) tuples
            total_value (float): Total value to distribute
        
        Returns:
            dict: {ticker: target_value} - Values in dollars, not shares
                  Actual share counts calculated during rebalance with prices
        """
        n = len(selected_assets)
        if n == 0:
            return {}
        
        value_per_asset = total_value / n
        
        return {ticker: value_per_asset for ticker, score in selected_assets}
    
    def _score_proportional(self, selected_assets, total_value):
        """
        Distribute value proportionally to scores.
        
        Args:
            selected_assets (list): List of (ticker, score) tuples
            total_value (float): Total value to distribute
        
        Returns:
            dict: {ticker: target_value}
        """
        if not selected_assets:
            return {}
        
        total_score = sum(score for ticker, score in selected_assets)
        
        if total_score == 0:
            warnings.warn("Total score is 0, falling back to equal weight")
            return self._equal_weight(selected_assets, total_value)
        
        return {
            ticker: (score / total_score) * total_value 
            for ticker, score in selected_assets
        }
    
    # =========================
    # UTILITIES
    # =========================
    
    def convert_values_to_shares(self, target_values, prices_dict):
        """
        Convert target monetary values to shares, accounting for buy commissions.
        
        CRITICAL: When allocating capital, must account for commission BEFORE calculating shares.
        If you have $10,000 and commission is 0.1%, you can only buy $10,000 / 1.001 = $9,990 worth.
        
        Args:
            target_values (dict): {ticker: target_value_in_dollars}
            prices_dict (dict): {ticker: current_price}
        
        Returns:
            dict: {ticker: shares_to_buy}
        
        Example:
            >>> portfolio = Portfolio(initial_capital=100000, commission_buy=0.001)
            >>> target_values = {'AAPL': 50000, 'MSFT': 50000}
            >>> prices = {'AAPL': 150, 'MSFT': 250}
            >>> shares = portfolio.convert_values_to_shares(target_values, prices)
            >>> # AAPL: 50000 / 1.001 / 150 = 333.11 shares
            >>> # MSFT: 50000 / 1.001 / 250 = 199.87 shares
        """
        target_shares = {}
        
        for ticker, target_value in target_values.items():
            if ticker not in prices_dict:
                warnings.warn(f"No price available for {ticker}, skipping")
                continue
            
            # CRITICAL: Adjust for commission BEFORE calculating shares
            value_for_shares = target_value / (1 + self.commission_buy)
            shares = value_for_shares / prices_dict[ticker]
            target_shares[ticker] = shares
        
        return target_shares
    
    def get_holdings_value(self, prices_dict):
        """
        Calculate current value of all holdings.
        
        Args:
            prices_dict (dict): {ticker: current_price}
        
        Returns:
            float: Total value of holdings
        """
        total = 0
        for ticker, shares in self.holdings.items():
            if ticker in prices_dict:
                total += shares * prices_dict[ticker]
            else:
                warnings.warn(f"No price available for {ticker}, using 0")
        return total
    
    def get_position(self, ticker):
        """
        Get current position in a ticker.
        
        Args:
            ticker (str): Ticker symbol
        
        Returns:
            float: Number of shares (0 if not held)
        """
        return self.holdings.get(ticker, 0)
    
    def get_trade_history(self):
        """
        Get trade history as DataFrame.
        
        Returns:
            pd.DataFrame: All trades with columns [date, ticker, action, shares, price, commission, value]
        """
        if not self.trades:
            return pd.DataFrame(columns=['date', 'ticker', 'action', 'shares', 'price', 'commission', 'value'])
        
        return pd.DataFrame(self.trades)
    
    def _record_trade(self, date, ticker, action, shares, price, commission, value):
        """
        Record a trade in history.
        
        Args:
            date (datetime): Trade date
            ticker (str): Ticker symbol
            action (str): 'buy' or 'sell'
            shares (float): Number of shares
            price (float): Price per share
            commission (float): Commission paid
            value (float): Total value (shares * price)
        """
        self.trades.append({
            'date': date if date else datetime.now(),
            'ticker': ticker,
            'action': action,
            'shares': shares,
            'price': price,
            'commission': commission,
            'value': value
        })
    
    def __repr__(self):
        """String representation of portfolio."""
        return (
            f"Portfolio(cash=${self.cash:.2f}, "
            f"holdings_value=${self.get_holdings_value({}) if not self.holdings else 'N/A'}, "
            f"total_value=${self.total_value:.2f}, "
            f"positions={len(self.holdings)})"
        )
