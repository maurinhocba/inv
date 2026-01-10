"""
Test script for Portfolio

This script demonstrates and validates Portfolio class functionality.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import trading_backtest
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_backtest.portfolio import Portfolio


def test_initialization():
    """Test portfolio initialization."""
    print("=" * 60)
    print("TEST 1: Portfolio Initialization")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000, commission_buy=0.001, commission_sell=0.001)
    
    print(f"Initial capital: ${portfolio.initial_capital:,.2f}")
    print(f"Cash: ${portfolio.cash:,.2f}")
    print(f"Holdings: {portfolio.holdings}")
    print(f"Total value: ${portfolio.total_value:,.2f}")
    
    assert portfolio.cash == 100000, "Initial cash should equal initial capital"
    assert len(portfolio.holdings) == 0, "Holdings should be empty"
    assert len(portfolio.trades) == 0, "Trade history should be empty"
    
    print("✓ Initialization successful\n")
    return portfolio


def test_buying():
    """Test buying shares."""
    print("=" * 60)
    print("TEST 2: Buying Shares")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000)
    
    # Buy AAPL
    print("Buying 100 shares of AAPL at $150")
    portfolio.buy('AAPL', 100, 150, date=datetime(2023, 1, 1))
    
    cost = 100 * 150
    commission = cost * 0.001
    expected_cash = 100000 - cost - commission
    
    print(f"Cash after purchase: ${portfolio.cash:,.2f}")
    print(f"Expected cash: ${expected_cash:,.2f}")
    print(f"AAPL position: {portfolio.get_position('AAPL')} shares")
    
    assert abs(portfolio.cash - expected_cash) < 0.01, "Cash calculation error"
    assert portfolio.get_position('AAPL') == 100, "Position should be 100 shares"
    
    # Buy MSFT
    print("\nBuying 50 shares of MSFT at $250")
    portfolio.buy('MSFT', 50, 250, date=datetime(2023, 1, 2))
    
    print(f"MSFT position: {portfolio.get_position('MSFT')} shares")
    print(f"Total positions: {len(portfolio.holdings)}")
    
    assert len(portfolio.holdings) == 2, "Should have 2 positions"
    
    print("✓ Buying works correctly\n")
    return portfolio


def test_selling():
    """Test selling shares."""
    print("=" * 60)
    print("TEST 3: Selling Shares")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000)
    portfolio.buy('AAPL', 100, 150, date=datetime(2023, 1, 1))
    
    cash_before = portfolio.cash
    
    # Partial sell
    print("Selling 30 shares of AAPL at $160")
    portfolio.sell_partial('AAPL', 30, 160, date=datetime(2023, 1, 5))
    
    proceeds = 30 * 160
    commission = proceeds * 0.001
    expected_cash = cash_before + proceeds - commission
    
    print(f"Cash after partial sell: ${portfolio.cash:,.2f}")
    print(f"Expected cash: ${expected_cash:,.2f}")
    print(f"Remaining AAPL: {portfolio.get_position('AAPL')} shares")
    
    assert abs(portfolio.cash - expected_cash) < 0.01, "Cash calculation error"
    assert portfolio.get_position('AAPL') == 70, "Should have 70 shares left"
    
    # Full sell
    print("\nSelling entire AAPL position at $165")
    portfolio.sell('AAPL', 165, date=datetime(2023, 1, 10))
    
    print(f"AAPL position after full sell: {portfolio.get_position('AAPL')} shares")
    print(f"Positions remaining: {len(portfolio.holdings)}")
    
    assert portfolio.get_position('AAPL') == 0, "AAPL should be sold"
    assert 'AAPL' not in portfolio.holdings, "AAPL should not be in holdings"
    
    print("✓ Selling works correctly\n")
    return portfolio


def test_value_update():
    """Test portfolio value updating."""
    print("=" * 60)
    print("TEST 4: Portfolio Value Update")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000)
    portfolio.buy('AAPL', 100, 150)
    portfolio.buy('MSFT', 50, 250)
    
    # Update with new prices
    prices = {'AAPL': 160, 'MSFT': 260}
    total_value = portfolio.update_value(prices, date=datetime(2023, 1, 15))
    
    expected_holdings_value = 100 * 160 + 50 * 260
    expected_total = portfolio.cash + expected_holdings_value
    
    print(f"Current prices: {prices}")
    print(f"Holdings value: ${portfolio.get_holdings_value(prices):,.2f}")
    print(f"Expected holdings value: ${expected_holdings_value:,.2f}")
    print(f"Total portfolio value: ${total_value:,.2f}")
    print(f"Expected total: ${expected_total:,.2f}")
    
    assert abs(total_value - expected_total) < 0.01, "Total value calculation error"
    
    print("✓ Value update works correctly\n")
    return portfolio


def test_equal_weight_allocation():
    """Test equal weight allocation."""
    print("=" * 60)
    print("TEST 5: Equal Weight Allocation")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000)
    
    selected_assets = [
        ('AAPL', 1.5),
        ('MSFT', 1.2),
        ('GOOGL', 1.8)
    ]
    
    target_values = portfolio.calculate_target_holdings(
        selected_assets, 
        total_value=90000,
        allocation_method='equal'
    )
    
    print(f"Selected assets: {selected_assets}")
    print(f"Total value to allocate: $90,000")
    print(f"Target values per asset:")
    for ticker, value in target_values.items():
        print(f"  {ticker}: ${value:,.2f}")
    
    expected_value = 90000 / 3
    for ticker, value in target_values.items():
        assert abs(value - expected_value) < 0.01, f"{ticker} should have ${expected_value}"
    
    print("✓ Equal weight allocation works correctly\n")
    return portfolio


def test_score_proportional_allocation():
    """Test score proportional allocation."""
    print("=" * 60)
    print("TEST 6: Score Proportional Allocation")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000)
    
    selected_assets = [
        ('AAPL', 2.0),   # 40% of total score (5.0)
        ('MSFT', 2.0),   # 40%
        ('GOOGL', 1.0)   # 20%
    ]
    
    target_values = portfolio.calculate_target_holdings(
        selected_assets,
        total_value=100000,
        allocation_method='score_proportional'
    )
    
    print(f"Selected assets: {selected_assets}")
    print(f"Total score: {sum(s for _, s in selected_assets)}")
    print(f"Target values by score:")
    for ticker, value in target_values.items():
        score = next(s for t, s in selected_assets if t == ticker)
        pct = (score / 5.0) * 100
        print(f"  {ticker} (score={score}): ${value:,.2f} ({pct:.1f}%)")
    
    assert abs(target_values['AAPL'] - 40000) < 0.01, "AAPL should get $40,000"
    assert abs(target_values['MSFT'] - 40000) < 0.01, "MSFT should get $40,000"
    assert abs(target_values['GOOGL'] - 20000) < 0.01, "GOOGL should get $20,000"
    
    print("✓ Score proportional allocation works correctly\n")
    return portfolio


def test_rebalancing():
    """Test portfolio rebalancing."""
    print("=" * 60)
    print("TEST 7: Portfolio Rebalancing")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000)
    
    # Initial portfolio: 100 AAPL, 50 MSFT
    portfolio.buy('AAPL', 100, 150)
    portfolio.buy('MSFT', 50, 250)
    
    print("Initial holdings:")
    print(f"  AAPL: {portfolio.get_position('AAPL')} shares")
    print(f"  MSFT: {portfolio.get_position('MSFT')} shares")
    print(f"  Cash: ${portfolio.cash:,.2f}")
    
    # New target: sell all MSFT, buy GOOGL
    # Note: In real scenario, we'd calculate shares from target values
    # For this test, we'll manually set target shares
    current_prices = {'AAPL': 160, 'MSFT': 260, 'GOOGL': 140}
    
    # Update total value
    portfolio.update_value(current_prices)
    
    # Calculate new targets (equal weight across AAPL and GOOGL only)
    selected = [('AAPL', 1.0), ('GOOGL', 1.0)]
    target_values = portfolio.calculate_target_holdings(
        selected,
        portfolio.total_value,
        'equal'
    )
    
    # Convert values to shares
    target_shares = {
        ticker: value / current_prices[ticker]
        for ticker, value in target_values.items()
    }
    
    print(f"\nTarget allocation (equal weight AAPL & GOOGL):")
    for ticker, shares in target_shares.items():
        print(f"  {ticker}: {shares:.2f} shares")
    
    # Rebalance
    portfolio.rebalance(target_shares, current_prices, date=datetime(2023, 2, 1))
    
    print(f"\nAfter rebalancing:")
    print(f"  AAPL: {portfolio.get_position('AAPL'):.2f} shares")
    print(f"  MSFT: {portfolio.get_position('MSFT'):.2f} shares")
    print(f"  GOOGL: {portfolio.get_position('GOOGL'):.2f} shares")
    print(f"  Cash: ${portfolio.cash:,.2f}")
    
    assert portfolio.get_position('MSFT') == 0, "MSFT should be sold"
    assert portfolio.get_position('GOOGL') > 0, "Should have GOOGL position"
    
    print("✓ Rebalancing works correctly\n")
    return portfolio


def test_trade_history():
    """Test trade history tracking."""
    print("=" * 60)
    print("TEST 8: Trade History")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000)
    
    # Make some trades
    portfolio.buy('AAPL', 100, 150, date=datetime(2023, 1, 1))
    portfolio.buy('MSFT', 50, 250, date=datetime(2023, 1, 2))
    portfolio.sell_partial('AAPL', 30, 160, date=datetime(2023, 1, 5))
    
    history = portfolio.get_trade_history()
    
    print("Trade history:")
    print(history.to_string(index=False))
    
    print(f"\nTotal trades: {len(history)}")
    print(f"Buys: {len(history[history['action'] == 'buy'])}")
    print(f"Sells: {len(history[history['action'] == 'sell'])}")
    
    assert len(history) == 3, "Should have 3 trades"
    assert len(history[history['action'] == 'buy']) == 2, "Should have 2 buys"
    assert len(history[history['action'] == 'sell']) == 1, "Should have 1 sell"
    
    print("✓ Trade history works correctly\n")
    return portfolio


def test_edge_cases():
    """Test edge cases and error handling."""
    print("=" * 60)
    print("TEST 9: Edge Cases")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=1000)
    
    # Try to buy more than we can afford
    print("Attempting to buy $2000 worth of stock with $1000 cash...")
    portfolio.buy('AAPL', 20, 150)  # Would cost $3000+
    print(f"Cash after attempted purchase: ${portfolio.cash:,.2f}")
    print(f"AAPL shares purchased: {portfolio.get_position('AAPL'):.2f}")
    
    assert portfolio.cash > -1e-8, f"Cash slightly negative due to float error: {portfolio.cash}"
    assert portfolio.get_position('AAPL') > 0, "Should buy what we can afford"
    
    # Try to sell something we don't have
    print("\nAttempting to sell MSFT (not owned)...")
    try:
        portfolio.sell('MSFT', 250)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"Correctly raised error: {e}")
    
    # Try to sell more than we have
    print("\nAttempting to sell more AAPL than owned...")
    try:
        portfolio.sell_partial('AAPL', 1000, 150)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"Correctly raised error: {e}")
    
    print("✓ Edge cases handled correctly\n")


def test_commission_adjusted_shares():
    """Test convert_values_to_shares with commission consideration."""
    print("=" * 60)
    print("TEST 10: Commission-Adjusted Share Calculation")
    print("=" * 60)
    
    portfolio = Portfolio(initial_capital=100000, commission_buy=0.001)
    
    # Target: invest $50,000 in AAPL at $150/share
    target_values = {'AAPL': 50000}
    prices = {'AAPL': 150}
    
    print(f"Target value: ${target_values['AAPL']:,.2f}")
    print(f"Price: ${prices['AAPL']}")
    print(f"Commission: {portfolio.commission_buy * 100}%")
    
    # Convert accounting for commission
    target_shares = portfolio.convert_values_to_shares(target_values, prices)
    
    print(f"\nCalculated shares: {target_shares['AAPL']:.2f}")
    
    # Verify that buying these shares won't exceed available cash
    shares = target_shares['AAPL']
    cost = shares * prices['AAPL']
    commission = cost * portfolio.commission_buy
    total_cost = cost + commission
    
    print(f"Cost: ${cost:,.2f}")
    print(f"Commission: ${commission:,.2f}")
    print(f"Total cost: ${total_cost:,.2f}")
    print(f"Target value: ${target_values['AAPL']:,.2f}")
    
    # Total cost should be ≤ target value (within rounding error)
    assert total_cost <= target_values['AAPL'] + 0.01, "Total cost exceeds target value"
    
    # Actually buy and verify no warnings
    portfolio.buy('AAPL', shares, prices['AAPL'])
    print(f"\n✓ Purchased {shares:.2f} shares without insufficient cash warning")
    print(f"Remaining cash: ${portfolio.cash:,.2f}")
    
    assert portfolio.cash >= 0, "Cash should not be negative"
    
    print("✓ Commission-adjusted calculation works correctly\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PORTFOLIO TEST SUITE")
    print("=" * 60)
    
    try:
        test_initialization()
        test_buying()
        test_selling()
        test_value_update()
        test_equal_weight_allocation()
        test_score_proportional_allocation()
        test_rebalancing()
        test_trade_history()
        test_edge_cases()
        test_commission_adjusted_shares()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
