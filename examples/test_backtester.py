"""
Test script for Backtester

This script demonstrates end-to-end backtesting with the Price to SMA Ratio strategy.

Author: Mauro S. Maza - mauromaza8@gmail.com
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_backtest.backtester import Backtester
from trading_backtest.strategies import price_to_sma_ratio


def test_basic_backtest():
    """Test basic backtest with SMA ratio strategy."""
    print("=" * 60)
    print("TEST 1: Basic Backtest")
    print("=" * 60)
    
    # Initialize backtester
    backtester = Backtester()
    
    # Define parameters
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 
               'NVDA', 'TSLA', 'JPM', 'V', 'WMT']
    
    print(f"\nRunning backtest with {len(tickers)} tickers...")
    
    # Run backtest
    results = backtester.run(
        tickers=tickers,
        initial_capital=100000,
        start_date='2022-01-01',
        end_date='2023-12-31',
        lookback_period=100,  # 100 days before start for initial SMA calculation
        holding_period=30,    # Rebalance monthly
        n_assets=5,           # Hold 5 stocks at a time
        strategy_func=price_to_sma_ratio,
        strategy_params={'m': 50},  # 50-day SMA
        allocation_method='equal',
        commission_buy=0.001,
        commission_sell=0.001
    )
    
    # Print summary
    backtester.print_summary()
    
    # Verify results structure
    assert 'metrics' in results, "Results should contain metrics"
    assert 'history' in results, "Results should contain history"
    assert 'final_portfolio' in results, "Results should contain final portfolio"
    assert 'parameters' in results, "Results should contain parameters"
    
    # Verify metrics
    metrics = results['metrics']
    assert 'tir' in metrics, "Metrics should contain TIR"
    assert 'sharpe' in metrics, "Metrics should contain Sharpe"
    assert 'max_drawdown' in metrics, "Metrics should contain max drawdown"
    
    # Verify history
    history = results['history']
    assert len(history) > 0, "History should not be empty"
    assert 'portfolio_value' in history.columns, "History should track portfolio value"
    
    print("\n✓ Basic backtest successful\n")
    return results


def test_different_holding_periods():
    """Test backtests with different holding periods."""
    print("=" * 60)
    print("TEST 2: Different Holding Periods")
    print("=" * 60)
    
    backtester = Backtester()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    holding_periods = [15, 30, 60]
    results_list = []
    
    for hp in holding_periods:
        print(f"\nTesting holding period: {hp} days")
        
        results = backtester.run(
            tickers=tickers,
            initial_capital=100000,
            start_date='2023-01-01',
            end_date='2023-12-31',
            lookback_period=100,
            holding_period=hp,
            n_assets=3,
            strategy_func=price_to_sma_ratio,
            strategy_params={'m': 50},
            allocation_method='equal',
            commission_buy=0.001,
            commission_sell=0.001
        )
        
        results_list.append(results)
        
        print(f"  TIR: {results['metrics']['tir']*100:.2f}%")
        print(f"  Sharpe: {results['metrics']['sharpe']:.3f}")
        print(f"  Rebalances: {results['metrics']['num_rebalances']}")
    
    print("\n✓ Different holding periods tested\n")
    return results_list


def test_allocation_methods():
    """Test different allocation methods."""
    print("=" * 60)
    print("TEST 3: Allocation Methods")
    print("=" * 60)
    
    backtester = Backtester()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    methods = ['equal', 'score_proportional']
    
    for method in methods:
        print(f"\nTesting allocation method: {method}")
        
        results = backtester.run(
            tickers=tickers,
            initial_capital=100000,
            start_date='2023-01-01',
            end_date='2023-12-31',
            lookback_period=100,
            holding_period=30,
            n_assets=3,
            strategy_func=price_to_sma_ratio,
            strategy_params={'m': 50},
            allocation_method=method,
            commission_buy=0.001,
            commission_sell=0.001
        )
        
        print(f"  Final value: ${results['metrics']['final_value']:,.2f}")
        print(f"  Total return: {results['metrics']['total_return']*100:.2f}%")
        print(f"  TIR: {results['metrics']['tir']*100:.2f}%")
    
    print("\n✓ Allocation methods tested\n")


def test_portfolio_evolution():
    """Test that portfolio evolves correctly over time."""
    print("=" * 60)
    print("TEST 4: Portfolio Evolution")
    print("=" * 60)
    
    backtester = Backtester()
    
    results = backtester.run(
        tickers=['AAPL', 'MSFT', 'GOOGL'],
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-06-30',
        lookback_period=100,
        holding_period=30,
        n_assets=2,
        strategy_func=price_to_sma_ratio,
        strategy_params={'m': 30},
        allocation_method='equal'
    )
    
    history = results['history']
    
    print(f"\nPortfolio evolution over {len(history)} rebalances:")
    print(history[['date', 'portfolio_value', 'cash', 'num_positions']].head(10))
    
    # Verify portfolio value is always positive
    assert (history['portfolio_value'] > 0).all(), "Portfolio value should always be positive"
    
    # Verify number of positions <= n_assets
    assert (history['num_positions'] <= 2).all(), "Should not exceed target portfolio size"
    
    print("\n✓ Portfolio evolution correct\n")


def test_commission_impact():
    """Test impact of different commission rates."""
    print("=" * 60)
    print("TEST 5: Commission Impact")
    print("=" * 60)
    
    backtester = Backtester()
    
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    commission_rates = [0, 0.001, 0.005]  # 0%, 0.1%, 0.5%
    
    print("\nComparing different commission rates:")
    print("*" * 40)
    print(f"\n\n")
    
    for rate in commission_rates:
        results = backtester.run(
            tickers=tickers,
            initial_capital=100000,
            start_date='2023-01-01',
            end_date='2023-12-31',
            lookback_period=100,
            holding_period=30,
            n_assets=2,
            strategy_func=price_to_sma_ratio,
            strategy_params={'m': 50},
            allocation_method='equal',
            commission_buy=rate,
            commission_sell=rate
        )
        
        print(f"\n  Commission: {rate*100}%")
        print(f"    Final value: ${results['metrics']['final_value']:,.2f}")
        print(f"    Total return: {results['metrics']['total_return']*100:.2f}%")
        print(f"\n\n")
    
    print("\n✓ Commission impact analyzed\n")


def test_empty_portfolio_start():
    """Test backtest starting from empty portfolio (first rebalance)."""
    print("=" * 60)
    print("TEST 6: Empty Portfolio Start")
    print("=" * 60)
    
    backtester = Backtester()
    
    print("\nTesting first rebalance from empty portfolio...")
    
    results = backtester.run(
        tickers=['AAPL', 'MSFT', 'GOOGL'],
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-03-31',
        lookback_period=100,
        holding_period=30,
        n_assets=3,
        strategy_func=price_to_sma_ratio,
        strategy_params={'m': 50},
        allocation_method='equal'
    )
    
    history = results['history']
    first_rebalance = history.iloc[0]
    
    print(f"First rebalance date: {first_rebalance['date']}")
    print(f"Positions after first rebalance: {first_rebalance['num_positions']}")
    print(f"Cash after first rebalance: ${first_rebalance['cash']:,.2f}")
    print(f"Portfolio value: ${first_rebalance['portfolio_value']:,.2f}")
    
    # Should have bought positions on first rebalance
    assert first_rebalance['num_positions'] > 0, "Should buy assets on first rebalance"
    assert first_rebalance['num_positions'] <= 3, "Should not exceed target size"
    
    print("\n✓ Empty portfolio start handled correctly\n")


def test_no_selling_rebalance():
    """Test rebalance where all selected assets are maintained (no sells)."""
    print("=" * 60)
    print("TEST 7: No-Sell Rebalance")
    print("=" * 60)
    
    # This is hard to guarantee with real market data, so we test
    # that the system handles it without errors
    
    backtester = Backtester()
    
    print("\nRunning backtest to observe rebalancing behavior...")
    
    results = backtester.run(
        tickers=['AAPL', 'MSFT'],  # Small universe
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-06-30',
        lookback_period=100,
        holding_period=60,  # Longer period = fewer rebalances
        n_assets=2,         # Hold both = likely to keep same assets
        strategy_func=price_to_sma_ratio,
        strategy_params={'m': 50},
        allocation_method='equal'
    )
    
    history = results['history']
    
    # Check if any rebalance maintained all positions
    maintained_all = 0
    for i in range(1, len(history)):
        prev_tickers = set(history.iloc[i-1]['selected_tickers'])
        curr_tickers = set(history.iloc[i]['selected_tickers'])
        if prev_tickers == curr_tickers:
            maintained_all += 1
    
    print(f"\nRebalances that maintained all positions: {maintained_all}/{len(history)-1}")
    print(f"Final portfolio value: ${results['metrics']['final_value']:,.2f}")
    
    print("\n✓ No-sell rebalances handled correctly\n")


def test_complete_turnover_rebalance():
    """Test rebalance with complete portfolio turnover (sell all, buy all new)."""
    print("=" * 60)
    print("TEST 8: Complete Turnover Rebalance")
    print("=" * 60)
    
    # Use larger universe and smaller portfolio to increase turnover likelihood
    
    backtester = Backtester()
    
    print("\nRunning backtest with high potential for turnover...")
    
    results = backtester.run(
        tickers=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-12-31',
        lookback_period=100,
        holding_period=15,  # Frequent rebalancing
        n_assets=2,         # Small portfolio
        strategy_func=price_to_sma_ratio,
        strategy_params={'m': 20},  # Shorter SMA = more volatility in rankings
        allocation_method='score_proportional'  # May cause more variation
    )
    
    history = results['history']
    
    # Check for complete turnovers
    complete_turnovers = 0
    for i in range(1, len(history)):
        prev_tickers = set(history.iloc[i-1]['selected_tickers'])
        curr_tickers = set(history.iloc[i]['selected_tickers'])
        if len(prev_tickers & curr_tickers) == 0:  # No overlap
            complete_turnovers += 1
    
    print(f"\nComplete turnovers: {complete_turnovers}/{len(history)-1}")
    print(f"Total rebalances: {results['metrics']['num_rebalances']}")
    print(f"Final portfolio value: ${results['metrics']['final_value']:,.2f}")
    
    # System should handle complete turnovers without error
    assert results['metrics']['final_value'] > 0, "Portfolio should have positive value"
    
    print("\n✓ Complete turnover rebalances handled correctly\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BACKTESTER TEST SUITE")
    print("=" * 60)
    
    try:
        test_basic_backtest()
        test_different_holding_periods()
        test_allocation_methods()
        test_portfolio_evolution()
        test_commission_impact()
        test_empty_portfolio_start()
        test_no_selling_rebalance()
        test_complete_turnover_rebalance()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nNote: These tests use real market data.")
        print("Results will vary based on market conditions during test periods.")
        
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
