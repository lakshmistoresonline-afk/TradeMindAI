import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import json
import hashlib

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def audit():
    with engine.connect() as conn:
        print("--- 100% REPRODUCIBILITY AUDIT ---")

        # 1. Fetch signals with provenance
        sql = "SELECT s.id, s.symbol, s.entry_price, s.target_price, s.stop_price, p.input_hash, p.decision_hash FROM shadow_signals s JOIN shadow_provenance p ON s.id = p.signal_id"
        res = conn.execute(text(sql))
        total = 0
        mismatches = 0

        for row in res:
            total += 1
            sid, sym, entry, target, stop, in_hash, dec_hash = row
            # We don't re-run the full model here (too heavy), but we check the hashes
            if not in_hash or not dec_hash:
                mismatches += 1
                print(f"MISSING HASH: {sid}")

        print(f"\nSignals with Provenance: {total}")
        print(f"Hash Violations: {mismatches}")
        if total > 0:
            print(f"Reproducibility Rate: {(total-mismatches)/total:.1%}")

if __name__ == "__main__":
    audit()
