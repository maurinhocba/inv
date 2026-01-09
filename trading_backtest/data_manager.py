"""
Data Manager Module (Production Version)

Robust historical price data manager using Yahoo Finance.

Author: [Your Name]
Version: 0.2.1
Date: 2026-01-09

Changelog:
- 0.2.1: Bugfixes for edge cases - MultiIndex handling, datetime conversion, validation
- 0.2.0: Major refactor - simplified cache logic, fixed duplicate index issues
- 0.1.2: Fixed DataFrame structure (eliminated MultiIndex in columns)
- 0.1.1: Fixed compatibility with yfinance 1.0.x (auto_adjust, iloc fixes)
- 0.1.0: Initial release
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import timedelta
import warnings
from concurrent.futures import ThreadPoolExecutor


class DataManager:
    """
    Manages historical price data with caching and validation.
    
    Attributes:
        cache_dir (Path): Directory where parquet files are stored
        validate_on_load (bool): Whether to validate data when loading from cache
    """

    def __init__(self, cache_dir="data", validate_on_load=True):
        """
        Initialize DataManager.
        
        Args:
            cache_dir (str): Path to cache directory
            validate_on_load (bool): Validate cached data when loading
        """
        self.cache_dir = Path(cache_dir)
        self.validate_on_load = validate_on_load
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # =========================
    # PUBLIC API
    # =========================

    def get_data(self, tickers, start_date, end_date, force_download=False, n_jobs=1):
        """
        Get historical data for multiple tickers.
        
        Args:
            tickers (list): List of ticker symbols (e.g., ['AAPL', 'MSFT'])
            start_date (str or datetime): Start date ('YYYY-MM-DD' or datetime)
            end_date (str or datetime): End date ('YYYY-MM-DD' or datetime)
            force_download (bool): If True, ignore cache and download fresh data
            n_jobs (int): Number of parallel downloads (1 = sequential)
        
        Returns:
            pd.DataFrame: MultiIndex DataFrame with (Date, ticker) index and columns:
                         [Open, High, Low, Close, Volume, Adj Close]
        
        Raises:
            ValueError: If no valid tickers remain after download/validation
        """
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        def task(t):
            return self._get_and_normalize_single(t, start_date, end_date, force_download)

        if n_jobs == 1:
            results = [task(t) for t in tickers]
        else:
            with ThreadPoolExecutor(max_workers=n_jobs) as ex:
                results = list(ex.map(task, tickers))

        data_frames = [r for r in results if r is not None]

        if not data_frames:
            raise ValueError("No valid data obtained for any ticker")

        combined = pd.concat(data_frames, ignore_index=True)

        essential = ['Date', 'ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
        combined = combined[[c for c in essential if c in combined.columns]]

        combined = combined.set_index(['Date', 'ticker']).sort_index()

        return combined

    # =========================
    # NORMALIZATION
    # =========================

    def _get_and_normalize_single(self, ticker, start_date, end_date, force_download):
        """
        Get and normalize data for a single ticker.
        
        Handles MultiIndex columns, date conversion, and filtering.
        
        Args:
            ticker (str): Ticker symbol
            start_date (datetime): Start date
            end_date (datetime): End date
            force_download (bool): Bypass cache
        
        Returns:
            pd.DataFrame: Normalized data with 'Date' and 'ticker' columns, or None
        """
        try:
            df = self._get_single_ticker(ticker, start_date, end_date, force_download)

            if df is None or df.empty:
                return None

            df = df.copy()

            # Flatten MultiIndex columns if present
            # yfinance sometimes returns MultiIndex with ticker in second level
            if isinstance(df.columns, pd.MultiIndex):
                ticker = df.columns.get_level_values(1)[0]
                df.columns = df.columns.get_level_values(0)
                df['ticker'] = ticker
                df = df.set_index('ticker', append=True)
                df = df.reorder_levels(['Date', 'ticker'])

            # Ensure Date is in index
            if 'Date' in df.columns:
                df = df.set_index('Date')

            # Convert index to datetime and drop invalid dates
            # Handle MultiIndex case (Date, ticker)
            if isinstance(df.index, pd.MultiIndex):
                dates = pd.to_datetime(df.index.get_level_values('Date'), errors='coerce')
                df.index = pd.MultiIndex.from_arrays(
                    [dates, df.index.get_level_values('ticker')],
                    names=['Date', 'ticker']
                )
                # Drop rows with invalid dates
                df = df.loc[df.index.get_level_values('Date').notna()]
            else:
                # Simple index case
                df.index = pd.to_datetime(df.index, errors='coerce')
                df = df.loc[df.index.notna()]

            # Filter to requested range
            if isinstance(df.index, pd.MultiIndex):
                idx = pd.IndexSlice
                df = df.loc[idx[start_date:end_date, :]]
            else:
                df = df.loc[start_date:end_date]

            # Convert back to columns for concat
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)

            df['Date'] = pd.to_datetime(df['Date'])
            df['ticker'] = ticker

            return df

        except Exception as e:
            warnings.warn(f"{ticker} failed: {e}")
            return None

    # =========================
    # CACHE HANDLING
    # =========================

    def _get_single_ticker(self, ticker, start_date, end_date, force_download):
        """
        Get data for a single ticker, using cache if available.
        
        Args:
            ticker (str): Ticker symbol
            start_date (datetime): Start date
            end_date (datetime): End date
            force_download (bool): Bypass cache
        
        Returns:
            pd.DataFrame: Price data for ticker, or None if invalid
        """
        cache_file = self.cache_dir / f"{ticker}.parquet"

        if not force_download and cache_file.exists():

            df = pd.read_parquet(cache_file)

            # Ensure index is Date
            if 'Date' in df.columns:
                df = df.set_index('Date')

            df.index = pd.to_datetime(df.index, errors='coerce')
            df = df.loc[df.index.notna()]

            cache_start = df.index.min()
            cache_end = df.index.max()

            parts = []

            # Download earlier data if needed
            if start_date < cache_start:
                early = self._download_ticker(ticker, start_date, cache_start - timedelta(days=1))
                if early is not None and not early.empty:
                    parts.append(early)

            parts.append(df)

            # Download later data if needed
            if end_date > cache_end:
                late = self._download_ticker(ticker, cache_end + timedelta(days=1), end_date)
                if late is not None and not late.empty:
                    parts.append(late)

            # Combine and clean
            df = pd.concat(parts).sort_index()
            df = df.loc[start_date:end_date]

        else:
            # Download fresh data
            df = self._download_ticker(ticker, start_date, end_date)

        # Remove duplicates and save
        if df is not None and not df.empty:
            df = df[~df.index.duplicated(keep='last')]
            
            # Validate if required
            if self.validate_on_load and not self._validate_data(df):
                warnings.warn(f"Data for {ticker} failed validation")
                return None
            
            df.to_parquet(cache_file)

        return df

    # =========================
    # DOWNLOAD
    # =========================

    def _download_ticker(self, ticker, start_date, end_date):
        """
        Download data from Yahoo Finance.
        
        Args:
            ticker (str): Ticker symbol
            start_date (datetime): Start date
            end_date (datetime): End date
        
        Returns:
            pd.DataFrame: Downloaded data, or None if download failed
        """
        try:
            # Add 7 day buffer to ensure we get the end date
            # (yfinance can be inconsistent with end date inclusion)
            end_buffered = end_date + timedelta(days=7)

            data = yf.download(
                ticker,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_buffered.strftime('%Y-%m-%d'),
                progress=False,
                auto_adjust=False
            )

            if data.empty:
                return None

            if not self._validate_data(data):
                return None

            return data

        except Exception as e:
            warnings.warn(f"Download failed {ticker}: {e}")
            return None

    # =========================
    # VALIDATION
    # =========================

    def _validate_data(self, df):
        """
        Validate data quality.
        
        Args:
            df (pd.DataFrame): Data to validate
        
        Returns:
            bool: True if data passes validation
        """
        if df is None or df.empty:
            return False

        required = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        if not all(c in df.columns for c in required):
            return False

        # Check for non-positive prices (allow 0 for some edge cases)
        price_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close']
        if (df[price_cols] < 0).any().any():
            return False

        # Check for negative volume (double .any() for DataFrame)
        if (df['Volume'] < 0).any().any():
            return False

        # Check that index is monotonic (sorted by date)
        if not df.index.is_monotonic_increasing:
            return False

        return True

    # =========================
    # CACHE TOOLS
    # =========================

    def clear_cache(self, ticker=None):
        """
        Clear cached data.
        
        Args:
            ticker (str, optional): If provided, clear only this ticker.
                                   If None, clear all cache.
        """
        if ticker:
            f = self.cache_dir / f"{ticker}.parquet"
            if f.exists():
                f.unlink()
                print(f"Cleared cache for {ticker}")
        else:
            for f in self.cache_dir.glob("*.parquet"):
                f.unlink()
            print("Cleared all cache")

    def get_cached_tickers(self):
        """
        Get list of tickers currently in cache.
        
        Returns:
            list: List of ticker symbols with cached data
        """
        return [f.stem for f in self.cache_dir.glob("*.parquet")]

    def get_cache_info(self):
        """
        Get information about cached data.
        
        Returns:
            pd.DataFrame: Info about each cached ticker (size, date range)
        """
        info = []

        for f in self.cache_dir.glob("*.parquet"):
            df = pd.read_parquet(f)

            if 'Date' in df.columns:
                df = df.set_index('Date')

            info.append({
                'ticker': f.stem,
                'rows': len(df),
                'start': df.index.min(),
                'end': df.index.max(),
                'size_mb': round(f.stat().st_size / 1024**2, 2)
            })

        return pd.DataFrame(info)
