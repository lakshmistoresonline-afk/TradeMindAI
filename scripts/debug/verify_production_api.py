import requests
import json

def verify():
    url = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"
    print(f"Calling: {url}")
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Signal Count: {len(data)}")
            if len(data) > 0:
                horizons = {}
                qualities = {}
                for s in data:
                    h = s.get('timeframe')
                    q = s.get('quality_class')
                    horizons[h] = horizons.get(h, 0) + 1
                    qualities[q] = qualities.get(q, 0) + 1

                print("\nHorizon Distribution:")
                for h, count in horizons.items():
                    print(f"   {h}: {count}")

                print("\nQuality Distribution:")
                for q, count in qualities.items():
                    print(f"   {q}: {count}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    verify()
