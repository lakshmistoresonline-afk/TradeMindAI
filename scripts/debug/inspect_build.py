import glob
import os

def inspect():
    assets = glob.glob('web/dist/assets/*.js')
    print(f"Found {len(assets)} JS assets.")

    targets = [
        "CHALLENGER V2.3",
        "SHADOW SIGNAL",
        "MODEL PROBABILITY",
        "PRIMARY SWING",
        "EXPERIMENTAL SHORT",
        "NO CURRENTLY QUALIFIED SIGNALS",
        "EQUITY SCANNER",
        "WATCHLIST",
        "ACCURACY",
        "RESEARCH",
        "NSE LIVE FEED ACTIVE",
        "AI CORE V2.2"
    ]

    for a in assets:
        print(f"\nInspecting: {a}")
        with open(a, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for t in targets:
                if t in content:
                    print(f"   [FOUND] {t}")
                else:
                    # Case insensitive check just in case
                    if t.lower() in content.lower():
                         print(f"   [FOUND_CI] {t}")

if __name__ == "__main__":
    inspect()
