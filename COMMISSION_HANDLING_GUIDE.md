# Commission Handling Guide

## Critical Concept

When implementing the Backtester, **always account for commissions BEFORE calculating share quantities**.

This is not optional - failing to do this will cause the backtest to fail with "insufficient cash" errors.

## The Math

### Wrong Approach ❌

```python
# Given: $10,000 available, price = $100/share, commission = 0.1%

shares = available_cash / price
# shares = 10000 / 100 = 100

# When buying:
cost = shares * price = 100 * 100 = 10000
commission = cost * 0.001 = 10
total_needed = 10000 + 10 = 10010  # ❌ Need $10 more!
```

### Correct Approach ✓

```python
# Given: $10,000 available, price = $100/share, commission = 0.1%

# Account for commission FIRST
adjusted_value = available_cash / (1 + commission_rate)
# adjusted_value = 10000 / 1.001 = 9990.01

shares = adjusted_value / price
# shares = 9990.01 / 100 = 99.90

# When buying:
cost = shares * price = 99.90 * 100 = 9990
commission = cost * 0.001 = 9.99
total_needed = 9990 + 9.99 = 9999.99  # ✓ Fits in $10,000!
```

## Implementation in Code

### Step 1: Calculate Target Values

```python
# In backtester, after strategy selects assets
selected_assets = strategy_function(data, n=5, current_date=date)
# Returns: [('AAPL', 1.5), ('MSFT', 1.2), ...]

# Calculate how much $ to allocate to each
target_values = portfolio.calculate_target_holdings(
    selected_assets,
    portfolio.total_value,
    allocation_method='equal'
)
# Returns: {'AAPL': 50000, 'MSFT': 50000}
```

### Step 2: Convert to Shares (Accounting for Commissions)

```python
# Get current prices
current_prices = {
    'AAPL': data.loc[(current_date, 'AAPL'), 'Adj Close'],
    'MSFT': data.loc[(current_date, 'MSFT'), 'Adj Close']
}

# CRITICAL: Convert values to shares accounting for buy commission
target_shares = portfolio.convert_values_to_shares(
    target_values, 
    current_prices
)
# Returns: {'AAPL': 333.11, 'MSFT': 199.87}
# (Already adjusted for 0.1% commission)
```

### Step 3: Rebalance

```python
# Now rebalance - this will work without cash errors
portfolio.rebalance(target_shares, current_prices, date=current_date)
```

## Common Mistakes

### Mistake 1: Calculating shares directly from values

```python
# ❌ WRONG
target_shares = {
    ticker: value / current_prices[ticker]
    for ticker, value in target_values.items()
}
```

**Problem:** Doesn't account for commission, will cause insufficient cash.

**Fix:** Use `portfolio.convert_values_to_shares(target_values, prices)`

### Mistake 2: Adjusting commission incorrectly

```python
# ❌ WRONG
adjusted = available_cash * (1 - commission_rate)  # Subtraction!
shares = adjusted / price
```

**Problem:** Wrong formula. Commission is charged on the COST, not the available cash.

**Fix:** Divide by `(1 + commission_rate)`, not multiply by `(1 - commission_rate)`

### Mistake 3: Forgetting commission exists

```python
# ❌ WRONG
shares = total_value / n_assets / price
portfolio.buy(ticker, shares, price)  # Will fail!
```

**Problem:** Treats available cash as if commission doesn't exist.

**Fix:** Always use `convert_values_to_shares()` when going from $ to shares.

## Testing Your Implementation

Verify your backtester handles this correctly:

```python
# Setup
portfolio = Portfolio(initial_capital=10000, commission_buy=0.001)

# Calculate target
target_values = {'AAPL': 10000}
prices = {'AAPL': 100}

# Convert correctly
target_shares = portfolio.convert_values_to_shares(target_values, prices)

# Buy should succeed without warnings
portfolio.buy('AAPL', target_shares['AAPL'], prices['AAPL'])

# Verify
assert portfolio.cash >= 0, "Should not go negative"
assert portfolio.cash < 1, "Should use almost all cash"
```

If you see warnings like "Insufficient cash for AAPL", your allocation is not accounting for commission.

## Formula Reference

```
Given:
  C = available cash
  r = commission rate (e.g., 0.001 for 0.1%)
  p = price per share

Calculate shares:
  value_for_shares = C / (1 + r)
  shares = value_for_shares / p

Verify:
  cost = shares × p
  commission = cost × r
  total = cost + commission = C  (within rounding error)
```

## When to Use This

**Always use when:**
1. Implementing backtester rebalancing
2. Calculating initial portfolio allocation
3. ANY time you convert dollar amounts to share quantities

**Not needed when:**
1. Selling (commission comes out of proceeds, not upfront)
2. Updating portfolio value (just prices × shares)
3. Calculating returns (work backwards from actual trades)

## Quick Checklist

Before running a backtest, verify:

- [ ] Using `convert_values_to_shares()` for all $ → shares conversions
- [ ] Not calculating shares directly as `value / price`
- [ ] Test passes without "insufficient cash" warnings
- [ ] Cash residual is minimal (< $1 per rebalance)

---

**Version:** 0.3.1  
**Date:** 2026-01-09  
**Criticality:** HIGH - Failing to follow this will break backtesting
