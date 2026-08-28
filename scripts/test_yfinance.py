import yfinance as yf
import pandas as pd

def test():
    symbol = "RELIANCE.NS"
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="10y")
    print(f"RELIANCE 10y Data Points: {len(df)}")
    print(f"Start Date: {df.index.min()}")
    print(f"End Date: {df.index.max()}")

if __name__ == "__main__":
    test()
