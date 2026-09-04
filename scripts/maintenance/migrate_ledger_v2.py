import os
import sys
import json
import pandas as pd
from sqlalchemy import text
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine, SessionLocal, ShadowSignalDB

def run_migration():
    print("--- TRADEMIND AI: CANONICAL SIGNAL LEDGER 2.0 MIGRATION ---")

    with engine.connect() as conn:
        # 1. Backup existing shadow_signals
        try:
            shadow_df = pd.DataFrame(conn.execute(text("SELECT * FROM shadow_signals")).fetchall())
            shadow_df.to_csv("docs/nifty200/BACKUP_shadow_signals_pre_v2.csv", index=False)
            print(f"[*] Backup created for {len(shadow_df)} shadow signals.")
        except:
            print("[!] No shadow signals to backup.")
            shadow_df = pd.DataFrame()

        # 2. Fetch all signals from live_signals
        try:
            live_df = pd.DataFrame(conn.execute(text("SELECT * FROM live_signals")).fetchall())
            print(f"[*] Fetched {len(live_df)} live signals for migration.")
        except Exception as e:
            print(f"[!] Error fetching live signals: {e}")
            live_df = pd.DataFrame()

    session = SessionLocal()
    try:
        # 3. Migrate unique records
        count = 0
        all_ids = set()
        if not shadow_df.empty:
            all_ids = set(shadow_df['id'].tolist())

        if not live_df.empty:
            for _, row in live_df.iterrows():
                if row['id'] in all_ids: continue

                # Map LiveSignalDB to ShadowSignalDB (Ledger 2.0)
                # Map fields manually where names differ
                db_sig = ShadowSignalDB(
                    id=row['id'],
                    symbol=row['symbol'],
                    timestamp=row['timestamp'],
                    direction=row['direction'],
                    entry_price=row['entry_price'],
                    target_price=row['target_price'],
                    stop_price=row['stop_loss_price'],
                    status=row['status'],
                    strategy_version=row['strategy_version'] or "v2.2",
                    model_version=row['model_version'] or "TradeMind-Legacy",
                    evaluation_mode="LEGACY_UNVERIFIED",
                    verification_level=0,
                    asset_type="EQUITY", # Default for legacy
                    created_at=row['timestamp'] or datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(db_sig)
                all_ids.add(row['id'])
                count += 1

        # 4. Update existing ShadowSignalDB records with new classifications
        # Mark the 50 verified ones as LEVEL 4
        # (Heuristic: outcome_verified = True)
        session.execute(text("""
            UPDATE shadow_signals
            SET verification_level = 4,
                evaluation_mode = 'LIVE_SHADOW_VERIFIED',
                lifecycle_state = 'TERMINAL'
            WHERE outcome_verified = TRUE
        """))

        # Mark Active ones as LEVEL 2
        session.execute(text("""
            UPDATE shadow_signals
            SET verification_level = 2,
                evaluation_mode = 'LIVE_SHADOW_ACTIVE',
                lifecycle_state = 'ACTIVE'
            WHERE status = 'ACTIVE'
        """))

        session.commit()
        print(f"\n[SUCCESS] Migration Complete. Migrated {count} new records. Updated existing records.")

    except Exception as e:
        print(f"[!!] Migration Failed: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
