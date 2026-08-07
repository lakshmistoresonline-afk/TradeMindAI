import httpx
import json

def check():
    base_url = "https://trademind-api-m8jg.onrender.com/api/v1"
    print("\n--- PRODUCTION API DATA AUDIT ---\n")

    endpoints = {
        "Stocks": "/stocks/",
        "Market Stats": "/stocks/market-stats",
        "Institutional Flow": "/stocks/fii-dii",
        "Market Regime": "/ios/regime",
        "Intelligence Report": "/ios/intel?type=CLOSING"
    }

    for name, path in endpoints.items():
        try:
            r = httpx.get(base_url + path, timeout=20.0)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    status = f"✅ {len(data)} items"
                elif isinstance(data, dict):
                    # Check for empty-like objects
                    is_empty = len(data) == 0 or (len(data) == 1 and "status" in data)
                    status = "⚠️ EMPTY OBJECT" if is_empty else "✅ DATA FOUND"
                else:
                    status = "✅ UNKNOWN FORMAT"
                print(f"[{name:.<25}] {status}")
            else:
                print(f"[{name:.<25}] ❌ ERROR {r.status_code}")
        except Exception as e:
            print(f"[{name:.<25}] ❌ TIMEOUT/ERROR: {e}")

    print("\n--- CHECK COMPLETE ---")

if __name__ == "__main__":
    check()
