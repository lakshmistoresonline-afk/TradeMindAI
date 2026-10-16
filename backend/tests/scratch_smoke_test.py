import subprocess
import time
import requests

def main():
    print("[Smoke Test] Starting uvicorn server...")
    proc = subprocess.Popen(["python", "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(3)
    try:
        urls = [
            "http://127.0.0.1:8000/",
            "http://127.0.0.1:8000/api/v1/system/health",
            "http://127.0.0.1:8000/api/v1/stocks/market-stats",
            "http://127.0.0.1:8000/api/v1/equity/signals"
        ]
        for url in urls:
            res = requests.get(url, timeout=5)
            print(f"GET {url} -> Status: {res.status_code}")
            try:
                data = res.json()
                print(f"  Response JSON summary: {str(data)[:200]}")
            except Exception:
                print(f"  Response text: {res.text[:200]}")
    finally:
        print("[Smoke Test] Terminating server process...")
        proc.terminate()
        proc.wait()
        print("[Smoke Test] Server stopped.")

if __name__ == "__main__":
    main()
