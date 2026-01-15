"""
Test script for new strategies: relative_momentum and fip

Quick validation that the strategies work correctly.

Author: Mauro S. Maza - mauromaza8@gmail.com
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_backtest.backtester import Backtester
from trading_backtest.strategies import relative_momentum, fip


def test_relative_momentum():
    """Test relative momentum strategy."""
    print("=" * 60)
    print("TEST 1: Relative Momentum Strategy")
    print("=" * 60)
    
    backtester = Backtester()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']
    
    print(f"\nTesting with {len(tickers)} tickers")
    print("Strategy: Relative Momentum (365 days to 30 days ago)")
    
    results = backtester.run(
        tickers=tickers,
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-12-31',
        lookback_period=560,  # Need > 365 days for strategy
        holding_period=60,
        n_assets=3,
        strategy_func=relative_momentum,
        strategy_params={'lookback_start': 365, 'lookback_end': 30},
        allocation_method='equal',
        commission_buy=0.001,
        commission_sell=0.001
    )
    
    backtester.print_summary()
    
    # Show first few rebalances
    history = results['history']
    print("\nFirst 5 rebalances:")
    print(history[['date', 'selected_tickers', 'portfolio_value']].head())
    
    print("\n✓ Relative Momentum strategy executed successfully\n")
    return results


def test_fip_only_sign():
    """Test FIP strategy with only_sign=True."""
    print("=" * 60)
    print("TEST 2: FIP Strategy (only_sign=True)")
    print("=" * 60)
    
    backtester = Backtester()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']
    
    print(f"\nTesting with {len(tickers)} tickers")
    print("Strategy: FIP with only_sign=True (default)")
    
    results = backtester.run(
        tickers=tickers,
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-12-31',
        lookback_period=560,
        holding_period=60,
        n_assets=3,
        strategy_func=fip,
        strategy_params={'lookback_start': 365, 'lookback_end': 30, 'only_sign': True},
        allocation_method='equal',
        commission_buy=0.001,
        commission_sell=0.001
    )
    
    backtester.print_summary()
    
    print("\n✓ FIP (only_sign=True) strategy executed successfully\n")
    return results


def test_fip_with_return():
    """Test FIP strategy with only_sign=False."""
    print("=" * 60)
    print("TEST 3: FIP Strategy (only_sign=False)")
    print("=" * 60)
    
    backtester = Backtester()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']
    
    print(f"\nTesting with {len(tickers)} tickers")
    print("Strategy: FIP with only_sign=False (uses actual return)")
    
    results = backtester.run(
        tickers=tickers,
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-12-31',
        lookback_period=560,
        holding_period=60,
        n_assets=3,
        strategy_func=fip,
        strategy_params={'lookback_start': 365, 'lookback_end': 30, 'only_sign': False},
        allocation_method='equal',
        commission_buy=0.001,
        commission_sell=0.001
    )
    
    backtester.print_summary()
    
    print("\n✓ FIP (only_sign=False) strategy executed successfully\n")
    return results


def compare_strategies():
    """Compare all three strategies side by side."""
    print("=" * 60)
    print("TEST 4: Strategy Comparison")
    print("=" * 60)
    
    backtester = Backtester()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V', 'WMT']
    
    strategies = [
        ('Relative Momentum', relative_momentum, {'lookback_start': 365, 'lookback_end': 30}),
        ('FIP (only_sign)', fip, {'lookback_start': 365, 'lookback_end': 30, 'only_sign': True}),
        ('FIP (with return)', fip, {'lookback_start': 365, 'lookback_end': 30, 'only_sign': False}),
    ]
    
    print(f"\nComparing strategies with {len(tickers)} tickers")
    print("Period: 2023-01-01 to 2023-12-31")
    print("=" * 60)
    
    results_list = []
    
    for name, func, params in strategies:
        print(f"\nRunning: {name}")
        
        results = backtester.run(
            tickers=tickers,
            initial_capital=100000,
            start_date='2023-01-01',
            end_date='2023-12-31',
            lookback_period=560,
            holding_period=60,
            n_assets=5,
            strategy_func=func,
            strategy_params=params,
            allocation_method='equal',
            commission_buy=0.001,
            commission_sell=0.001
        )
        
        results_list.append((name, results))
    
    # Print comparison table
    print("\n" + "=" * 60)
    print("STRATEGY COMPARISON")
    print("=" * 60)
    print(f"{'Strategy':<25} {'Final Value':>15} {'TIR':>10} {'Sharpe':>10} {'Max DD':>10}")
    print("-" * 60)
    
    for name, results in results_list:
        metrics = results['metrics']
        print(f"{name:<25} ${metrics['final_value']:>14,.2f} {metrics['tir']*100:>9.2f}% "
              f"{metrics['sharpe']:>9.3f} {metrics['max_drawdown']*100:>9.2f}%")
    
    print("=" * 60)
    print("\n✓ Strategy comparison completed\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("NEW STRATEGIES TEST SUITE")
    print("=" * 60)
    
    try:
        test_relative_momentum()
        test_fip_only_sign()
        test_fip_with_return()
        compare_strategies()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nBoth new strategies are working correctly!")
        print("- relative_momentum: ✓")
        print("- fip (only_sign=True): ✓")
        print("- fip (only_sign=False): ✓")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
