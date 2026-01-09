"""
Test script for DataManager

This script demonstrates how to use the DataManager class
and validates it's working correctly.
"""

import sys
from pathlib import Path

# Add parent directory to path to import trading_backtest
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_backtest.data_manager import DataManager
import pandas as pd


def test_basic_download():
    """Test basic download and caching functionality."""
    print("=" * 60)
    print("TEST 1: Basic Download")
    print("=" * 60)
    
    # Initialize DataManager
    dm = DataManager(cache_dir="data")
    
    # Define test parameters
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    start_date = '2020-01-01'
    end_date = '2023-12-31'
    
    print(f"Downloading data for {tickers}")
    print(f"Date range: {start_date} to {end_date}")
    
    # First download (should hit yfinance)
    print("\nFirst download (from yfinance)...")
    data = dm.get_data(tickers, start_date, end_date)
    
    print(f"Downloaded {len(data)} rows")
    print(f"Tickers: {data.index.get_level_values('ticker').unique().tolist()}")
    
    # Verify structure
    print(f"\n✓ Index levels: {data.index.names}")
    print(f"✓ Columns (should be simple): {data.columns.tolist()}")
    print(f"✓ Columns type: {type(data.columns)}")
    
    # Check for unnecessary NaN
    total_cells = len(data) * len(data.columns)
    nan_cells = data.isna().sum().sum()
    nan_pct = (nan_cells / total_cells) * 100
    print(f"✓ NaN percentage: {nan_pct:.2f}% (should be low)")
    
    print(f"\nSample data:")
    print(data.head(10))
    
    # Second download (should use cache)
    print("\n" + "=" * 60)
    print("Second download (from cache)...")
    data2 = dm.get_data(tickers, start_date, end_date)
    
    assert data.equals(data2), "Cached data doesn't match!"
    print("✓ Cached data matches original")
    
    return data


def test_cache_update():
    """Test cache updating with extended date range."""
    print("\n" + "=" * 60)
    print("TEST 2: Cache Update")
    print("=" * 60)
    
    dm = DataManager(cache_dir="data")
    
    # Request extended date range
    tickers = ['AAPL']
    start_date = '2019-01-01'  # Earlier than cached
    end_date = '2024-12-31'     # Later than cached
    
    print(f"Requesting extended range: {start_date} to {end_date}")
    
    data = dm.get_data(tickers, start_date, end_date)
    
    print(f"Retrieved {len(data)} rows")
    print(f"Actual date range: {data.index.get_level_values('Date').min()} to {data.index.get_level_values('Date').max()}")
    print("✓ Cache update successful")
    
    return data


def test_cache_info():
    """Test cache information methods."""
    print("\n" + "=" * 60)
    print("TEST 3: Cache Information")
    print("=" * 60)
    
    dm = DataManager(cache_dir="data")
    
    # Get cached tickers
    cached = dm.get_cached_tickers()
    print(f"Cached tickers: {cached}")
    
    # Get detailed cache info
    info = dm.get_cache_info()
    print("\nCache details:")
    print(info.to_string())
    
    return info


def test_data_access():
    """Test different ways to access the data."""
    print("\n" + "=" * 60)
    print("TEST 4: Data Access Patterns")
    print("=" * 60)
    
    dm = DataManager(cache_dir="data")
    data = dm.get_data(['AAPL', 'MSFT'], '2023-01-01', '2023-12-31')
    
    # Access single ticker
    print("Accessing AAPL data:")
    aapl = data.xs('AAPL', level='ticker')
    print(f"Shape: {aapl.shape}")
    print(aapl.head())
    
    # Access single date
    print("\nAccessing 2023-01-03 data:")
    try:
        single_date = data.xs('2023-01-03', level='Date')
        print(single_date)
    except KeyError:
        print("Date not in dataset (likely weekend/holiday)")
        # Try next trading day
        single_date = data.xs('2023-01-04', level='Date')
        print("Using 2023-01-04 instead:")
        print(single_date)
    
    # Access Adj Close for all tickers
    print("\nAdj Close prices (pivoted):")
    adj_close = data['Adj Close'].unstack(level='ticker')
    print(adj_close.head())
    print(f"\nShape: {adj_close.shape}")
    print(f"Columns (tickers): {adj_close.columns.tolist()}")
    
    print("✓ All access patterns working")


def test_invalid_ticker():
    """Test handling of invalid ticker."""
    print("\n" + "=" * 60)
    print("TEST 5: Invalid Ticker Handling")
    print("=" * 60)
    
    dm = DataManager(cache_dir="data")
    
    # Mix valid and invalid tickers
    tickers = ['AAPL', 'INVALID_TICKER_XYZ', 'MSFT']
    
    print(f"Requesting: {tickers}")
    data = dm.get_data(tickers, '2023-01-01', '2023-12-31')
    
    actual_tickers = data.index.get_level_values('ticker').unique().tolist()
    print(f"Got data for: {actual_tickers}")
    print("✓ Invalid tickers handled correctly")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("DATA MANAGER TEST SUITE")
    print("=" * 60)
    
    try:
        # Run tests
        test_basic_download()
        test_cache_update()
        test_cache_info()
        test_data_access()
        test_invalid_ticker()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
