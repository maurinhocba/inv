
# ============================
# Paths
# ============================
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
RUN_DIR = Path(__file__).resolve().parent
REPORTS_DIR = RUN_DIR
PLOTS_DIR = RUN_DIR

print(f"Cache dir: {DATA_DIR}")
print(f"Results dir: {RUN_DIR}")

# ============================
# Other imports
# ============================
import pandas as pd
import matplotlib.pyplot as plt

from trading_backtest.backtester import Backtester
from trading_backtest.data_manager import DataManager
from trading_backtest.strategies import price_to_sma_ratio

# ============================
# Data manager
# ============================
dm = DataManager(cache_dir=str(DATA_DIR))

# ============================
# Backtest
# ============================
bt = Backtester(dm)

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 
           'NVDA', 'TSLA', 'JPM', 'V', 'WMT']
           
results = bt.run(
    tickers=tickers,
    initial_capital=10000,
    start_date='1990-01-01',
    end_date='2025-12-31',
    lookback_period=round(200*7/5*1.2),
    holding_period=90,
    n_assets=10,
    strategy_func=price_to_sma_ratio,
    strategy_params={'m': 200},
    allocation_method='equal',
    commission_buy=0.005,
    commission_sell=0.005
)

# ============================
# Show and save outputs
# ============================
metrics = results["metrics"]
df = pd.DataFrame.from_dict(metrics, orient="index", columns=["value"])
df.to_excel(RUN_DIR / "metrics.xlsx")
print(f'TIR (Annualized Return): {metrics['tir']*100:6.2f}%')

history = results["history"]
holdings_df = history["holdings"].apply(pd.Series)
holdings_df = holdings_df.fillna(0)
history_expanded = pd.concat([history.drop(columns=["holdings"]), holdings_df], axis=1)
history_expanded.to_excel(RUN_DIR / "history.xlsx", index=False)
x = history["date"]
y = history["portfolio_value"]
plt.figure(figsize=(8,6))
plt.plot(x, y)
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.title("Equity Curve")
plt.tight_layout()
plt.savefig("equity.png", dpi=300)
plt.show()


print("Run completed")
