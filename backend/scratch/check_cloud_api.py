import httpx

def check():
    url = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"
    try:
        res = httpx.get(url, timeout=30.0)
        print(f"Cloud API ({url}) -> Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Signals: {len(data)}")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    check()
