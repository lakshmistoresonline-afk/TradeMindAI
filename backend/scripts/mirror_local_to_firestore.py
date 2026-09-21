import asyncio
import datetime
from datetime import timezone
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Mock environment
os.environ["ENVIRONMENT"] = "development"

from backend.core.postgres import SessionLocal, LiveSignalDB, ShadowSignalDB
from backend.core.database import db_client
from backend.core.container import container

async def mirror():
    print("=== [TradeMind AI] Local to Firestore Mirror Sync ===")

    if not db_client:
        print("[!] Firestore client not initialized. Check service-account.json.")
        return

    with SessionLocal() as db:
        # 1. Fetch all local live signals
        print("[*] Fetching local live signals...")
        live_signals = db.query(LiveSignalDB).all()
        print(f"   [+] Found {len(live_signals)} live signals.")

        # 2. Fetch all local shadow (historical) signals
        print("[*] Fetching local shadow signals...")
        shadow_signals = db.query(ShadowSignalDB).all()
        print(f"   [+] Found {len(shadow_signals)} shadow signals.")

        all_signals = live_signals + shadow_signals

        # 3. Mirror each to Firestore
        batch = db_client.batch()
        count = 0

        for s in all_signals:
            # Map DB object to model for serialization
            # Using _map_db_to_live_signal from ios_repo
            model = container.ios_repo._map_db_to_live_signal(s)

            mirror_data = model.model_dump()

            # Serialize datetimes for Firestore if model_dump didn't do it right
            # Actually, google-cloud-firestore handles python datetime objects natively.

            mirror_data["mirrored_at"] = datetime.datetime.now(timezone.utc)
            mirror_data["source_local_id"] = model.id

            # Use doc ID as signal ID
            doc_ref = db_client.collection("signals").document(model.id)
            batch.set(doc_ref, mirror_data)

            count += 1
            if count % 20 == 0:
                print(f"   [SYNC] Buffered {count} records...")

        if count > 0:
            print(f"[*] Committing batch write to Firestore ({count} records)...")
            batch.commit()
            print("[+] Firestore Mirror Complete.")
        else:
            print("[!] No signals found to mirror.")

if __name__ == "__main__":
    asyncio.run(mirror())
