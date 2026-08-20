
from yahooquery import Ticker
import datetime

symbol = "TATAMOTORS.NS"
tk = Ticker(symbol)

start = datetime.datetime(2020, 1, 1)
end = datetime.datetime.utcnow()

print(f"Fetching {symbol} from {start} to {end}...")
hist = tk.history(start=start, end=end)
print(f"Total rows: {len(hist)}")
if not hist.empty:
    print(f"First: {hist.index[0]}")
    print(f"Last: {hist.index[-1]}")
