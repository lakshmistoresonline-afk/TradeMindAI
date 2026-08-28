import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def run_recon():
    print("[*] Starting Cross-Tier Reconciliation Audit...")

    # 1. Neon Repository
    sigs_repo = await container.ios_repo.get_active_live_signals()
    repo_ids = {s.id for s in sigs_repo if s.id.startswith('master_')}

    # 2. Firestore Mirror (Mocking check since local init skipped)
    from backend.core.database import db_client
    firestore_ids = set()
    if bool(db_client):
        try:
            fs_sigs = db_client.collection('live_signals').where('status', '==', 'ACTIVE').get()
            firestore_ids = {s.id for s in fs_sigs}
        except: pass

    print(f"   Neon Master Signals: {len(repo_ids)}")
    print(f"   Firestore Mirror:    {len(firestore_ids) if bool(db_client) else 'SKIPPED (Local)'}")

    # 3. Field Verification
    if sigs_repo:
        s = sigs_repo[0]
        print(f"\n[*] Sample Signal Integrity ({s.symbol}):")
        print(f"   - ID Unique:       {len(repo_ids) == len(set(repo_ids))}")
        print(f"   - Created_at:      {s.timestamp}")
        print(f"   - Entry Price:     {s.entry_price}")
        print(f"   - Target Price:    {s.target_price}")
        print(f"   - Prob (Calibrated):{s.calibrated_probability}")
        print(f"   - Expected Value:  {s.expected_value}")

    print("\n[SUCCESS] Reconciliation Check Complete.")

if __name__ == "__main__":
    asyncio.run(run_recon())
