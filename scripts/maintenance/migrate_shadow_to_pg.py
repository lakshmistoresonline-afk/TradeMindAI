
import os
import sys
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.config import settings

def migrate():
    print("--- SHADOW DATABASE MIGRATION (SQLite -> PostgreSQL) ---")

    local_db = "backend/local_operational.db"
    pg_url = os.getenv("POSTGRES_URL")

    if not pg_url or "sqlite" in pg_url:
        print("[!] ERROR: POSTGRES_URL not set or points to SQLite. Migration halted.")
        return

    print(f"[*] Source: {local_db}")
    print(f"[*] Target: {pg_url.split('@')[-1]}") # Redact credentials

    # 1. Connect to Source
    conn_sq = sqlite3.connect(local_db)

    # 2. Connect to Target
    engine_pg = create_engine(pg_url)

    try:
        # A. Migrate shadow_signals (Baseline: 2026-08-18)
        print("[*] Migrating shadow_signals...")
        signals_df = pd.read_sql_query("SELECT * FROM shadow_signals WHERE timestamp >= '2026-08-18'", conn_sq)
        if not signals_df.empty:
            signals_df.to_sql("shadow_signals", engine_pg, if_exists='append', index=False)
            print(f"   [+] Migrated {len(signals_df)} signals.")
        else:
            print("   [INFO] No signals to migrate for Phase 5G baseline.")

        # B. Migrate shadow_events (Baseline: 2026-08-18)
        print("[*] Migrating shadow_events...")
        events_df = pd.read_sql_query("SELECT * FROM shadow_events WHERE timestamp >= '2026-08-18'", conn_sq)
        if not events_df.empty:
            events_df.to_sql("shadow_events", engine_pg, if_exists='append', index=False)
            print(f"   [+] Migrated {len(events_df)} events.")
        else:
            print("   [INFO] No events to migrate for Phase 5G baseline.")

        # 3. Verification
        with engine_pg.connect() as pg_conn:
            # Check SBIN Signal
            res = pg_conn.execute(text("SELECT status, net_return FROM shadow_signals WHERE symbol='SBIN' AND status='TARGET_HIT'")).fetchone()
            if res:
                print(f"[PASS] SBIN Target Hit migrated. Net Return: {res[1]}%")

            # Check completed count
            completed = pg_conn.execute(text("SELECT count(*) FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'TIMEOUT', 'AMBIGUOUS', 'INVALID')")).scalar()
            print(f"[*] Verified Completed Trades in PG: {completed} / 20")

        print("\n[SUCCESS] Migration Complete.")

    except Exception as e:
        print(f"[!] Migration Failed: {e}")
    finally:
        conn_sq.close()

if __name__ == "__main__":
    migrate()
