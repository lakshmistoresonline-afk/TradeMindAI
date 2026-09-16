import requests
import json

URL = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"

def test():
    print(f"Fetching from {URL}...")
    resp = requests.get(URL)
    if resp.status_code != 200:
        print(f"Error: {resp.status_code}")
        return

    data = resp.json()
    print(f"Received {len(data)} signals.")

    for s in data:
        if s['symbol'] == 'CIPLA':
            print("\n--- CIPLA Signal Raw ---")
            print(json.dumps(s, indent=2))
            print(f"\nSummary: Entry {s.get('entry_price')} | Current {s.get('current_price')} | Last {s.get('last_price')}")

if __name__ == "__main__":
    test()
