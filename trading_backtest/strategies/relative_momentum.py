"""
Relative Momentum Strategy

Selects assets with highest momentum calculated over a specific lookback window,
with the ability to exclude recent days.

Author: Mauro S. Maza - mauromaza8@gmail.com
Version: 0.1.0
Date: 2026-01-15
"""

import pandas as pd
import warnings


def relative_momentum(data, n, current_date, lookback_start=365, lookback_end=30, **kwargs):
    """
    Select top n assets with highest relative momentum.
    
    Strategy logic:
    - Calculate return from lookback_start days ago to lookback_end days ago
    - This excludes the most recent lookback_end days (useful to avoid short-term reversals)
    - Select top n tickers with highest momentum score
    
    Args:
        data (DataFrame): MultiIndex DataFrame (Date, ticker) with price data
                         Full historical data is provided
        n (int): Number of assets to select
        current_date (datetime): Current date for strategy execution
                                DO NOT use data after this date (look-ahead bias)
        lookback_start (int): Days back to start the momentum calculation (default: 365 = 1 year)
        lookback_end (int): Days back to end the momentum calculation (default: 30 = 1 month)
                           Must be < lookback_start (calendar days)
        **kwargs: Additional parameters (for future extensions)
    
    Returns:
        list: [(ticker, score), ...] sorted by score descending
              score = price_lookback_end / price_lookback_start - 1
    
    Example:
        >>> # Momentum from 1 year ago to 1 month ago (excludes last month)
        >>> selected = relative_momentum(data, n=5, current_date=date, 
        ...                              lookback_start=365, lookback_end=30)
        >>> # Returns: [('AAPL', 0.45), ('MSFT', 0.38), ...]
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
            
            # Get the date lookback_start days ago
            dates = ticker_data.index
            if len(dates) < lookback_start:
                continue
            
            start_idx = -lookback_start
            end_idx = -lookback_end if lookback_end > 0 else None
            
            # Get prices at the two points
            price_start = ticker_data.iloc[start_idx]['Adj Close']
            price_end = ticker_data.iloc[end_idx]['Adj Close']
            
            # Calculate momentum (return)
            if pd.notna(price_start) and pd.notna(price_end) and price_start > 0:
                momentum = (price_end / price_start) - 1
                scores.append((ticker, momentum))
            
        except (KeyError, IndexError):
            # Ticker doesn't have sufficient data
            continue
        except Exception as e:
            warnings.warn(f"Error processing {ticker}: {str(e)}")
            continue
    
    # Sort by score (descending) and take top n
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return scores[:n]
