import requests
import json

URL_BASE = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals/"

def test():
    # 1. Get a historical signal ID from history endpoint
    resp_h = requests.get("https://trademind-api-m8jg.onrender.com/api/v1/equity/history", timeout=10)
    history = resp_h.json().get('records', [])
    if not history:
        print("No history found.")
        return

    sig_id = history[0]['id']
    print(f"Testing Detail for Historical Signal: {sig_id}")

    # 2. Call Detail Endpoint
    resp_d = requests.get(f"{URL_BASE}{sig_id}", timeout=10)
    print(f"Status Code: {resp_d.status_code}")
    if resp_d.status_code == 200:
        print("Success! Detail found.")
    else:
        print(f"Error: {resp_d.text}")

if __name__ == "__main__":
    test()
