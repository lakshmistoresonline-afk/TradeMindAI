from yahooquery import search
import time

failures = ["GMRINFRA", "L&TFH", "LTIM", "PEL", "TATAMOTORS", "ZOMATO"]
for f in failures:
    print(f"Searching for {f}...")
    res = search(f)
    if res and 'quotes' in res:
        for q in res['quotes']:
            if q.get('exchange') in ['NSI', 'NSE']:
                print(f"   Found: {q['symbol']} ({q.get('shortname')})")
    time.sleep(1)
