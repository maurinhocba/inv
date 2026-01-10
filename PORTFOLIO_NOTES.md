# Portfolio Technical Notes

## Overview

The Portfolio class manages holdings, cash, and trading operations for backtesting. This document explains design decisions and areas marked for future review.

## CRITICAL: Commission Handling in Capital Allocation

### The Problem

When converting available capital to shares, you MUST account for buy commissions BEFORE calculating share quantities.

**Incorrect approach:**
```python
# ❌ WRONG - Will cause insufficient cash error
shares = cash / price
# When buying: cost = shares * price + commission → EXCEEDS cash!
```

**Correct approach:**
```python
# ✓ CORRECT - Accounts for commission first
value_for_shares = cash / (1 + commission_buy)
shares = value_for_shares / price
# Now: cost = shares * price + commission = cash (exactly)
```

### Example

With $10,000 cash and 0.1% commission:

```python
# WRONG WAY:
shares = 10000 / 100 = 100 shares
cost = 100 * 100 = 10000
commission = 10000 * 0.001 = 10
total = 10010  # ❌ Need $10 more!

# RIGHT WAY:
value_for_shares = 10000 / 1.001 = 9990.01
shares = 9990.01 / 100 = 99.90 shares
cost = 99.90 * 100 = 9990
commission = 9990 * 0.001 = 9.99
total = 9999.99  # ✓ Fits in $10,000!
```

### Implementation

Use the `convert_values_to_shares()` method:

```python
# In backtester, after calculating target allocation:
target_values = portfolio.calculate_target_holdings(
    selected_assets, 
    portfolio.total_value,
    allocation_method='equal'
)

# Convert to shares accounting for commissions
target_shares = portfolio.convert_values_to_shares(target_values, current_prices)

# Now rebalance
portfolio.rebalance(target_shares, current_prices, date)
```

### Where This Matters

1. **Backtester rebalancing**: Every holding period when recalculating positions
2. **Initial portfolio allocation**: First purchase at simulation start
3. **Any capital allocation calculation**: Anywhere you convert dollars to shares

### Safety Nets

The `buy()` method has a safety check (line 76):
```python
if total_cost > self.cash:
    warnings.warn("Insufficient cash... Buying maximum possible.")
    max_cost = self.cash / (1 + self.commission_buy)  # ✓ Correct
    shares = max_cost / price
```

But relying on this warning repeatedly indicates incorrect upstream calculation.

## Design Decisions

### 1. Cash Residual Handling

**Decision:** Allow small cash residuals (typically < $1)

**Rationale:**
- Mathematically impossible to invest 100% when buying fractional shares
- Attempting to distribute residual adds complexity for minimal benefit
- Real trading also has uninvested cash

**Implementation:**
```python
# After rebalancing, small cash remains
portfolio.cash  # e.g., $0.47
```

### 2. Rebalancing Strategy

**Decision:** Incremental approach (sell first, then buy)

**Current Implementation:**
1. Sell positions not in target or that need reduction
2. Buy new positions or increase existing ones

**Marked for review (line 202):**
```python
# TODO: Review rebalancing logic - current implementation is incremental.
# May need optimization for transaction costs or more sophisticated ordering.
```

**Why review later:**
- Current approach is simple and correct
- More sophisticated strategies exist:
  - Minimize number of trades
  - Optimize for tax implications
  - Consider bid-ask spreads
- Premature optimization without real backtesting data

**Alternative approaches to consider:**
- Simultaneous buy/sell to minimize cash idle time
- Order by transaction cost efficiency
- Smart order routing (sell highest commission first)

### 3. Insufficient Cash Handling

**Decision:** Warning + buy maximum possible

**Implementation:**
```python
if total_cost > self.cash:
    warnings.warn("Insufficient cash... Buying maximum possible.")
    max_shares = self.cash / (price * (1 + commission_rate))
    # Proceed with max_shares
```

**Marked for review (line 245):**
```python
# TODO: Review - should we warn here or handle silently?
```

**Why this approach:**
- Avoids crashing the backtest
- Provides visibility (warnings logged)
- Allows backtesting to complete

**Alternatives to consider:**
- Raise exception (strict mode)
- Scale down all positions proportionally
- Skip the buy entirely
- Borrow cash (margin simulation)

### 4. Fractional Shares

**Decision:** Allow fractional shares

**Rationale:**
- Simplifies capital allocation
- Many modern brokers support fractional shares
- More accurate backtesting

**Trade-off:**
- Not realistic for all brokers/time periods
- Future: add option for whole-shares-only mode

### 5. Commission Structure

**Decision:** Separate buy and sell commission rates

**Implementation:**
```python
Portfolio(initial_capital=100000, commission_buy=0.001, commission_sell=0.001)
```

**Rationale:**
- Some brokers have asymmetric commissions
- Flexibility for testing different scenarios
- Real-world accuracy

## Allocation Methods

### equal_weight

Distributes capital equally regardless of scores.

**Use case:** When all selected assets are considered equal

**Formula:**
```python
value_per_asset = total_value / n_assets
```

### score_proportional

Distributes capital proportionally to scores.

**Use case:** When asset quality differs (e.g., momentum, value scores)

**Formula:**
```python
asset_value = (asset_score / total_score) * total_value
```

**Edge case:** If total_score = 0, falls back to equal_weight

## Future Enhancements

### Short-term (before v1.0)

1. **Whole shares mode:**
   ```python
   Portfolio(..., allow_fractional=False)
   ```

2. **Rebalancing optimization:**
   - Transaction cost minimization
   - Smart order execution

3. **Better insufficient cash handling:**
   - Configurable strategies (exception, warning, silent)
   - Proportional scaling option

### Long-term

1. **Margin support:**
   ```python
   Portfolio(..., margin_rate=0.5)
   ```

2. **Tax-aware trading:**
   - Wash sale rules
   - Capital gains tracking
   - Lot selection (FIFO, LIFO, specific)

3. **More allocation methods:**
   - Volatility-weighted
   - Risk-parity
   - Mean-variance optimization
   - Kelly criterion

4. **Advanced order types:**
   - Limit orders
   - Stop-loss orders
   - Trailing stops

## Testing Coverage

All major features tested in `test_portfolio.py`:

- ✅ Initialization
- ✅ Buy operations
- ✅ Sell operations (full and partial)
- ✅ Value updates
- ✅ Allocation methods (equal, score-proportional)
- ✅ Rebalancing
- ✅ Trade history
- ✅ Edge cases (insufficient cash, invalid operations)

## Known Limitations

1. **No slippage modeling:** Assumes exact execution at specified price
2. **No market impact:** Assumes unlimited liquidity
3. **No bid-ask spread:** Uses single price for buy and sell
4. **Instant execution:** No time delay between orders
5. **Perfect divisibility:** Fractional shares always available

These are acceptable for initial backtesting but should be addressed for production use.

---

**Version:** 0.3.1  
**Date:** 2026-01-09  
**Status:** Production-ready with documented enhancement opportunities
