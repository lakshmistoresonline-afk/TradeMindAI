import yfinance as yf
import pandas as pd

symbols = ["RELIANCE.NS", "TCS.NS", "ZOMATO.NS", "LTIM.NS", "PEL.NS", "TATAMOTORS.NS", "HDFCBANK.NS", "INFY.NS"]
print("--- YFinance Bulk Test ---")
for s in symbols:
    try:
        t = yf.Ticker(s)
        hist = t.history(period='5d')
        print(f"{s}: {len(hist)} rows")
    except Exception as e:
        print(f"{s}: ERROR - {e}")
