# Trading Backtest Framework

A modular Python framework for backtesting algorithmic trading strategies based on historical price data.

## Features

- ✅ Efficient data caching with Parquet format
- ✅ Automatic data validation
- ✅ Flexible strategy implementation
- ✅ Multiple portfolio allocation methods (equal weight, score proportional)
- ✅ Commission tracking (separate buy/sell rates)
- ✅ Comprehensive performance metrics (TIR, Sharpe, drawdown, volatility)
- ✅ Full backtest history tracking
- ✅ Fractional shares support
- ✅ Look-ahead bias prevention
- 🚧 Stop-loss functionality (planned)
- 🚧 Parameter optimization tools (planned)
- 🚧 Visualization tools (planned)

## Project Status

**Version:** 0.4.1 (Beta)  
**Status:** Complete backtesting framework - production ready with documented improvement opportunities

### Changelog

**v0.4.1** (2026-01-09) - **REFINEMENTS & EDGE CASES**
- Improved backtester rebalancing: separates holdings/target price dicts, updates value before strategy
- Enhanced sell commission handling in portfolio (adjusts buys for commission losses)
- Strategy renamed to more descriptive `price_to_sma_ratio`
- Increased lookback period from 60 to 100 days (proper for 50-day SMA)
- Fixed cash validation for floating point rounding errors
- Added 3 new edge case tests (empty start, no-sell, complete turnover)
- Updated author: Mauro S. Maza
- **Documented TODO**: Refactor portfolio to work entirely with values (not mixed values/shares)

**v0.4.0** (2026-01-09) - **BACKTESTER COMPLETE** 🎉
- Implemented complete Backtester class
- Full integration of DataManager + Portfolio + Strategy
- Automatic data loading with lookback periods
- Rebalancing loop with holding periods (calendar days)
- Commission-adjusted capital allocation (critical fix applied)
- Comprehensive metrics calculation (TIR, Sharpe, drawdown, volatility)
- First strategy implemented: SMA Ratio
- Complete test suite with 5 test scenarios
- Stop-loss marked as TODO for future implementation
- Production-ready for backtesting momentum-based strategies

**v0.3.1** (2026-01-09) - **CRITICAL ADDITION**
- Added `convert_values_to_shares()` method to Portfolio
- Correctly accounts for buy commissions when calculating share quantities
- Prevents insufficient cash errors during backtesting
- Essential prerequisite for Backtester implementation
- Updated documentation with commission handling best practices
- Added test case verifying commission-adjusted calculations

**v0.3.0** (2026-01-09) - **PORTFOLIO IMPLEMENTATION**
- Implemented Portfolio class for managing holdings and trading
- Buy/sell operations with commission tracking
- Full and partial sell capabilities
- Portfolio value tracking and updates
- Two allocation methods: equal_weight and score_proportional
- Incremental rebalancing logic (sell then buy)
- Complete trade history tracking
- Edge case handling (insufficient cash warnings)
- Comprehensive test suite for all portfolio operations
- TODOs marked for future review (rebalancing optimization, validation strategies)

**v0.2.1** (2026-01-09) - **BUGFIX RELEASE**
- Fixed MultiIndex handling when yfinance returns columns with ticker in second level
- Improved datetime conversion to handle both simple and MultiIndex cases
- Added IndexSlice for proper filtering on MultiIndex DataFrames
- Increased download buffer from 1 to 7 days for more reliable end date inclusion
- Fixed volume validation to use double `.any()` for DataFrames
- Changed `.dropna(subset=...)` to `.loc[index.notna()]` for better compatibility
- All tests passing with real-world data

**v0.2.0** (2026-01-09) - **MAJOR REFACTOR**
- Complete rewrite of cache update logic (simpler, more robust)
- Fixed duplicate index errors permanently
- Eliminated unnecessary complexity in `_update_cached_data`
- New feature: parallel downloads with `n_jobs` parameter
- Improved validation (checks monotonic index, negative values)
- Better error handling throughout
- More defensive datetime conversions

**v0.1.2** (2026-01-08) - **CRITICAL FIX**
- Fixed DataFrame structure: eliminated MultiIndex in columns
- Now returns clean structure with simple columns: [Open, High, Low, Close, Volume, Adj Close]
- MultiIndex only in rows (Date, ticker) as intended
- 50-70% reduction in memory usage (eliminated unnecessary NaN values)
- Significantly improved performance

**v0.1.1** (2026-01-08)
- Fixed compatibility with yfinance 1.0.x
- Added `auto_adjust=False` to ensure Adj Close column is available
- Improved cache update logic to avoid single-day downloads (reduces warnings)
- Added 7-day buffer when updating cache

**v0.1.0** (2026-01-08)
- Initial DataManager implementation
- Parquet caching system
- Data validation
- Project structure

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd trading_backtest
```

### 2. Create virtual environment

```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Project Structure

```
trading_backtest/
├── data/                     # Cache directory (not in git)
├── examples/                 # Usage examples & tests
│   ├── test_data_manager.py
│   ├── test_portfolio.py
│   └── test_backtester.py
├── tests/                    # Unit tests (future)
└── trading_backtest/         # Main package
    ├── __init__.py
    ├── data_manager.py       # ✅ Data download & caching
    ├── portfolio.py          # ✅ Portfolio management  
    ├── backtester.py         # ✅ Backtesting engine
    ├── metrics.py            # ✅ Performance metrics
    ├── strategies/           # ✅ Trading strategies
    │   ├── __init__.py
    │   └── sma_ratio.py      # ✅ SMA ratio momentum
    └── utils.py              # 🚧 Helper functions (future)
```

## Quick Start

### Testing DataManager

```python
from trading_backtest.data_manager import DataManager

# Initialize
dm = DataManager(cache_dir="data")

# Download data (first time from yfinance, then cached)
data = dm.get_data(
    tickers=['AAPL', 'MSFT', 'GOOGL'],
    start_date='2020-01-01',
    end_date='2023-12-31'
)

# Check cache
print(dm.get_cache_info())
```

Run the test script:

```bash
python examples/test_data_manager.py
```

### Testing Portfolio

```python
from trading_backtest.portfolio import Portfolio

# Initialize portfolio with $100,000
portfolio = Portfolio(initial_capital=100000)

# Buy shares
portfolio.buy('AAPL', shares=100, price=150)
portfolio.buy('MSFT', shares=50, price=250)

# Update value with current prices
prices = {'AAPL': 160, 'MSFT': 260}
total_value = portfolio.update_value(prices)

print(f"Total portfolio value: ${total_value:,.2f}")
print(f"Holdings: {portfolio.holdings}")
print(f"Cash: ${portfolio.cash:,.2f}")

# View trade history
print(portfolio.get_trade_history())
```

Run the test script:

```bash
python examples/test_portfolio.py
```

## Roadmap

### Phase 1: Core Infrastructure ✅ COMPLETE
- [x] Data manager with caching
- [x] Data validation  
- [x] Project structure
- [x] Portfolio class with buy/sell operations
- [x] Commission tracking
- [x] Allocation methods (equal, score-proportional)
- [x] Backtester core engine
- [x] Metrics calculation (TIR, Sharpe, drawdown, volatility)
- [x] First strategy (SMA ratio)

### Phase 2: Additional Strategies 🚧
- [x] SMA ratio strategy
- [ ] Mean reversion strategy
- [ ] Momentum strategy
- [ ] Value-based strategy
- [ ] Combined strategies

### Phase 3: Advanced Features 📋
- [ ] Stop-loss mechanisms
- [ ] More allocation methods (risk-parity, volatility-weighted)
- [ ] Parameter optimization utilities
- [ ] Visualization tools (equity curves, drawdown charts)
- [ ] Delisting handling
- [ ] Benchmark comparison

### Phase 4: Production Features 📋
- [ ] Walk-forward analysis
- [ ] Monte Carlo simulation
- [ ] Transaction cost analysis
- [ ] Slippage modeling
- [ ] Real-time trading integration

## Development Guidelines

- All code in English
- Docstrings for all public methods
- Type hints where appropriate
- Keep modules focused and modular

## Documentation

- **[TODO.md](TODO.md)** - Planned features and improvements (including critical portfolio refactor)
- **[BACKTESTER_GUIDE.md](BACKTESTER_GUIDE.md)** - Complete guide to using the backtester and writing new strategy functions
- **[COMMISSION_HANDLING_GUIDE.md](COMMISSION_HANDLING_GUIDE.md)** - Critical guide for commission calculations
- **[PORTFOLIO_NOTES.md](PORTFOLIO_NOTES.md)** - Technical notes on portfolio design decisions
- **[CHANGELOG.md](CHANGELOG.md)** - Detailed version history
- **[BUGFIXES_v0.2.1.md](BUGFIXES_v0.2.1.md)** - DataManager bugfix documentation

## Known Limitations

- **Survivorship bias:** Currently works only with tickers still trading
- **Fractional shares:** Assumes ability to buy fractional shares (not realistic for all brokers)
- **Slippage:** Not yet implemented
- **Stop-loss:** Not yet implemented
- **Dividends:** Uses adjusted close prices (includes reinvested dividends)
- **Market impact:** Assumes unlimited liquidity
- **Bid-ask spread:** Uses single price for buy and sell

## License

[Your chosen license]

## Contact

[Your contact info]

---

**Last updated:** 2026-01-08
