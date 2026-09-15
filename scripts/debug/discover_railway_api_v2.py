import requests

def discover():
    names = [
        "trademind-api",
        "trademind-backend",
        "trademind-ai",
        "trademind",
        "trademind-ai-backend",
        "trademind-prod",
        "trademind-api-prod",
        "trademindai"
    ]
    envs = [
        "-production",
        "-prod",
        ""
    ]

    for n in names:
        for e in envs:
            domain = f"{n}{e}.up.railway.app"
            url = f"https://{domain}/api/v1/health"
            print(f"Trying: {url}")
            try:
                resp = requests.get(url, timeout=3)
                print(f"   Status: {resp.status_code}")
                # Check if it's a JSON response (FastAPI usually returns JSON)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        print(f"   [JSON MATCH!] {domain} -> {data}")
                        return domain
                    except:
                        print(f"   [HTML MATCH (IGNORED)] {domain}")
                elif resp.status_code == 401 or resp.status_code == 403:
                     print(f"   [AUTH MATCH?] {domain}")
                     return domain
            except:
                pass
    return None

if __name__ == "__main__":
    discover()
