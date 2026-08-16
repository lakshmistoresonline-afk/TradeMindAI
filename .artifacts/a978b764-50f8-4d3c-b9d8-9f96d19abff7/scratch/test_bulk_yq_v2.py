from yahooquery import Ticker
import pandas as pd

symbols = ["TMCV.NS", "GMRAIRPORT.NS", "LTF.NS", "LTIM.NS", "ZOMATO.NS", "PEL.NS"]
print("--- YahooQuery Bulk Test v2 ---")
t = Ticker(symbols, asynchronous=False)
hist = t.history(period='5d')

for s in symbols:
    if s in hist.index:
        count = len(hist.loc[s])
    elif isinstance(hist.index, pd.MultiIndex) and s in hist.index.get_level_values(0):
        count = len(hist.loc[s])
    else:
        count = 0
    print(f"{s}: {count} rows")
