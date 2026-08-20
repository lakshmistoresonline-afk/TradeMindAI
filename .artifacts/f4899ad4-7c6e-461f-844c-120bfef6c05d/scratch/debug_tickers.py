
import yfinance as yf

tickers = ["GUJGASLTD.NS", "TATAMOTORS.NS", "TMCV.NS", "PEL.NS", "PIRAMALFIN.NS"]
for t in tickers:
    print(f"\n--- DEBUG TICKER: {t} ---")
    tk = yf.Ticker(t)
    try:
        hist = tk.history(period="1mo")
        print(f"History rows: {len(hist)}")
        if not hist.empty:
            print(f"First date: {hist.index[0]}")
            print(f"Last date: {hist.index[-1]}")
    except Exception as e:
        print(f"Error: {e}")
