import requests
import json

BASE_URL = 'https://trademind-api-production.up.railway.app/api/v1'

def check():
    print(f"Checking Production API: {BASE_URL}")

    # 1. Root
    try:
        r = requests.get('https://trademind-api-production.up.railway.app/')
        print(f"Root: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Root Error: {e}")

    # 2. Shadow Status
    try:
        r = requests.get(f"{BASE_URL}/shadow/status")
        print(f"Shadow Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Shadow Status Error: {e}")

    # 3. Shadow Summary
    try:
        r = requests.get(f"{BASE_URL}/shadow/summary")
        print(f"Shadow Summary: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Shadow Summary Error: {e}")

    # 4. Shadow Active Signals
    try:
        r = requests.get(f"{BASE_URL}/shadow/active-signals")
        print(f"Active Signals: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Active Signals Error: {e}")

if __name__ == "__main__":
    check()
