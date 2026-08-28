import os
import sys
import asyncio
from dotenv import load_dotenv
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, ShadowSignalDB, LiveSignalDB
from backend.core.database import db_client

async def reconcile_all():
    print("--- TRADEMIND AI: MASTER RECONCILIATION ---")

    # 1. Neon counts
    session = SessionLocal()
    shadow_count = session.query(ShadowSignalDB).count()
    live_count = session.query(LiveSignalDB).count()
    session.close()

    # 2. Firestore counts
    fs_shadow = db_client.collection("shadow_signals").count().get()
    fs_live = db_client.collection("live_signals").count().get()

    print(f"Shadow Signals: Neon={shadow_count}, Firestore={fs_shadow[0][0].value}")
    print(f"Live Signals:   Neon={live_count}, Firestore={fs_live[0][0].value}")

    if shadow_count != fs_shadow[0][0].value:
        print("[!] DISCREPANCY detected in Shadow Signals count.")
    if live_count != fs_live[0][0].value:
        print("[!] DISCREPANCY detected in Live Signals count.")

    # 3. Specific Signal Check (SBIN)
    sbin_id = "sig_SBIN_202608180715"
    with SessionLocal() as session:
        pg_sig = session.query(ShadowSignalDB).filter(ShadowSignalDB.id == sbin_id).first()
        if pg_sig:
            fs_doc = db_client.collection("shadow_signals").document(sbin_id).get()
            if fs_doc.exists:
                fs_data = fs_doc.to_dict()
                print(f"\nSBIN Reconcile ({sbin_id}):")
                print(f"   Status: PG={pg_sig.status}, FS={fs_data['status']}")
                print(f"   Net P&L: PG={pg_sig.net_return}, FS={fs_data['net_return']}")
            else:
                print(f"\n[!] SBIN {sbin_id} missing in Firestore.")
        else:
            print(f"\n[!] SBIN {sbin_id} missing in Postgres.")

if __name__ == "__main__":
    asyncio.run(reconcile_all())
