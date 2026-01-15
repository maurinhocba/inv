# Backtester Quick Start Guide

## Overview

The Backtester is the main engine that simulates trading strategies over historical data. It integrates DataManager (data loading), Portfolio (holdings management), and Strategy (asset selection).

## Basic Usage

### Minimal Example

```python
from trading_backtest import Backtester
from trading_backtest.strategies import price_to_sma_ratio

# Create backtester
backtester = Backtester()

# Run backtest
results = backtester.run(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    initial_capital=100000,
    start_date='2023-01-01',
    end_date='2023-12-31',
    lookback_period=60,
    holding_period=30,
    n_assets=2,
    strategy_func=price_to_sma_ratio,
    strategy_params={'m': 50}
)

# View results
backtester.print_summary()
```

## Parameters Explained

### Required Parameters

- **`tickers`** (list): Universe of stocks to choose from
  - Example: `['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']`
  - Larger universe = more selection options, but slower downloads

- **`initial_capital`** (float): Starting money
  - Example: `100000` for $100,000

- **`start_date`** (str/datetime): When simulation begins
  - Example: `'2022-01-01'`
  - Strategy makes first selection on this date

- **`end_date`** (str/datetime): When simulation ends
  - Example: `'2023-12-31'`
  
- **`lookback_period`** (int): Days of data before start_date
  - Example: `100` for 100 days
  - Strategy needs this to calculate indicators (e.g., 50-day SMA needs at least 50 trading days)
  - Rule of thumb: For an M-day SMA, use lookback_period ≥ M * (7/5) * 1.2
    - 50-day SMA: 50 * 1.4 = 70 days minimum, recommend 100 days for safety
  - Data downloaded from: `start_date - lookback_period` to `end_date`

- **`holding_period`** (int): Days between rebalances
  - Example: `30` for monthly rebalancing
  - Calendar days, not trading days
  - Smaller = more frequent trading = higher commissions

- **`n_assets`** (int): Portfolio size (how many stocks to hold)
  - Example: `5` to hold 5 stocks at a time
  - Must be ≤ len(tickers)

- **`strategy_func`** (callable): Function that selects assets
  - Example: `sma_ratio_strategy`
  - Must have signature: `strategy_func(data, n, current_date, **params)`
  - Returns: `[(ticker, score), ...]`

### Optional Parameters

- **`strategy_params`** (dict): Parameters for strategy
  - Example: `{'m': 50}` for 50-day SMA
  - Default: `{}`

- **`allocation_method`** (str): How to divide capital
  - Options: `'equal'` or `'score_proportional'`
  - Default: `'equal'`
  - `'equal'`: Each asset gets same dollar amount
  - `'score_proportional'`: Higher scored assets get more money

- **`commission_buy`** (float): Commission on buys
  - Example: `0.001` for 0.1%
  - Default: `0.001`

- **`commission_sell`** (float): Commission on sells
  - Example: `0.001` for 0.1%
  - Default: `0.001`

- **`stoploss_func`** (callable): Stop-loss function
  - Currently not implemented (TODO)
  - Default: `None`

## Understanding Results

### Results Dictionary

```python
results = {
    'metrics': {
        'final_value': 125000.00,
        'total_return': 0.25,      # 25% total return
        'tir': 0.23,               # 23% annualized return
        'sharpe': 1.45,            # Sharpe ratio
        'max_drawdown': -0.12,     # -12% worst drawdown
        'volatility': 0.16,        # 16% annualized volatility
        'num_rebalances': 24       # Number of rebalances
    },
    'history': DataFrame(...),      # Full history
    'final_portfolio': Portfolio(...),  # Final state
    'parameters': {...}             # All input parameters
}
```

### Key Metrics

**Total Return**: (Final - Initial) / Initial
- Example: 0.25 = 25% gain over entire period

**TIR (Annualized Return)**: Compound annual growth rate
- Example: 0.23 = 23% per year
- More useful than total return for comparing different time periods

**Sharpe Ratio**: Return / Volatility
- Measures risk-adjusted return
- Higher is better (> 1 is good, > 2 is excellent)
- Assumes risk-free rate = 0

**Max Drawdown**: Worst peak-to-trough decline
- Example: -0.12 = portfolio fell 12% from peak
- Shows worst case scenario

**Volatility**: Standard deviation of returns (annualized)
- Example: 0.16 = 16% per year
- Measures how much portfolio value fluctuates

### History DataFrame

```python
history = results['history']

# Columns:
# - date: Rebalance date
# - portfolio_value: Total value (cash + holdings)
# - cash: Uninvested cash
# - num_positions: Number of stocks held
# - holdings: Dict of {ticker: shares}
# - selected_tickers: List of tickers chosen

# Examples:
history['portfolio_value'].plot()  # Equity curve
history['cash'].mean()             # Average cash level
history['num_positions'].value_counts()  # Position count distribution
```

## Common Patterns

### Comparing Holding Periods

```python
results_list = []

for hp in [15, 30, 60]:
    results = backtester.run(
        ...,
        holding_period=hp,
        ...
    )
    results_list.append(results)
    print(f"{hp} days: TIR={results['metrics']['tir']:.2%}")
```

### Comparing Strategies

```python
from trading_backtest.strategies import price_to_sma_ratio
# from trading_backtest.strategies import momentum_strategy  # Future

strategies = [
    ('Price/SMA Ratio', price_to_sma_ratio, {'m': 50}),
    # ('Momentum', momentum_strategy, {'period': 90}),
]

for name, func, params in strategies:
    results = backtester.run(
        ...,
        strategy_func=func,
        strategy_params=params,
        ...
    )
    print(f"{name}: TIR={results['metrics']['tir']:.2%}")
```

### Parameter Sweep (Manual)

```python
import pandas as pd

sweep_results = []

for hp in [15, 30, 60]:
    for n in [3, 5, 10]:
        results = backtester.run(
            ...,
            holding_period=hp,
            n_assets=n,
            ...
        )
        sweep_results.append({
            'holding_period': hp,
            'n_assets': n,
            'tir': results['metrics']['tir'],
            'sharpe': results['metrics']['sharpe']
        })

df = pd.DataFrame(sweep_results)
df.pivot(index='holding_period', columns='n_assets', values='tir')
```

## Writing Your Own Strategy

### Template

```python
def my_strategy(data, n, current_date, **params):
    """
    Your strategy description.
    
    Args:
        data: MultiIndex DataFrame (Date, ticker) with full history
        n: Number of assets to select
        current_date: Current date (don't use data after this!)
        **params: Your custom parameters
    
    Returns:
        list: [(ticker, score), ...] sorted by score descending
    """
    # 1. Filter data to avoid look-ahead bias
    historical = data.loc[:current_date]
    
    # 2. Get available tickers
    tickers = historical.index.get_level_values('ticker').unique()
    
    scores = []
    
    # 3. Calculate score for each ticker
    for ticker in tickers:
        try:
            ticker_data = historical.xs(ticker, level='ticker')
            
            # Your logic here
            score = calculate_your_score(ticker_data, **params)
            
            scores.append((ticker, score))
        except:
            continue
    
    # 4. Sort and return top n
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:n]
```

### Important Rules

1. **Never use data after current_date** (look-ahead bias)
2. **Always filter: `data.loc[:current_date]`**
3. **Handle missing data gracefully** (try/except)
4. **Return exactly n assets** (or fewer if not enough valid)
5. **Score can be any float** (higher = better)

## Troubleshooting

### "No data available for date"
- Check that tickers exist during your date range
- Some tickers may have started trading after your start_date
- Use `lookback_period` ≥ indicator window (e.g., 60 for 50-day SMA)

### "Insufficient cash" warnings
- Shouldn't happen if using `convert_values_to_shares()` correctly
- If you see this, report it - likely a bug

### Slow performance
- Reduce number of tickers (fewer downloads)
- Reduce date range
- Increase holding_period (fewer rebalances)
- Data is cached, so second run should be much faster

### Low/negative returns
- Check commission rates (too high?)
- Check if strategy makes sense
- Compare to buy-and-hold benchmark
- Market may have been down during period

## Best Practices

1. **Always start with a short test period** (e.g., 6 months)
2. **Use realistic commissions** (0.1% = 0.001 is typical)
3. **Cache is your friend** - data downloads are slow
4. **Check history DataFrame** - verify strategy is working as expected
5. **Compare to benchmark** - is your strategy beating buy-and-hold?
6. **Test different time periods** - does it work in different market conditions?

---

**Version:** 0.4.0  
**Date:** 2026-01-09
