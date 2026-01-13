# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-01-09

### Changed
- **Backtester**: Improved rebalancing logic
  - Now updates portfolio value BEFORE executing strategy
  - Separates price dictionaries for holdings vs target assets
  - Handles empty portfolio at start correctly
- **Portfolio**: Enhanced sell commission handling
  - Adjusts buy quantities to account for value lost in sell commissions
  - Added debug output for commission tracking (can be disabled)
  - Relaxed cash validation threshold to handle floating point errors

### Fixed
- Strategy renamed: `sma_ratio_strategy` → `price_to_sma_ratio` (more descriptive)
- Lookback period increased from 60 to 100 days in tests (appropriate for 50-day SMA)
- Cash validation now allows tiny negative values due to floating point rounding
- Insufficient cash warnings only shown when difference > $1 (not for rounding errors)

### Added
- Three new edge case tests in test_backtester.py:
  - Empty portfolio start (first rebalance)
  - No-sell rebalance (all assets maintained)
  - Complete turnover rebalance (sell all, buy all new)

### Documentation
- Updated BACKTESTER_GUIDE.md with proper lookback period calculation
- Updated README.md to clarify BACKTESTER_GUIDE includes strategy writing
- Author updated throughout: Mauro S. Maza - mauromaza8@gmail.com

### TODO (Documented for Future)
- **CRITICAL ARCHITECTURAL ISSUE**: Portfolio class mixes monetary values and share quantities
  - Current design: `calculate_target_holdings()` returns values ($), then converts to shares, 
    then `rebalance()` works with shares, but needs values again for commission calculations
  - Proposed refactor: Work entirely with monetary values throughout, only convert to shares 
    at final trade execution
  - This would significantly simplify commission handling and reduce complexity
  - Documented in portfolio.py TODO section

### Technical Notes
- Sell commission impact calculation uses 0.01 threshold (1 cent) to avoid floating point issues
- `fraction_to_buy` logic proportionally reduces all purchases when sell commissions reduce available cash
- Commission debug print can be commented out if output too verbose

## [0.4.0] - 2026-01-09

### Added
- **Backtester class**: Complete backtesting engine
  - Orchestrates DataManager, Portfolio, and Strategy
  - Automatic data loading with configurable lookback period
  - Main loop iterates through holding periods
  - Strategy execution at each rebalance point
  - Commission-adjusted capital allocation (uses `convert_values_to_shares`)
  - Portfolio rebalancing with incremental approach
  - Comprehensive history tracking
- **Metrics module**: Performance measurement
  - TIR (annualized IRR)
  - Total return
  - Sharpe ratio
  - Maximum drawdown
  - Annualized volatility
  - Number of rebalances
  - Utility functions: rolling Sharpe, drawdown series, strategy comparison
- **SMA Ratio Strategy**: First momentum strategy
  - Selects top N assets by price/SMA ratio
  - Configurable SMA window (default: 50 days)
  - Proper look-ahead bias prevention
  - Handles missing data gracefully
- **Test suite**: 5 comprehensive tests
  - Basic backtest
  - Different holding periods
  - Allocation methods comparison
  - Portfolio evolution verification
  - Commission impact analysis

### Changed
- Project status: Alpha → Beta
- Updated `__init__.py` to export Backtester, strategies, metrics

### Technical Implementation

**Holding Period Handling:**
- Uses calendar days (simpler than trading days)
- Skips dates without data automatically
- Uses most recent available date if exact date missing

**Data Flow:**
```
DataManager → Full historical data → Strategy (filters to current_date)
Strategy → Selected assets with scores → Portfolio allocation
Portfolio → Target values → convert_values_to_shares() → Rebalance
```

**Critical Features:**
- Always uses `convert_values_to_shares()` to prevent insufficient cash errors
- Strategy receives full DataFrame, responsible for avoiding look-ahead bias
- MultiIndex DataFrame format throughout (Date, ticker)

### TODO (Marked for future)
- Stop-loss implementation (currently stubbed out)
- More allocation methods (risk-parity, volatility-weighted)
- More strategies (mean reversion, value-based, etc.)
- Visualization tools
- Parameter optimization utilities

### Breaking Changes
None - all previous APIs remain compatible

## [0.3.1] - 2026-01-09

### Added
- **CRITICAL**: `convert_values_to_shares()` method in Portfolio
  - Correctly accounts for buy commissions when converting dollar amounts to shares
  - Prevents insufficient cash errors during rebalancing
  - Essential for backtester implementation

### Changed
- Updated PORTFOLIO_NOTES.md with critical section on commission handling
- Added test for commission-adjusted share calculation (test 10)

### Technical Details
**The Commission Problem:**
When allocating capital, you must account for commission BEFORE calculating shares:

```python
# WRONG - causes insufficient cash:
shares = cash / price  

# CORRECT - accounts for commission:
value_for_shares = cash / (1 + commission_buy)
shares = value_for_shares / price
```

Example: With $10,000 and 0.1% commission:
- Wrong way: tries to buy 100 shares → costs $10,010 (exceeds cash!)
- Right way: buys 99.90 shares → costs exactly $9,999.99 ✓

The new `convert_values_to_shares()` method handles this automatically.

## [0.3.0] - 2026-01-09

### Added
- **Portfolio class**: Complete portfolio management system
  - Buy and sell operations with commission tracking
  - Full sell (`sell()`) and partial sell (`sell_partial()`) methods
  - Portfolio value tracking and updates based on current prices
  - Holdings management with fractional shares support
  - Complete trade history with timestamps
- **Allocation methods**:
  - `equal_weight`: Distributes capital equally among selected assets
  - `score_proportional`: Allocates capital proportional to asset scores
- **Rebalancing logic**: Incremental approach (sell unwanted, buy needed)
- **Test suite**: Comprehensive tests for all portfolio operations (`test_portfolio.py`)

### Changed
- Project version bumped to 0.3.0
- Updated `__init__.py` to export Portfolio class

### Technical Details
- Commission rates configurable per portfolio (buy and sell can differ)
- Warnings when insufficient cash (buys maximum possible instead of failing)
- TODOs marked for future optimization:
  - Rebalancing logic review (line 202): Current incremental approach may need optimization
  - Validation strategy review (line 245): Warning vs exception handling
- Cash residual intentionally allowed (< $1 typically) per design decision

### Notes
Portfolio is production-ready but has documented areas for future enhancement:
1. Rebalancing order optimization for minimizing transaction costs
2. More sophisticated insufficient cash handling strategies
3. Advanced allocation methods (risk-based, volatility-weighted, etc.)

## [0.2.1] - 2026-01-09

### Fixed
- **MultiIndex column handling**: yfinance sometimes returns MultiIndex with ticker in second level - now properly extracted and flattened
- **Datetime conversion**: Handles both simple Index and MultiIndex cases correctly
- **Date filtering**: Uses `pd.IndexSlice` for proper filtering on MultiIndex DataFrames
- **Volume validation**: Now uses double `.any()` for correct DataFrame boolean reduction
- **Index cleaning**: Changed from `.dropna(subset=...)` to `.loc[index.notna()]` for better compatibility

### Changed
- Increased download buffer from 1 to 7 days (more reliable end date inclusion from yfinance)
- More robust normalization logic handles edge cases better

### Technical Details
When yfinance returns MultiIndex columns like:
```
         Price  Price  ...
Ticker   AAPL   AAPL   ...
         Open   Close  ...
```

Now extracts ticker from level 1, flattens to level 0, and restructures properly.

## [0.2.0] - 2026-01-09

### Changed
- **MAJOR REFACTOR**: Completely rewrote cache update logic for simplicity and robustness
- Simplified `_get_single_ticker` - no more complex merge operations
- New `_get_and_normalize_single` function separates concerns cleanly
- Better separation between download, cache, and normalization logic

### Fixed
- **CRITICAL**: Fixed "Reindexing only valid with uniquely valued Index objects" error
- Explicit duplicate removal: `df[~df.index.duplicated(keep='last')]`
- Fixed cache update overlap issues (now uses proper timedelta offsets)
- More defensive datetime conversions with `errors='coerce'`

### Added
- **NEW FEATURE**: Parallel downloads with `n_jobs` parameter (use with caution on Yahoo API)
- Improved validation: checks for monotonic index (proper date sorting)
- Validation now checks for negative prices and volumes

### Removed
- Eliminated `_update_cached_data` function (was source of complexity and bugs)
- Removed 7-day buffer (was causing unnecessary downloads)

### Technical Details
- Cache updates now download only missing ranges with proper boundary handling
- MultiIndex column flattening more robust
- Better error messages and warnings

## [0.1.2] - 2026-01-08

### Fixed
- **CRITICAL**: Corrected DataFrame structure to eliminate MultiIndex in columns
- DataFrame now has simple column index [Open, High, Low, Close, Volume, Adj Close]
- MultiIndex only in rows (Date, ticker) as intended
- Massive reduction in NaN values (50-70% memory savings)

### Changed
- Improved `get_data()` to flatten any MultiIndex columns from yfinance
- Added explicit column structure validation
- Enhanced test suite to verify DataFrame structure

### Performance
- Significantly reduced memory usage by eliminating unnecessary NaN values
- Faster operations without MultiIndex in columns

## [0.1.1] - 2026-01-08

### Fixed
- Compatibility with yfinance 1.0.x
- Added `auto_adjust=False` parameter to `yf.download()` to ensure Adj Close column is returned
- DataFrame structure now cleaner (removed duplicate columns in MultiIndex)

### Changed
- Cache update logic now downloads with 7-day buffer to avoid single-day requests
- Reduced unnecessary warnings for weekend/holiday dates
- Updated requirements.txt to specify yfinance version range

### Technical Details
- yfinance 1.0+ changed default `auto_adjust=True`, which removes Adj Close column
- For backtesting we need Adj Close (includes dividends), so we explicitly set `auto_adjust=False`
- Single-day downloads often fail for weekends/holidays, causing confusing warnings

## [0.1.0] - 2026-01-08

### Added
- Initial project structure
- DataManager class with:
  - Automatic data downloading from Yahoo Finance via yfinance
  - Parquet-based caching system
  - Data validation (NaN checks, price positivity, volume presence)
  - Cache management utilities
- Test suite for DataManager
- Project documentation (README.md)
- Development configuration (.gitignore, requirements.txt)

### Features
- Multi-ticker data download
- Efficient caching to avoid redundant API calls
- Automatic cache updates when requesting extended date ranges
- Data validation to ensure quality
- MultiIndex DataFrame output (Date, ticker)

---

## Upcoming

### [0.2.0] - Planned
- Portfolio class implementation
- Backtesting engine core
- Commission handling
- Basic rebalancing logic

### [0.3.0] - Planned
- First trading strategy (SMA ratio)
- Performance metrics (TIR, Sharpe, drawdown)
- Parameter sweep utilities

### [0.4.0] - Planned
- Stop-loss mechanisms
- Multiple capital allocation methods
- Visualization tools
