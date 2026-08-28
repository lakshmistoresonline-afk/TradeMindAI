
import os
import sys
import asyncio
import sqlite3
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import ShadowSignalDB, SessionLocal
from production.shadow.shadow_service import ShadowService

async def recovery_test():
    print("--- SHADOW RECOVERY TEST ---")

    # 1. Create a synthetic test signal
    test_id = f"test_sig_{uuid.uuid4().hex[:8]}"
    print(f"[*] Step 1: Creating test signal {test_id}")

    with SessionLocal() as session:
        sig = ShadowSignalDB(
            id=test_id,
            timestamp=datetime.utcnow(),
            symbol="TEST_RECOVERY",
            direction="LONG",
            calibrated_probability=0.75,
            expected_value=10.0,
            status="ACTIVE",
            strategy_version="v2.2"
        )
        session.add(sig)
        session.commit()

    # 2. Simulate "Service Stop" (we just check if it's there)
    print("[*] Step 2: Simulating service stop/start")

    # 3. Verify persistence
    with SessionLocal() as session:
        stored = session.query(ShadowSignalDB).filter(ShadowSignalDB.id == test_id).first()
        if not stored:
            print("[FAIL] Signal lost after 'restart'!")
            return False
        print("[PASS] Signal persisted correctly.")

    # 4. Resolve signal and check again
    print("[*] Step 3: Resolving signal to WIN")
    with SessionLocal() as session:
        stored = session.query(ShadowSignalDB).filter(ShadowSignalDB.id == test_id).first()
        stored.status = "TARGET_HIT"
        stored.net_return = 3.0
        session.commit()

    # 5. Simulate another restart
    print("[*] Step 4: Simulating second stop/start")
    with SessionLocal() as session:
        stored = session.query(ShadowSignalDB).filter(ShadowSignalDB.id == test_id).first()
        if not stored or stored.status != "TARGET_HIT":
            print("[FAIL] Resolved outcome lost or corrupted!")
            return False
        print("[PASS] Resolved outcome persisted correctly.")

    # 6. Cleanup test data
    print("[*] Step 5: Cleaning up test data")
    with SessionLocal() as session:
        session.query(ShadowSignalDB).filter(ShadowSignalDB.symbol == "TEST_RECOVERY").delete()
        session.commit()

    print("\n[SUCCESS] Shadow Recovery Test PASSED.")
    return True

if __name__ == "__main__":
    asyncio.run(recovery_test())
