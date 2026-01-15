
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
from trading_backtest.data_manager import DataManager

# ============================
# Data
# ============================
start_date='2025-01-02'
end_date='2025-12-31'

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

dm = DataManager(cache_dir=str(DATA_DIR))
dm.get_data(tickers, start_date, end_date, force_download=False, n_jobs=1)


