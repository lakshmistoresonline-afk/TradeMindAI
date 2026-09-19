import sys
import os
import json
import pandas as pd
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.postgres import SessionLocal

def extract_ledger():
    print("[*] Connecting to Authoritative Ledger (Neon)...")
    db = SessionLocal()

    try:
        # 1. Fetch Shadow Signals (V2.2 population)
        # We look for strategy_version = 'v2.2' and evaluation_mode in ['LIVE_SHADOW', 'HISTORICAL_REPLAY']
        query = text("""
            SELECT * FROM shadow_signals
            WHERE strategy_version = 'v2.2'
            ORDER BY timestamp DESC
        """)

        res = db.execute(query)
        columns = res.keys()
        shadow_data = [dict(zip(columns, row)) for r in res.fetchall()]

        print(f"   [+] Extracted {len(shadow_data)} Shadow signals.")

        # 2. Fetch Live Signals (Active/Terminal)
        query_live = text("""
            SELECT * FROM live_signals
            WHERE strategy_version = 'v2.2'
            ORDER BY created_at DESC
        """)
        res_live = db.execute(query_live)
        cols_live = res_live.keys()
        live_data = [dict(zip(cols_live, row)) for row in res_live.fetchall()]

        print(f"   [+] Extracted {len(live_data)} Live signals.")

        # Combine population
        # We need to be careful with duplicates if same ID exists in both.
        # Primary ledger for forensics is shadow_signals.

        combined = shadow_data + live_data

        # 3. Save to forensic snapshot
        os.makedirs("backend/data/forensics", exist_ok=True)
        with open("backend/data/forensics/ledger_snapshot.json", "w") as f:
            # Use custom encoder for datetime
            def default(obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                return str(obj)
            json.dump(combined, f, default=default, indent=2)

        print("[SUCCESS] Ledger snapshot saved to backend/data/forensics/ledger_snapshot.json")

    except Exception as e:
        print(f"[!] Extraction failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    extract_ledger()
