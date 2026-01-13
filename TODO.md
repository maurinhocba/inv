# TODO List

## Critical (Architectural)

### Portfolio Refactor: Values vs Shares
**Priority:** Medium  
**Complexity:** High  
**Impact:** High (simplifies code significantly)

**Problem:**
Current portfolio class mixes monetary values ($) and share quantities, causing complexity:
1. `calculate_target_holdings()` returns values ($)
2. `convert_values_to_shares()` converts to shares
3. `rebalance()` works with shares
4. But then needs values again for commission calculations
5. Workaround: `fraction_to_buy` logic to handle sell commission impact

**Proposed Solution:**
- All internal calculations work with monetary values ($)
- Only convert to shares at final trade execution (in `buy()` and `sell()`)
- Eliminates need for `convert_values_to_shares()`
- Simplifies commission handling dramatically
- Makes rebalancing logic much clearer

**Implementation Plan:**
1. Refactor `calculate_target_holdings()` to return $ values (already does)
2. Refactor `rebalance()` to work entirely in $ values
3. Calculate shares only when calling `buy()` or `sell()`
4. Remove or simplify `convert_values_to_shares()`
5. Update tests

**Files to Modify:**
- `portfolio.py`: Major refactor of `rebalance()` method
- `backtester.py`: Remove call to `convert_values_to_shares()`
- `test_portfolio.py`: Update tests
- `COMMISSION_HANDLING_GUIDE.md`: Update documentation

**Estimated Effort:** 4-6 hours

---

## High Priority

### Stop-Loss Implementation
**Priority:** High  
**Complexity:** Medium  
**Status:** Stubbed out (warnings in place)

**Requirements:**
- Different stop-loss strategies (fixed %, trailing %, time-based)
- Check stop-loss conditions during each iteration
- Execute sells when triggered
- Track stop-loss triggers in history

**Files to Create/Modify:**
- `trading_backtest/stoploss.py` (new)
- `backtester.py`: Uncomment and implement stop-loss logic
- `test_backtester.py`: Add stop-loss tests

---

## Medium Priority

### Additional Strategies
**Priority:** Medium  
**Complexity:** Low-Medium

**To Implement:**
- Mean reversion strategy
- Pure momentum strategy (not price/SMA ratio)
- Value-based strategy (P/E, P/B ratios) - requires fundamental data
- Combined/ensemble strategies

**Location:** `trading_backtest/strategies/`

---

### Parameter Optimization
**Priority:** Medium  
**Complexity:** Medium

**Features Needed:**
- Grid search over parameter space
- Walk-forward optimization
- Cross-validation for backtesting
- Overfitting detection

**Files to Create:**
- `trading_backtest/optimization.py`
- `examples/parameter_optimization.py`

---

### Visualization Tools
**Priority:** Medium  
**Complexity:** Low-Medium

**Charts to Implement:**
- Equity curve with benchmark comparison
- Drawdown chart
- Rolling Sharpe ratio
- Monthly returns heatmap
- Trade distribution analysis
- Parameter sensitivity heatmaps

**Files to Create:**
- `trading_backtest/visualization.py`
- `examples/plot_backtest_results.py`

---

## Low Priority

### Delisting Handling
**Priority:** Low  
**Complexity:** Medium  
**Current:** Documented limitation

**Implementation:**
- Detect when ticker stops having data
- Apply delisting rules (conservative: assume loss, or use last price)
- Document survivorship bias implications

---

### Advanced Allocation Methods
**Priority:** Low  
**Complexity:** Medium

**To Add:**
- Risk-parity allocation
- Volatility-weighted allocation
- Mean-variance optimization
- Kelly criterion sizing

---

### Slippage Modeling
**Priority:** Low  
**Complexity:** Low-Medium

**Features:**
- Fixed slippage (bps)
- Volume-based slippage
- Market impact model

---

### Bid-Ask Spread
**Priority:** Low  
**Complexity:** Low

**Implementation:**
- Buy at ask, sell at bid
- Configurable spread (bps or % of price)

---

## Documentation

### Additional Guides Needed
- Strategy writing best practices
- Common pitfalls and how to avoid them
- Performance interpretation guide
- When to trust backtest results

---

## Testing

### Additional Test Coverage
- Unit tests for metrics module
- Unit tests for individual portfolio methods
- Integration tests for data_manager + backtester
- Property-based tests for invariants

---

## Code Quality

### Improvements
- Add type hints throughout
- More comprehensive docstrings
- Code coverage measurement
- Linting with strict settings

---

**Last Updated:** 2026-01-09  
**Author:** Mauro S. Maza - mauromaza8@gmail.com
