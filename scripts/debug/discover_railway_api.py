import requests

def discover():
    prefixes = [
        "trademind-api",
        "trademind-backend",
        "trademind-ai",
        "trademind",
        "trademind-ai-backend"
    ]
    suffixes = [
        "-production",
        "-prod",
        ""
    ]

    for p in prefixes:
        for s in suffixes:
            url = f"https://{p}{s}.up.railway.app/health"
            print(f"Trying: {url}")
            try:
                resp = requests.get(url, timeout=5)
                print(f"   Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"   [MATCH FOUND!] {url}")
                    return url
            except:
                pass
    return None

if __name__ == "__main__":
    discover()
