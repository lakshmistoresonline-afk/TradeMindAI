import asyncio
import os
import sys
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.database import db_client

async def main():
    print("=== FIRESTORE DRIFT AUDIT ===")

    # 1. Get signals from Neon
    DATABASE_URL = os.getenv("POSTGRES_URL")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, symbol, direction, entry_price FROM live_signals;"))
        neon_signals = {r[0]: dict(r._mapping) for r in res.fetchall()}

    print(f"Neon: {len(neon_signals)} signals.")

    # 2. Get signals from Firestore
    if not db_client:
        print("Firestore client not initialized.")
        return

    fs_signals_ref = db_client.collection("signals")
    fs_docs = fs_signals_ref.stream()
    fs_signals = {doc.id: doc.to_dict() for doc in fs_docs}

    print(f"Firestore: {len(fs_signals)} signals.")

    drift_detected = []

    for sig_id, neon_data in neon_signals.items():
        if sig_id not in fs_signals:
            drift_detected.append(f"{sig_id}: MISSING_IN_FIRESTORE")
        else:
            fs_data = fs_signals[sig_id]
            # Check a few critical fields
            if neon_data['symbol'] != fs_data.get('symbol'):
                 drift_detected.append(f"{sig_id}: SYMBOL_MISMATCH")
            if abs(neon_data['entry_price'] - fs_data.get('entry_price', 0)) > 0.01:
                 drift_detected.append(f"{sig_id}: PRICE_MISMATCH")

    if not drift_detected:
        print("NO DRIFT DETECTED. PARITY PASS.")
    else:
        print(f"DRIFT DETECTED in {len(drift_detected)} records:")
        for d in drift_detected:
            print(f"  - {d}")

if __name__ == "__main__":
    asyncio.run(main())
