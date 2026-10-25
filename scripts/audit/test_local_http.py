import http.server
import threading
import urllib.request
import os
import sys

PORT = 8099
DIRECTORY = "web/dist"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_server():
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    server.timeout = 2
    # Serve a few requests then shut down
    server.handle_request()
    server.handle_request()
    server.handle_request()
    server.server_close()

def main():
    if not os.path.exists(DIRECTORY):
        print(f"Error: Directory {DIRECTORY} does not exist.")
        sys.exit(1)

    t = threading.Thread(target=run_server, daemon=True)
    t.start()

    urls = [
        f"http://127.0.0.1:{PORT}/",
        f"http://127.0.0.1:{PORT}/signals.json",
        f"http://127.0.0.1:{PORT}/performance.json"
    ]

    for url in urls:
        print(f"PROBING: {url}")
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as resp:
                print(f"  Status: {resp.status}")
                print(f"  Content-Type: {resp.headers.get('Content-Type')}")
                body = resp.read().decode('utf-8', errors='ignore')
                print(f"  Body Preview: {body[:150]}...\n")
        except urllib.error.HTTPError as e:
            print(f"  HTTPError Status: {e.code} ({e.reason})\n")
        except Exception as e:
            print(f"  Error: {e}\n")

if __name__ == '__main__':
    main()
