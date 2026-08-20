
from yahooquery import Ticker

tickers = ["GUJGASLTD.NS", "TATAMOTORS.NS", "PEL.NS"]
tk = Ticker(tickers)
hist = tk.history(period="1mo")
print(hist)
