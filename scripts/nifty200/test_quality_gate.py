import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB

async def test_gate():
    print("[*] Testing Signal Quality Gate (Negative Test)...")

    # Simulate a signal that violates Part 13: Stop > Entry for Long
    invalid_sig = LiveSignalDB(
        id="gate_test_invalid",
        symbol="RELIANCE",
        direction="LONG",
        entry_price=2500.0,
        target_price=2600.0,
        stop_loss_price=2550.0, # INVALID: Stop is above entry for LONG
        status="ACTIVE",
        timestamp=datetime.now()
    )

    # The actual production SignalEngine should have a validation step.
    # We will verify if our Step 2 audit script catches it.
    from scripts.nifty200.validate_step2 import validate

    db = SessionLocal()
    db.add(invalid_sig)
    db.commit()

    print("[*] Invalid signal injected. Running Audit...")
    try:
        # validate() calls sys.exit(1) on failure, which is what we expect
        validate()
        print("[!] ERROR: Quality gate failed to catch invalid signal.")
    except SystemExit as e:
        if e.code == 1:
            print("[SUCCESS] Quality gate caught the invalid signal.")
        else:
            print(f"[!] Unexpected exit code: {e.code}")
    finally:
        db.query(LiveSignalDB).filter(LiveSignalDB.id == "gate_test_invalid").delete()
        db.commit()
        db.close()

if __name__ == "__main__":
    asyncio.run(test_gate())
