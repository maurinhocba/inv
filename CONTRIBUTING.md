# Contributing to Trading Backtest Framework

Thank you for your interest in contributing! This guide helps both human developers and AI assistants understand how to extend the framework properly.

## Table of Contents

1. [Writing New Strategies (Recommended)](#writing-new-strategies)
2. [When to Modify the Framework](#when-to-modify-the-framework)
3. [Guidelines for AI Assistants](#guidelines-for-ai-assistants)
4. [Code Style and Standards](#code-style-and-standards)
5. [Testing Requirements](#testing-requirements)
6. [Known Issues to Avoid](#known-issues-to-avoid)

---

## Writing New Strategies

**Most users should NOT need to modify the core framework.** The strategy system is designed to be extended without touching backtester, portfolio, or data manager code.

### Strategy Template

All strategies must follow this signature:

```python
def my_strategy(data, n, current_date, **kwargs):
    """
    Brief description of strategy.
    
    Args:
        data (DataFrame): MultiIndex DataFrame (Date, ticker) with FULL historical data
        n (int): Number of assets to select
        current_date (datetime): Current date - DO NOT use data after this date!
        **kwargs: Strategy-specific parameters
    
    Returns:
        list: [(ticker, score), ...] sorted by score descending
              Higher score = better asset
    
    Example:
        >>> selected = my_strategy(data, n=5, current_date=date, param1=value1)
        >>> # Returns: [('AAPL', 1.15), ('MSFT', 1.12), ...]
    """
    # 1. CRITICAL: Filter to avoid look-ahead bias
    historical_data = data.loc[:current_date]
    
    # 2. Get available tickers
    tickers = historical_data.index.get_level_values('ticker').unique()
    
    scores = []
    
    # 3. Calculate score for each ticker
    for ticker in tickers:
        try:
            # Extract ticker data
            ticker_data = historical_data.xs(ticker, level='ticker')
            
            # Your logic here - calculate some score
            score = calculate_your_metric(ticker_data, **kwargs)
            
            scores.append((ticker, score))
            
        except KeyError:
            # Ticker doesn't have data for current_date
            continue
        except Exception as e:
            # Handle other errors gracefully
            warnings.warn(f"Error processing {ticker}: {str(e)}")
            continue
    
    # 4. Sort and return top n
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:n]
```

### Critical Rules for Strategies

#### ✅ DO:
1. **Always filter data first:** `historical_data = data.loc[:current_date]`
2. **Handle missing data:** Use try/except for each ticker
3. **Return list of tuples:** `[(ticker, score), ...]`
4. **Higher score = better:** Sort descending
5. **Document parameters:** Clear docstring with examples
6. **Use warnings:** `warnings.warn()` for non-critical issues

#### ❌ DON'T:
1. **NEVER use data after current_date** (look-ahead bias)
2. **Don't store state between calls** (strategies should be stateless)
3. **Don't modify the input data** (read-only)
4. **Don't assume all tickers have data** (handle KeyError)
5. **Don't raise exceptions for individual ticker failures** (use try/except)
6. **Don't return more than n assets** (slice to [:n])

### Example: Mean Reversion Strategy

```python
def mean_reversion_strategy(data, n, current_date, window=20, **kwargs):
    """
    Select assets trading furthest below their moving average.
    
    Strategy assumes prices will revert to mean.
    """
    historical_data = data.loc[:current_date]
    tickers = historical_data.index.get_level_values('ticker').unique()
    
    scores = []
    
    for ticker in tickers:
        try:
            ticker_data = historical_data.xs(ticker, level='ticker')
            
            if len(ticker_data) < window:
                continue
            
            # Calculate how far below mean
            current_price = ticker_data.loc[current_date, 'Adj Close']
            mean_price = ticker_data['Adj Close'].rolling(window).mean().loc[current_date]
            
            if pd.notna(mean_price) and mean_price > 0:
                # Negative ratio = trading below mean (good for mean reversion)
                score = -(current_price / mean_price - 1)
                scores.append((ticker, score))
                
        except:
            continue
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:n]
```

### Testing Your Strategy

Create a test file in `examples/`:

```python
from trading_backtest import Backtester
from trading_backtest.strategies.my_strategy import my_strategy

backtester = Backtester()

results = backtester.run(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    initial_capital=100000,
    start_date='2023-01-01',
    end_date='2023-12-31',
    lookback_period=100,
    holding_period=30,
    n_assets=3,
    strategy_func=my_strategy,
    strategy_params={'param1': value1}
)

backtester.print_summary()
```

---

## When to Modify the Framework

**⚠️ STOP! Before modifying core code, ask yourself:**

1. Can this be done as a strategy function? (99% of cases: YES)
2. Can this be done with existing allocation methods?
3. Am I duplicating functionality that already exists?
4. Will this break backward compatibility?

### Valid Reasons to Modify Framework

#### ✅ New Allocation Method
**Where:** `portfolio.py` → add to `_allocation_methods`

```python
def _volatility_weighted(self, selected_assets, total_value):
    """Allocate inversely proportional to volatility."""
    # Implementation
    return {ticker: target_value for ticker, score in selected_assets}
```

**Then:** Add to `calculate_target_holdings()` elif chain

#### ✅ New Data Source
**Where:** `data_manager.py` → new method or new class

Example: Adding fundamental data (P/E ratios, earnings)

#### ✅ Stop-Loss Implementation
**Where:** Already planned in `backtester.py` (see TODO comments)

Check `TODO.md` before implementing - it may already be designed!

#### ✅ New Performance Metric
**Where:** `metrics.py` → new function

```python
def calculate_sortino_ratio(history_df, initial_capital, target_return=0):
    """Calculate Sortino ratio (downside deviation)."""
    # Implementation
    return sortino
```

### Invalid Reasons (Don't Modify)

#### ❌ "My strategy needs different data format"
**Solution:** Transform data inside your strategy function

#### ❌ "I want custom position sizing"
**Solution:** Use `score_proportional` allocation or create new allocation method

#### ❌ "I need to track extra information"
**Solution:** Return it in strategy metadata or add to history DataFrame

---

## Guidelines for AI Assistants

**If you're an AI (like Claude, ChatGPT, etc.) helping a user extend this framework, follow these rules:**

### Before Suggesting Framework Changes

Ask yourself (and the user) these questions:

1. **Can this be a strategy function?**
   - If yes → Provide strategy template, NOT framework modification
   - 95% of requests should be strategy functions

2. **Does this already exist?**
   - Check `TODO.md` for planned features
   - Check existing code for similar functionality
   - Don't reinvent the wheel

3. **Is this in a TODO section?**
   - If yes → Note that it's planned but not yet implemented
   - Suggest temporary workaround or wait for official implementation
   - If user insists, warn about potential conflicts with future updates

4. **Will this break existing code?**
   - Any change to public APIs is a breaking change
   - Require explicit user confirmation

### Known Issues to NEVER Replicate

⚠️ **These are documented problems - do NOT suggest code that makes them worse:**

1. **Mixing Values and Shares** (see TODO.md)
   - Current issue: Portfolio mixes $ values and share quantities
   - DON'T: Add more functions that do this
   - DO: Follow existing pattern until refactor happens

2. **Insufficient Cash Warnings**
   - Should be rare if using `convert_values_to_shares()` correctly
   - If user gets these: Check their allocation logic, don't add workarounds

3. **Look-Ahead Bias**
   - ALWAYS filter: `data.loc[:current_date]` in strategies
   - This is the #1 mistake in backtesting

### Code Style Rules

When generating code for this project:

1. **All code in English** (comments, docstrings, variable names)
2. **Docstrings required** for all public functions
3. **Type hints encouraged** but not mandatory
4. **Follow existing patterns:**
   - Strategy functions: Same signature as `price_to_sma_ratio`
   - Use `warnings.warn()` not `print()` for issues
   - Try/except for individual ticker failures

### Artifact Guidelines

When creating code artifacts:

1. **Use artifacts for:**
   - New strategy functions (always)
   - Framework modifications (if approved)
   - Test scripts

2. **Don't use artifacts for:**
   - Minor tweaks (just show the diff)
   - Configuration changes

3. **File naming:**
   - Strategies: `trading_backtest/strategies/strategy_name.py`
   - Tests: `examples/test_strategy_name.py`

### Response Pattern

When user asks to extend framework:

```
1. Clarify intent: "Are you trying to [X]?"

2. Suggest strategy approach first:
   "This can be done as a strategy function without modifying the framework.
   Here's how..."
   
3. Only if genuinely needed:
   "This does require framework modification because [reason].
   Before proceeding:
   - Have you checked TODO.md?
   - This will require testing
   - Consider backward compatibility
   
   Proceed? [wait for confirmation]"
```

---

## Code Style and Standards

### Python Style

- Follow PEP 8 (mostly)
- Line length: ~100 characters (flexible)
- Indentation: 4 spaces
- Variable naming:
  - Functions/methods: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Documentation

- All public functions need docstrings
- Use Google-style docstrings:

```python
def function(arg1, arg2):
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        arg1 (type): Description
        arg2 (type): Description
    
    Returns:
        type: Description
    
    Raises:
        ErrorType: When this happens
    
    Example:
        >>> function(1, 2)
        3
    """
```

### Imports

Order:
1. Standard library
2. Third-party (pandas, numpy, etc.)
3. Local imports (from .module import)

```python
import pandas as pd
import numpy as np
from datetime import datetime

from .data_manager import DataManager
```

---

## Testing Requirements

### For New Strategies

Minimum test:

```python
def test_my_strategy():
    """Test that strategy runs without errors."""
    backtester = Backtester()
    
    results = backtester.run(
        tickers=['AAPL', 'MSFT', 'GOOGL'],
        initial_capital=100000,
        start_date='2023-01-01',
        end_date='2023-06-30',
        lookback_period=100,
        holding_period=30,
        n_assets=3,
        strategy_func=my_strategy,
        strategy_params={'param': value}
    )
    
    # Basic sanity checks
    assert results['metrics']['final_value'] > 0
    assert len(results['history']) > 0
    
    print("✓ Strategy test passed")
```

### For Framework Modifications

Required:
1. Unit tests for new functions
2. Integration test with backtester
3. Verify all existing tests still pass
4. Update documentation

---

## Known Issues to Avoid

### From TODO.md

**CRITICAL - Portfolio Values/Shares Mixing:**
- Don't add more code that mixes $ values and share quantities
- If you must work with Portfolio internals, follow existing patterns
- Better: Wait for refactor (see TODO.md)

**Stop-Loss:**
- Don't implement your own - it's planned (see TODO.md)
- If you need it now, implement as external function

**Survivorship Bias:**
- Framework currently only works with tickers still trading
- Don't assume all historical tickers are available
- Document this limitation in your strategy

### Common Mistakes

1. **Using future data:**
   ```python
   # ❌ WRONG
   def bad_strategy(data, n, current_date):
       all_data = data  # Uses future data!
       
   # ✅ CORRECT
   def good_strategy(data, n, current_date):
       historical_data = data.loc[:current_date]
   ```

2. **Not handling missing data:**
   ```python
   # ❌ WRONG - will crash
   price = data.loc[(current_date, ticker), 'Adj Close']
   
   # ✅ CORRECT - handles errors
   try:
       price = data.loc[(current_date, ticker), 'Adj Close']
   except KeyError:
       continue
   ```

3. **Stateful strategies:**
   ```python
   # ❌ WRONG - state persists between calls
   last_prices = {}  # Module-level variable
   
   def bad_strategy(data, n, current_date):
       # Uses last_prices from previous call - BAD!
       
   # ✅ CORRECT - stateless
   def good_strategy(data, n, current_date):
       # Calculate everything from data parameter
   ```

---

## Questions?

- Check [TODO.md](TODO.md) for planned features
- Check [BACKTESTER_GUIDE.md](BACKTESTER_GUIDE.md) for usage examples
- Check existing strategies in `trading_backtest/strategies/`
- Open an issue on GitHub (if repository exists)
- Contact: Mauro S. Maza - mauromaza8@gmail.com

---

**Remember:** When in doubt, write a strategy function. Framework modifications should be rare and well-justified.

**Last Updated:** 2026-01-09  
**Author:** Mauro S. Maza - mauromaza8@gmail.com
