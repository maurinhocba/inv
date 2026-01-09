# Migration Notes: v0.1.x → v0.2.1

## Summary

Version 0.2.1 is a **bugfix release** over 0.2.0 that fixes critical edge cases discovered during real-world testing. **Highly recommended upgrade from any previous version.**

**v0.2.0** was a major refactor that fixed duplicate index errors and simplified codebase.  
**v0.2.1** fixes edge cases in MultiIndex handling, datetime conversion, and validation.

## Breaking Changes

**None** - The public API remains identical:

```python
# Still works exactly the same
dm = DataManager(cache_dir="data")
data = dm.get_data(['AAPL', 'MSFT'], '2020-01-01', '2023-12-31')
```

## New Features

### 1. Parallel Downloads

```python
# Download 10 tickers in parallel (4 threads)
data = dm.get_data(tickers, start, end, n_jobs=4)
```

**Warning:** Use with caution - Yahoo Finance may rate-limit aggressive parallel requests.

## Key Fixes

### 1. Duplicate Index Error (CRITICAL)

**Before (v0.1.x):**
```
pandas.errors.InvalidIndexError: Reindexing only valid with uniquely valued Index objects
```

**Now (v0.2.0):**
- Explicit duplicate removal in `_get_single_ticker`
- Proper overlap handling in cache updates
- Should never happen again

### 2. Cache Update Logic

**Before:**
- Complex `_update_cached_data` function
- 7-day buffer causing unnecessary downloads
- Potential for overlapping dates

**Now:**
- Simple parts-based approach
- Downloads only exact missing ranges
- Proper boundary handling with `timedelta(days=1)` offsets

### 3. Data Normalization

**Before:**
- Mixed responsibilities in `get_data`
- Inconsistent handling of MultiIndex columns

**Now:**
- Dedicated `_get_and_normalize_single` function
- Robust MultiIndex flattening
- Better error handling per ticker

## What to Test

After upgrading to v0.2.0, verify:

1. **Basic download works:**
   ```python
   dm = DataManager()
   data = dm.get_data(['AAPL'], '2023-01-01', '2023-12-31')
   print(data.head())
   ```

2. **Cache updates work:**
   ```python
   # First download
   data1 = dm.get_data(['AAPL'], '2020-01-01', '2022-12-31')
   
   # Extended range (should update cache)
   data2 = dm.get_data(['AAPL'], '2019-01-01', '2023-12-31')
   ```

3. **Structure is correct:**
   ```python
   data = dm.get_data(['AAPL', 'MSFT'], '2023-01-01', '2023-12-31')
   
   # Should print: ['Date', 'ticker']
   print(data.index.names)
   
   # Should print: Index(['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'])
   print(data.columns)
   
   # Should be < 5%
   print(f"NaN%: {(data.isna().sum().sum() / (len(data) * len(data.columns))) * 100:.2f}%")
   ```

## Recommended Actions

1. **Clear cache before testing:**
   ```bash
   rm -rf data/
   ```
   This ensures you're testing fresh downloads with new logic.

2. **Run test suite:**
   ```bash
   python examples/test_data_manager.py
   ```

3. **Monitor warnings:**
   - Should see fewer "possibly delisted" warnings
   - Download failures will still warn (expected for invalid tickers)

## Performance Notes

- **Memory:** No significant change (structure already optimized in v0.1.2)
- **Speed:** Slightly faster due to simpler logic
- **Parallel downloads:** Can be 2-4x faster with `n_jobs=4`, but use cautiously

## Rollback

If you encounter issues, you can rollback to v0.1.2 by reverting the `data_manager.py` file. Your cache files are compatible with both versions.

## Questions?

If you encounter issues with v0.2.0:

1. Check that you've updated `data_manager.py` 
2. Clear cache and retry
3. Report the specific error message
4. We can debug or rollback if needed

---

**Version:** 0.2.0  
**Date:** 2026-01-09
