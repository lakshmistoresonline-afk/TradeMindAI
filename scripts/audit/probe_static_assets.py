"""
================================================================================
TradeMindAI: Real HTTP Static Asset Isolation Probe CLI (PER-01 & TM-13)
================================================================================
Starts a local HTTP loopback server serving web/dist, sends real HTTP GET requests
to inspect asset exposure, records status codes, content-types, and byte sizes,
and cleanly terminates the server.
================================================================================
"""

import os
import sys
import time
import argparse
import tempfile
import urllib.request
import urllib.error
import http.server
import socketserver
import threading
from pathlib import Path

def probe_directory(dist_dir: str, host: str = "127.0.0.1", port: int = 8099) -> dict:
    dist_path = Path(dist_dir).resolve()
    if not dist_path.exists() or not dist_path.is_dir():
        raise FileNotFoundError(f"Directory not found: {dist_path}")

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dist_path), **kwargs)
        def log_message(self, format, *args):
            pass  # Suppress HTTP server stdout logs during probing

    server = socketserver.TCPServer((host, port), QuietHandler)
    server.allow_reuse_address = True
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    results = {}
    paths_to_probe = ["/", "/signals.json", "/performance.json", "/signals_history.json"]

    try:
        for path in paths_to_probe:
            url = f"http://{host}:{port}{path}"
            req = urllib.request.Request(url, headers={"User-Agent": "TradeMindAI-Asset-Probe/1.0"})
            try:
                with urllib.request.urlopen(req) as resp:
                    data = resp.read()
                    results[path] = {
                        "status": resp.status,
                        "content_type": resp.headers.get("Content-Type", "unknown"),
                        "bytes": len(data),
                        "exposed": resp.status == 200
                    }
            except urllib.error.HTTPError as err:
                results[path] = {
                    "status": err.code,
                    "content_type": err.headers.get("Content-Type", "unknown"),
                    "bytes": 0,
                    "exposed": False
                }
            except Exception as e:
                results[path] = {
                    "status": 0,
                    "content_type": "error",
                    "bytes": 0,
                    "error": str(e),
                    "exposed": False
                }
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=1.0)

    return results

def run_negative_control_test(host: str = "127.0.0.1", port: int = 8098) -> bool:
    """
    Negative Control Test: Serves a temporary directory containing a dummy signals.json file
    to prove that the probe accurately detects exposed files (status 200).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        dummy = Path(tmp_dir) / "signals.json"
        dummy.write_text('{"status": "EXPOSED_DUMMY"}')
        res = probe_directory(tmp_dir, host=host, port=port)
        detected_exposure = res.get("/signals.json", {}).get("exposed", False)
        return detected_exposure

def main():
    parser = argparse.ArgumentParser(description="TradeMindAI Static Asset Probe CLI")
    parser.add_argument("--dist-dir", type=str, default="web/dist", help="Path to built static directory")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Loopback host")
    parser.add_argument("--port", type=int, default=8099, help="Loopback port")
    parser.add_argument("--negative-control", action="store_true", help="Run negative control test fixture")

    args = parser.parse_args()

    print("================================================================================")
    print("  TRADEMIND AI REAL HTTP STATIC ASSET PROBE")
    print("================================================================================")

    # 1. Run Negative Control Test
    print("[1] Executing Probe Negative Control Test (verifying exposure detection capability)...")
    ctrl_passed = run_negative_control_test()
    if ctrl_passed:
        print("    [PASS] Negative control verified: Probe correctly detects exposed JSON files.")
    else:
        print("    [FAIL] Negative control failed: Probe did not detect exposed dummy file.")
        sys.exit(1)

    # 2. Probe Target Distribution Directory
    print(f"\n[2] Probing Target Static Directory: {args.dist_dir} on http://{args.host}:{args.port}")
    try:
        probe_res = probe_directory(args.dist_dir, host=args.host, port=args.port)
    except Exception as e:
        print(f"[!] FATAL: Probing failed: {e}")
        sys.exit(1)

    failures = []
    for path, info in probe_res.items():
        status = info["status"]
        ct = info.get("content_type", "unknown")
        b = info.get("bytes", 0)
        exp = info.get("exposed", False)

        status_str = f"Status {status} ({ct}, {b} bytes)"
        if path == "/":
            if status == 200:
                print(f"    [OK] Path '{path}': {status_str}")
            else:
                print(f"    [FAIL] Path '{path}': {status_str} - Index page failed to serve!")
                failures.append(f"Root path '/' returned status {status}")
        else:
            if exp:
                print(f"    [EXPOSED RISK!] Path '{path}': {status_str}")
                failures.append(f"Prohibited static dataset exposed at '{path}' (status 200)")
            else:
                print(f"    [SECURE] Path '{path}': {status_str}")

    print("\n[+] Server shutdown confirmed cleanly.")

    if failures:
        print("\n[FAIL] Static Asset Probe DENIED: Prohibited datasets exposed!")
        for f in failures:
            print(f"    - {f}")
        sys.exit(1)

    print("\n[SUCCESS] Static Asset Probe PASSED: Zero prohibited datasets exposed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
