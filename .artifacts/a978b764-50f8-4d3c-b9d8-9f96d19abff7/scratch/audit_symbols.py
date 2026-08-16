import sys
import os
from yahooquery import Ticker
import pandas as pd
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

def audit():
    print(f"[*] Auditing {len(NIFTY_200_CONSTITUENTS)} symbols...")
    failures = []

    # Process in chunks to avoid overwhelming
    chunk_size = 20
    for i in range(0, len(NIFTY_200_CONSTITUENTS), chunk_size):
        chunk = NIFTY_200_CONSTITUENTS[i:i+chunk_size]
        symbols = [f"{s}.NS" for s in chunk]
        t = Ticker(symbols, asynchronous=True)
        hist = t.history(period='5d')

        for s in chunk:
            s_ns = f"{s}.NS"
            if s_ns not in hist.index or (isinstance(hist.index, pd.MultiIndex) and s_ns not in hist.index.get_level_values(0)):
                failures.append(s)

    print(f"\n[!] Audit Complete. Found {len(failures)} failures:")
    print(failures)

if __name__ == "__main__":
    audit()
