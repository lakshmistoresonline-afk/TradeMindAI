import requests
import json

URL = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"

def audit():
    print("--- TRADEMIND AI: PRODUCTION LIFECYCLE AUDIT ---")
    try:
        r = requests.get(URL, timeout=60)
        if r.status_code != 200:
            print(f"Error: {r.status_code}")
            return

        signals = r.json()
        print(f"Total Signals: {len(signals)}")

        mismatches = 0
        for s in signals:
            symbol = s.get('symbol')
            direction = s.get('direction')
            entry = s.get('entry_price')
            current = s.get('current_price')
            status = s.get('status')

            # V2.2 Canonical Trigger Rules
            # LONG: Trigger if current >= entry (WAITING if current < entry)
            # SHORT: Trigger if current <= entry (WAITING if current > entry)

            expected = "WAITING_FOR_ENTRY"
            if direction == "LONG":
                if current >= entry: expected = "TRIGGERED / ACTIVE"
            else:
                if current <= entry: expected = "TRIGGERED / ACTIVE"

            # Since the system currently labels them WAITING_FOR_ENTRY
            # Let's see if the logic holds

            match = False
            if status == "WAITING_FOR_ENTRY" and expected == "WAITING_FOR_ENTRY":
                match = True
            elif status in ["TRIGGERED", "ACTIVE", "ENTRY_TRIGGERED"] and expected == "TRIGGERED / ACTIVE":
                match = True

            if not match:
                mismatches += 1
                print(f"[MISMATCH] {symbol} ({direction}): Status {status} | Expected {expected} | Entry {entry} | Curr {current}")
            else:
                pass # print(f"[OK] {symbol}")

        print(f"\nAudit Summary:")
        print(f"   Mismatches: {mismatches}")
        if mismatches == 0:
            print("[+] Lifecycle Truth Verified: All signals are in their technically correct state.")

    except Exception as e:
        print(f"Audit Failed: {e}")

if __name__ == "__main__":
    audit()
