
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
import seaborn as sns
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

tickers = [ "AAL", "AAPL", "ABBV", "ABEV", "ABNB", "ABT", # "ACH",
            "ADBE", "ADI", "AEM", "AGRO", # "AKO.B", 
            "AMAT", "AMD", "AMGN", "AMX", "AMZN", "ARCO", # "AUY", 
            "AVGO", "AXP", "AZN", "BA", "BABA", "BAC", "BB", "BBAR", "BBD", 
            "BBVA", "BCS", "BG", "BHP", "BIDU", "BIIB", "BIOX", "BITF", "BMA", #,"BRK.A"
            "BMY", "BP", "BRFS", "BSBR", "C", "CAAP", "CAH", "CAT", "CDE", 
            "CEPU", "CL",  "COST", "CRESY", "CRM", "CSCO", "CVX", "CX", # "CS", 
            "DD", "DE", "DESP", "DIS", "DOCU", "EA", "EBAY", "EBR", "DOW", ####"DIA",
            "EDN", "EFX", "ERIC", "ERJ", "ETSY",  "F", "FCX", "FDX",### "EEM", "EWZ",
            "FMX", "FSLR", "GE", "GFI", "GGAL", "GGB", "GILD", "GLOB", "GLW", "GM", 
            "GOLD", "GOOGL", "GPRK", "GRMN", "GS", "GSK", "HAL", "HD", "HL", "HMC", 
            "HMY", "HOG", "HON", "HPQ", "HSBC", "HSY", "HUT", "HWM", "IBM", "INTC", 
            "IP", "IRS", "ITUB",  "JD", "JMIA", "JNJ", "JPM", "KMB", "KO", ##"IWM",
            "LLY", "LMT", "LOMA", "LRCX", "LVS", "LYG", "MA", "MCD", "MDT", "MELI", 
            "META", "MMC", "MMM", "MO", "MOS", "MRK", "MSFT", "MSI", "MSTR", "MU", 
            "NEM", "NFLX", "NGG", "NIO", "NKE", "NOK", "NTES", "NUE", "NVDA", ##"NTCO"
            "NVS","ORCL", "OXY", "PAAS", "PAM", "PANW", "PBI",#, "ORAN"# "OGZPY"
            "PBR", "PCAR", "PEP", "PFE", "PG", "PHG", "PKX", "PSX",  "PYPL", ##"PTRCY",
            "QCOM", "RBLX", "RIO", "RTX", "SAN", "SAP", "SATL", "SBS", "SBUX", #"QQQ",
            "SCCO", "SE", "SHEL", "SHOP", "SID", "SLB", "SNA", "SNAP", "SNOW", #, "SI"
            "SONY", "SPGI", "SPOT",  "SQ", "SUPV", "SUZ", "T", "TEF", "TEO", #"SPY",
            "TGS", "TGT", "TMO", "TRIP", "TS", "TSLA", "TSM", "TTE", "TV", "TWLO", 
            "TX", "TXN", "UAL", "UBER", "UGP", "UL", "UNH", "UNP", "UPST", #"TWTR",
            "V", "VALE", "VIST", "VIV", "VOD", "VRSN", "VZ", "WBA", "WFC", "WMT", 
            "X","XOM", "XP", "XRX", "YELP", "YPF", "ZM", # "XLE", "XLF"
]

# tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 
           # 'NVDA', 'TSLA', 'JPM', 'V', 'WMT']

print(f"\nRunning backtest with {len(tickers)} tickers...")

sweep_results = []

for hp in [15, 30, 60, 90, 120]:
    for n in [5, 10, 20, 40]:
        results = bt.run(
            tickers=tickers,
            initial_capital=10000,
            start_date='1990-01-01',
            end_date='2025-12-31',
            lookback_period=round(200*7/5*1.2),
            holding_period=hp,
            n_assets=n,
            strategy_func=price_to_sma_ratio,
            strategy_params={'m': 200},
            allocation_method='equal',
            commission_buy=0.005,
            commission_sell=0.005
        )
        sweep_results.append({
            'holding_period': hp,
            'n_assets': n,
            'tir': results['metrics']['tir'],
            'sharpe': results['metrics']['sharpe']
        })
        print(f"holding period: {hp:4d}; n portfolio: {n:3d}; TIR={results['metrics']['tir']:6.2%}")

df = pd.DataFrame(sweep_results)
pivot = df.pivot(index='holding_period', columns='n_assets', values='tir')

# ============================
# Show and save outputs
# ============================
df.to_parquet("sweep_results.parquet") # READ: sweep_results = pd.read_parquet("sweep_results.parquet")
df.to_excel("sweep_results.xlsx", index=False)

# figure
plt.figure(figsize=(8,6))
sns.heatmap(pivot, annot=True, fmt=".2%", cmap="viridis")
plt.title("TIR Heatmap")
plt.xlabel("Number of Assets")
plt.ylabel("Holding Period")
plt.tight_layout()
plt.savefig("tir_heatmap.png", dpi=300)
plt.show()

print("Run completed")
