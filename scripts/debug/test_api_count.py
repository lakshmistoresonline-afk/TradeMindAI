import requests
import subprocess
import time
import os

def test():
    # Start backend
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    proc = subprocess.Popen(["python", "-m", "backend.app.main"], env=env)
    time.sleep(5)

    try:
        resp = requests.get("http://localhost:8000/api/v1/equity/signals")
        data = resp.json()
        print(f"API Signal Count: {len(data)}")
        if len(data) > 0:
            print(f"Sample Quality Class: {data[0].get('quality_class')}")
    except Exception as e:
        print(f"API Test Failed: {e}")
    finally:
        proc.terminate()

if __name__ == "__main__":
    test()
