"""
Price to SMA Ratio Strategy

Selects assets with highest ratio of current price to Simple Moving Average.

Author: Mauro S. Maza - mauromaza8@gmail.com
Version: 0.1.0
Date: 2026-01-09
"""

import pandas as pd
import warnings


def price_to_sma_ratio(data, n, current_date, m=50, **kwargs):
    """
    Select top n assets with highest price/SMA ratio.
    
    Strategy logic:
    - Calculate m-day Simple Moving Average for each ticker
    - Calculate ratio: current_price / SMA
    - Select top n tickers with highest ratio
    
    Args:
        data (DataFrame): MultiIndex DataFrame (Date, ticker) with price data
                         Full historical data is provided
        n (int): Number of assets to select
        current_date (datetime): Current date for strategy execution
                                DO NOT use data after this date (look-ahead bias)
        m (int): SMA window size in days (default: 50)
        **kwargs: Additional parameters (for future extensions)
    
    Returns:
        list: [(ticker, score), ...] sorted by score descending
              score = current_price / SMA
    
    Example:
        >>> selected = price_to_sma_ratio(data, n=5, current_date=date, m=50)
        >>> # Returns: [('AAPL', 1.15), ('MSFT', 1.12), ...]
    """
    # Filter data up to current_date (avoid look-ahead bias)
    historical_data = data.loc[:current_date]
    
    # Get list of available tickers
    tickers = historical_data.index.get_level_values('ticker').unique()
    
    scores = []
    
    for ticker in tickers:
        try:
            # Extract data for this ticker
            ticker_data = historical_data.xs(ticker, level='ticker')
            
            # Need at least m days of data
            if len(ticker_data) < m:
                continue
            
            # Calculate SMA
            sma = ticker_data['Adj Close'].rolling(window=m).mean()
            
            # Get current price and SMA value
            current_price = ticker_data.loc[current_date, 'Adj Close']
            current_sma = sma.loc[current_date]
            
            # Calculate ratio (score)
            if pd.notna(current_sma) and current_sma > 0:
                ratio = current_price / current_sma
                scores.append((ticker, ratio))
            
        except KeyError:
            # Ticker doesn't have data for current_date
            continue
        except Exception as e:
            warnings.warn(f"Error processing {ticker}: {str(e)}")
            continue
    
    # Sort by score (descending) and take top n
    scores.sort(key=lambda x: x[1], reverse=True)
    
    return scores[:n]
