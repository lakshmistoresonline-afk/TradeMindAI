import requests
import json

URL = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"

def test():
    print(f"Testing connectivity to {URL}...")
    try:
        # Long timeout for cold starts
        resp = requests.get(URL, timeout=30)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Success! Received {len(data)} signals.")
        else:
            print(f"Error Body: {resp.text}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test()
