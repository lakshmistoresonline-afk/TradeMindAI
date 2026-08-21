import yfinance as yf
import pandas as pd

symbols = ["PEL.NS", "TATAMOTORS.NS", "ZOMATO.NS", "LTIM.NS", "GUJGASLTD.NS"]
for s in symbols:
    print(f"Fetching {s}...")
    df = yf.download(s, period="1mo", progress=False)
    print(f"   Rows: {len(df)}")
    if not df.empty:
        print(f"   Last: {df.index[-1]}")
