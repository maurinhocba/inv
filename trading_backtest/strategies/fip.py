"""
FIP (Frog in the Pan) Strategy

Selects assets that have risen gradually with many positive days,
avoiding assets with volatile price movements.

Author: Mauro S. Maza - mauromaza8@gmail.com
Version: 0.1.0
Date: 2026-01-15
"""

import pandas as pd
import numpy as np
import warnings


def fip(data, n, current_date, lookback_start=365, lookback_end=30, only_sign=True, **kwargs):
    """
    Select top n assets using Frog in the Pan (FIP) strategy.
    
    Strategy logic:
    - Analyze price movement from lookback_start to lookback_end days ago
    - Count positive days (n_pos) and negative days (n_neg)
    - Calculate overall return for the period
    - Favor assets with positive return AND more positive days than negative days
    - This identifies "gradual risers" vs "volatile jumpers"
    
    Args:
        data (DataFrame): MultiIndex DataFrame (Date, ticker) with price data
                         Full historical data is provided
        n (int): Number of assets to select
        current_date (datetime): Current date for strategy execution
                                DO NOT use data after this date (look-ahead bias)
        lookback_start (int): Days back to start analysis (default: 365 = 1 year)
        lookback_end (int): Days back to end analysis (default: 30 = 1 month)
                           Must be < lookback_start (calendar days)
        only_sign (bool): If True, use sign(return) in score calculation (default)
                         If False, use actual return value (amplifies effect)
        **kwargs: Additional parameters (for future extensions)
    
    Returns:
        list: [(ticker, score), ...] sorted by score descending
              score = sign(return) * (n_pos - n_neg) / total_days  if only_sign=True
              score = return * (n_pos - n_neg) / total_days        if only_sign=False
    
    Example:
        >>> # FIP from 1 year ago to 1 month ago
        >>> selected = fip(data, n=5, current_date=date, 
        ...                lookback_start=365, lookback_end=30, only_sign=True)
        >>> # Returns: [('AAPL', 0.65), ('MSFT', 0.58), ...]
    """
    if lookback_end >= lookback_start:
        raise ValueError(f"lookback_end ({lookback_end}) must be < lookback_start ({lookback_start})")
    
    # Filter data up to current_date (avoid look-ahead bias)
    historical_data = data.loc[:current_date]
    
    # Get list of available tickers
    tickers = historical_data.index.get_level_values('ticker').unique()
    
    scores = []
    
    for ticker in tickers:
        try:
            # Extract data for this ticker
            ticker_data = historical_data.xs(ticker, level='ticker')
            
            # Need at least lookback_start days of data
            if len(ticker_data) < lookback_start:
                continue
            
            # Get the slice from lookback_start to lookback_end days ago
            start_idx = -lookback_start
            end_idx = -lookback_end if lookback_end > 0 else None
            
            period_data = ticker_data.iloc[start_idx:end_idx]
            
            if len(period_data) < 2:
                continue
            
            # Calculate daily price changes
            daily_changes = period_data['Adj Close'].pct_change().dropna()
            
            if len(daily_changes) == 0:
                continue
            
            # Count positive and negative days
            n_pos = (daily_changes > 0).sum()
            n_neg = (daily_changes < 0).sum()
            
            # Calculate overall return for the period
            price_start = period_data.iloc[0]['Adj Close']
            price_end = period_data.iloc[-1]['Adj Close']
            
            if pd.notna(price_start) and pd.notna(price_end) and price_start > 0:
                period_return = (price_end / price_start) - 1
                
                # Calculate total days in analysis
                total_days = lookback_start - lookback_end
                
                # Calculate score
                if only_sign:
                    score = np.sign(period_return) * (n_pos - n_neg) / total_days
                else:
                    score = period_return * (n_pos - n_neg) / total_days
                
                scores.append((ticker, score))
            
        except (KeyError, IndexError):
            # Ticker doesn't have sufficient data
            continue
        except Exception as e:
            warnings.warn(f"Error processing {ticker}: {str(e)}")
            continue
    
    # Sort by score (descending) and take top n
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return scores[:n]
