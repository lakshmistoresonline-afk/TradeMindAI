import requests

def check():
    url = "https://com-webcraft-trademindai-c8f75.web.app/"
    print(f"Fetching: {url}")
    try:
        resp = requests.get(url, headers={"Cache-Control": "no-cache"})
        print(f"Status: {resp.status_code}")
        content = resp.text
        print("\n--- HTML CONTENT START ---")
        print(content)
        print("--- HTML CONTENT END ---\n")

        targets = [
            "CHALLENGER V2.3",
            "DASHBOARD",
            "SIGNALS",
            "PERFORMANCE",
            "SYSTEM STATUS"
        ]

        print("\nChecking for new UI strings in HTML:")
        for t in targets:
            if t in content:
                print(f"   [FOUND] {t}")
            else:
                print(f"   [NOT FOUND] {t}")

        # Check for JS bundle link
        import re
        js_match = re.search(r'src="/assets/index-(.*?)\.js"', content)
        if js_match:
            js_url = url + "assets/index-" + js_match.group(1) + ".js"
            print(f"\nFetching JS Bundle: {js_url}")
            js_resp = requests.get(js_url)
            js_content = js_resp.text
            print(f"JS Size: {len(js_content)} bytes")

            print("\nChecking for hardened strings in JS bundle:")
            for t in targets:
                if t in js_content:
                    print(f"   [FOUND] {t}")
                else:
                    print(f"   [NOT FOUND] {t}")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    check()
