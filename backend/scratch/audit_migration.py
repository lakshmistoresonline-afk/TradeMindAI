import os
import sys
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

# Mock environment
os.environ["ENVIRONMENT"] = "development"
os.environ["POSTGRES_URL"] = "sqlite:///G:/TradeMindAI/backend/local_operational.db"

from backend.core.postgres import SessionLocal

def test_migration():
    print("CLAIM: V2.3 Database Schema (Shadow Decisions & Instrumentation)")
    print("-" * 60)

    db = SessionLocal()
    try:
        # 1. Check shadow decisions table
        db.execute(text("SELECT * FROM signal_shadow_decisions LIMIT 1"))
        print("   [PASS] signal_shadow_decisions table exists.")

        # 2. Check new columns in live_signals
        res = db.execute(text("PRAGMA table_info(live_signals)"))
        cols = [r[1] for r in res.fetchall()]

        expected = [
            "candidate_timestamp", "published_at", "price_at_signal", "price_at_publish",
            "regime_timestamp", "regime_source", "regime_confidence", "regime_available"
        ]

        missing = []
        for e in expected:
            if e not in cols:
                missing.append(e)

        if not missing:
            print("   [PASS] All instrumentation columns exist in live_signals.")
        else:
            print(f"   [FAIL] Missing columns in live_signals: {missing}")

        if not missing:
            print("\nRESULT: PASS")
        else:
            print("\nRESULT: FAIL")

    except Exception as e:
        print(f"   [ERROR] Schema verification failed: {e}")
        print("\nRESULT: FAIL")
    finally:
        db.close()

if __name__ == "__main__":
    test_migration()
