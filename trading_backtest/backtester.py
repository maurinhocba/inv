"""
Backtester Module

Core backtesting engine that orchestrates DataManager, Portfolio, and Strategy.

Author: Mauro S. Maza - mauromaza8@gmail.com
Version: 0.4.1
Date: 2026-01-09

Changelog:
- 0.4.1: Improved rebalancing logic - separate price dicts for holdings and targets
- 0.4.0: Initial backtester implementation
"""

import pandas as pd
import warnings
from datetime import timedelta
from .data_manager import DataManager
from .portfolio import Portfolio
from .metrics import calculate_metrics


class Backtester:
    """
    Backtesting engine for trading strategies.
    
    Orchestrates data loading, portfolio management, strategy execution,
    and performance measurement.
    """
    
    def __init__(self, data_manager=None):
        """
        Initialize Backtester.
        
        Args:
            data_manager (DataManager, optional): Existing DataManager instance.
                                                  If None, creates new one.
        """
        self.data_manager = data_manager if data_manager else DataManager()
        self.results = None
    
    def run(
        self,
        tickers,
        initial_capital,
        start_date,
        end_date,
        lookback_period,
        holding_period,
        n_assets,
        strategy_func,
        strategy_params=None,
        allocation_method='equal',
        commission_buy=0.001,
        commission_sell=0.001,
        stoploss_func=None,
        stoploss_params=None
    ):
        """
        Run a backtest.
        
        Args:
            tickers (list): Universe of tickers to select from
            initial_capital (float): Starting capital
            start_date (str or datetime): Simulation start date
            end_date (str or datetime): Simulation end date
            lookback_period (int): Days before start_date for initial analysis
            holding_period (int): Days between rebalances (calendar days)
            n_assets (int): Number of assets in portfolio
            strategy_func (callable): Strategy function(data, n, current_date, **params)
                                     Returns: [(ticker, score), ...]
            strategy_params (dict, optional): Parameters for strategy
            allocation_method (str): 'equal' or 'score_proportional'
            commission_buy (float): Buy commission rate
            commission_sell (float): Sell commission rate
            stoploss_func (callable, optional): Stop-loss function (TODO)
            stoploss_params (dict, optional): Parameters for stop-loss (TODO)
        
        Returns:
            dict: Results containing metrics, history, final portfolio, and parameters
        """
        if strategy_params is None:
            strategy_params = {}
        if stoploss_params is None:
            stoploss_params = {}
        
        # Convert dates
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Calculate data download range (need lookback before start)
        data_start = start_date - timedelta(days=lookback_period)
        
        print(f"Downloading data for {len(tickers)} tickers...")
        print(f"Data range: {data_start.date()} to {end_date.date()}")
        
        # Download data
        try:
            data = self.data_manager.get_data(
                tickers=tickers,
                start_date=data_start,
                end_date=end_date
            )
        except Exception as e:
            raise ValueError(f"Failed to download data: {str(e)}")
        
        print(f"Data loaded: {len(data)} rows")
        
        # Initialize portfolio
        portfolio = Portfolio(
            initial_capital=initial_capital,
            commission_buy=commission_buy,
            commission_sell=commission_sell
        )
        
        # Initialize tracking
        history = []
        current_date = start_date
        
        print(f"\nStarting backtest...")
        print(f"Simulation period: {start_date.date()} to {end_date.date()}")
        print(f"Holding period: {holding_period} days")
        print(f"Portfolio size: {n_assets} assets")
        
        iteration = 0
        
        # Main backtest loop
        while current_date <= end_date:
            iteration += 1
            
            # Get available dates in data at or before current_date
            available_dates = data.index.get_level_values('Date').unique()
            available_dates = available_dates[available_dates <= current_date]
            
            if len(available_dates) == 0:
                warnings.warn(f"No data available for {current_date}, skipping")
                current_date += timedelta(days=holding_period)
                continue
            
            # Use the most recent available date
            actual_date = available_dates[-1]
            
            if iteration % 10 == 0:
                print(f"  Iteration {iteration}: {actual_date.date()}")
            
            try:
                # 1. UPDATE PORTFOLIO VALUE AND CHECK STOP-LOSS
                if portfolio.holdings:
                    # 1.1. Get current prices for holdings
                    holding_assets = [(ticker, 0) for ticker in portfolio.holdings]
                    current_prices_holding = self._get_prices(data, actual_date, holding_assets)
                    
                    if not current_prices_holding:
                        warnings.warn(f"No prices available for holdings on {actual_date}, skipping")
                        current_date += timedelta(days=holding_period)
                        continue
                    
                    # 1.2. Update portfolio value
                    portfolio.update_value(current_prices_holding, date=actual_date)
                    
                    # 1.3. TODO: Check stop-loss
                    if stoploss_func is not None:
                        warnings.warn("Stop-loss functionality not yet implemented")
                        # stoploss_triggers = stoploss_func(portfolio, data, actual_date, **stoploss_params)
                        # for ticker in stoploss_triggers:
                        #     if ticker in portfolio.holdings:
                        #         portfolio.sell(ticker, current_prices_holding[ticker], actual_date)
                else:
                    current_prices_holding = {}
                
                # 2. EXECUTE STRATEGY AND REBALANCE
                # 2.1. Execute strategy to select assets
                selected_assets = strategy_func(
                    data,
                    n=n_assets,
                    current_date=actual_date,
                    **strategy_params
                )
                
                if not selected_assets:
                    warnings.warn(f"Strategy returned no assets for {actual_date}, skipping")
                    current_date += timedelta(days=holding_period)
                    continue
                
                # 2.2. Get current prices for selected (target) assets
                current_prices_target = self._get_prices(data, actual_date, selected_assets)
                
                if not current_prices_target:
                    warnings.warn(f"No prices available for selected assets on {actual_date}, skipping")
                    current_date += timedelta(days=holding_period)
                    continue
                
                # 2.3. Calculate target allocation (in dollar values)
                target_values = portfolio.calculate_target_holdings(
                    selected_assets,
                    portfolio.total_value,
                    allocation_method
                )
                
                # 2.4. Convert values to shares accounting for buy commission
                target_shares = portfolio.convert_values_to_shares(
                    target_values,
                    current_prices_target
                )
                
                # 2.5. Rebalance portfolio (needs prices for both holdings and targets)
                all_prices = current_prices_holding | current_prices_target
                portfolio.rebalance(target_shares, all_prices, date=actual_date)
                
                # 3. RECORD SNAPSHOT
                history.append({
                    'date': actual_date,
                    'portfolio_value': portfolio.total_value,
                    'cash': portfolio.cash,
                    'num_positions': len(portfolio.holdings),
                    'holdings': portfolio.holdings.copy(),
                    'selected_tickers': [t for t, s in selected_assets]
                })
                
            except Exception as e:
                warnings.warn(f"Error at {actual_date}: {str(e)}")
            
            # 4. MOVE TO NEXT HOLDING PERIOD
            current_date += timedelta(days=holding_period)
        
        print(f"\nBacktest complete: {iteration} iterations")
        
        # Convert history to DataFrame
        history_df = pd.DataFrame(history)
        
        if history_df.empty:
            raise ValueError("Backtest produced no results - check data and parameters")
        
        # Calculate metrics
        print("Calculating metrics...")
        metrics = calculate_metrics(history_df, initial_capital)
        
        # Compile results
        self.results = {
            'metrics': metrics,
            'history': history_df,
            'final_portfolio': portfolio,
            'parameters': {
                'tickers': tickers,
                'initial_capital': initial_capital,
                'start_date': start_date,
                'end_date': end_date,
                'lookback_period': lookback_period,
                'holding_period': holding_period,
                'n_assets': n_assets,
                'strategy': strategy_func.__name__,
                'strategy_params': strategy_params,
                'allocation_method': allocation_method,
                'commission_buy': commission_buy,
                'commission_sell': commission_sell
            }
        }
        
        return self.results
    
    def _get_prices(self, data, date, selected_assets):
        """
        Get prices for selected assets at a given date.
        
        Args:
            data (DataFrame): Price data
            date (datetime): Date to get prices for
            selected_assets (list): List of (ticker, score) tuples
        
        Returns:
            dict: {ticker: price} for available tickers
        """
        prices = {}
        
        for ticker, score in selected_assets:
            try:
                price = data.loc[(date, ticker), 'Adj Close']
                prices[ticker] = price
            except KeyError:
                warnings.warn(f"No price for {ticker} on {date}")
                continue
        
        return prices
    
    def print_summary(self):
        """Print summary of backtest results."""
        if self.results is None:
            print("No results available. Run backtest first.")
            return
        
        print("\n" + "=" * 60)
        print("BACKTEST SUMMARY")
        print("=" * 60)
        
        params = self.results['parameters']
        print(f"\nParameters:")
        print(f"  Period: {params['start_date'].date()} to {params['end_date'].date()}")
        print(f"  Initial Capital: ${params['initial_capital']:,.2f}")
        print(f"  Universe: {len(params['tickers'])} tickers")
        print(f"  Portfolio Size: {params['n_assets']} assets")
        print(f"  Holding Period: {params['holding_period']} days")
        print(f"  Strategy: {params['strategy']}")
        print(f"  Allocation: {params['allocation_method']}")
        
        metrics = self.results['metrics']
        print(f"\nPerformance Metrics:")
        print(f"  Final Value: ${metrics['final_value']:,.2f}")
        print(f"  Total Return: {metrics['total_return']*100:.2f}%")
        print(f"  Annualized Return (TIR): {metrics['tir']*100:.2f}%")
        print(f"  Sharpe Ratio: {metrics['sharpe']:.3f}")
        print(f"  Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
        print(f"  Volatility (annual): {metrics['volatility']*100:.2f}%")
        print(f"  Number of Rebalances: {metrics['num_rebalances']}")
        
        print("=" * 60)
