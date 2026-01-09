# Bugfixes in v0.2.1

## Overview

Version 0.2.1 fixes several edge cases discovered during real-world testing with yfinance 1.0.x. These issues were not caught in initial testing because they depend on specific data patterns returned by Yahoo Finance.

## Issue 1: MultiIndex Columns from yfinance

### Problem
yfinance sometimes returns data with MultiIndex columns:

```python
# Structure returned:
         Price  Price  Price  ...
Ticker   AAPL   AAPL   AAPL   ...
         Open   High   Low    ...
```

Previous code assumed simple column index and would fail when trying to access columns by name.

### Solution (lines 133-141)
```python
if isinstance(df.columns, pd.MultiIndex):
    ticker = df.columns.get_level_values(1)[0]  # Extract ticker from level 1
    df.columns = df.columns.get_level_values(0)  # Flatten to level 0
    df['ticker'] = ticker
    df = df.set_index('ticker', append=True)
    df = df.reorder_levels(['Date', 'ticker'])
```

Now properly extracts ticker information and flattens the structure.

## Issue 2: Datetime Conversion with MultiIndex

### Problem
When trying to convert index to datetime after creating MultiIndex:

```python
df.index = pd.to_datetime(df.index, errors='coerce')  # ❌ Fails on MultiIndex
```

This would fail because you can't convert a MultiIndex directly to datetime.

### Solution (lines 148-161)
```python
if isinstance(df.index, pd.MultiIndex):
    # Convert only the Date level
    dates = pd.to_datetime(df.index.get_level_values('Date'), errors='coerce')
    # Rebuild MultiIndex with cleaned dates
    df.index = pd.MultiIndex.from_arrays(
        [dates, df.index.get_level_values('ticker')],
        names=['Date', 'ticker']
    )
    df = df.loc[df.index.get_level_values('Date').notna()]
else:
    # Simple index case
    df.index = pd.to_datetime(df.index, errors='coerce')
    df = df.loc[df.index.notna()]
```

Now handles both simple and MultiIndex cases correctly.

## Issue 3: Date Filtering on MultiIndex

### Problem
Standard date slicing doesn't work properly on MultiIndex:

```python
df = df.loc[start_date:end_date]  # ❌ Ambiguous on MultiIndex
```

### Solution (lines 164-168)
```python
if isinstance(df.index, pd.MultiIndex):
    idx = pd.IndexSlice
    df = df.loc[idx[start_date:end_date, :]]  # Explicit: all dates, all tickers
else:
    df = df.loc[start_date:end_date]
```

Uses `IndexSlice` for explicit MultiIndex filtering.

## Issue 4: Volume Validation

### Problem
Single `.any()` on a DataFrame column returns a Series, not a boolean:

```python
if (df['Volume'] < 0).any():  # ❌ Returns Series, not bool
    return False
```

### Solution (line 329)
```python
if (df['Volume'] < 0).any().any():  # ✅ First .any() reduces rows, second reduces to bool
    return False
```

Double `.any()` properly reduces to a single boolean value.

## Issue 5: dropna with Index

### Problem
`.dropna(subset=[df.index.name])` can be unreliable with certain index configurations.

### Solution (line 213)
```python
# Before:
df = df.dropna(subset=[df.index.name])

# After:
df = df.loc[df.index.notna()]
```

More direct and reliable approach.

## Issue 6: Download End Date Buffer

### Problem
yfinance inconsistently includes the end date. Buffer of 1 day was sometimes insufficient.

### Solution (line 284)
```python
# Increased from:
end_buffered = end_date + timedelta(days=1)

# To:
end_buffered = end_date + timedelta(days=7)
```

Larger buffer ensures end date is always included, excess data is filtered later.

## Testing

All fixes verified with:
- Multiple tickers (AAPL, MSFT, GOOGL)
- Various date ranges
- Cache updates
- Fresh downloads

## Impact

These fixes make DataManager robust to:
- Different yfinance return formats
- Edge cases in datetime handling
- Proper MultiIndex operations

No breaking changes to the public API.

---

**Version:** 0.2.1  
**Date:** 2026-01-09  
**Status:** All tests passing
