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
        # 1. Fetch all local live signals (Only ACTIVE/WAITING/ENTRY_TRIGGERED)
        print("[*] Fetching local live signals...")
        live_signals = db.query(LiveSignalDB).filter(LiveSignalDB.status.in_(['ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED'])).all()
        print(f"   [+] Found {len(live_signals)} truly active signals.")

        # 2. Fetch recent local shadow (historical) signals (Limit to last 50 for dashboard performance)
        print("[*] Fetching recent local shadow signals...")
        shadow_signals = db.query(ShadowSignalDB).order_by(ShadowSignalDB.timestamp.desc()).limit(50).all()
        print(f"   [+] Found {len(shadow_signals)} recent shadow signals.")

        all_signals = live_signals + shadow_signals

        # 3. Mirror each to Firestore (Chunked Batches for >500 limits)
        CHUNK_SIZE = 400
        total_signals = live_signals + shadow_signals

        if not total_signals:
            print("[!] No signals found to mirror.")
            return

        print(f"[*] Starting Mirroring for {len(total_signals)} total records...")

        for i in range(0, len(total_signals), CHUNK_SIZE):
            batch = db_client.batch()
            chunk = total_signals[i:i + CHUNK_SIZE]

            for s in chunk:
                model = container.ios_repo._map_db_to_live_signal(s)
                mirror_data = model.model_dump()
                mirror_data["mirrored_at"] = datetime.datetime.now(timezone.utc)
                mirror_data["source_local_id"] = model.id

                doc_ref = db_client.collection("signals").document(model.id)
                batch.set(doc_ref, mirror_data)

            print(f"   [*] Committing batch {i//CHUNK_SIZE + 1}...")
            batch.commit()

        print("[+] Firestore Mirror Complete.")

if __name__ == "__main__":
    asyncio.run(mirror())
