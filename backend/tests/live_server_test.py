import threading
import time
import requests
import uvicorn
from backend.app.main import app

class ServerThread(threading.Thread):
    def __init__(self, app, host="127.0.0.1", port=8000):
        super().__init__()
        self.host = host
        self.port = port
        self.config = uvicorn.Config(app=app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def main():
    print("[Live Server Test] Starting uvicorn server in background thread...")
    server_thread = ServerThread(app, host="127.0.0.1", port=8000)
    server_thread.start()

    # Wait for server to start up
    time.sleep(3)

    try:
        endpoints = [
            "/",
            "/api/v1/system/health",
            "/api/v1/stocks/market-stats",
            "/api/v1/equity/signals"
        ]

        for ep in endpoints:
            url = f"http://127.0.0.1:8000{ep}"
            try:
                res = requests.get(url, timeout=5)
                print(f"GET {ep} -> Status: {res.status_code}")
                try:
                    data = res.json()
                    print(f"  Response summary: {str(data)[:300]}")
                except Exception:
                    print(f"  Response text: {res.text[:300]}")
            except Exception as e:
                print(f"GET {ep} -> Failed with exception: {e}")

    finally:
        print("[Live Server Test] Stopping server...")
        server_thread.stop()
        server_thread.join(timeout=3)
        print("[Live Server Test] Server stopped.")

if __name__ == "__main__":
    main()
