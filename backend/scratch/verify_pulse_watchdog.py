import sys
import os
import asyncio
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.pulse_watchdog import PulseWatchdog
from backend.core.postgres import SessionLocal, PulseExecutionDB

async def test_watchdog():
    print("CLAIM: Pulse watchdog state persists via database")
    print("-" * 60)

    # 1. Clear in-memory state
    PulseWatchdog._last_success = None

    # 2. Inject a successful execution into the DB
    with SessionLocal() as db:
        # Delete any existing for clean test
        db.query(PulseExecutionDB).delete()

        exec_id = "test_pulse_ok"
        now = datetime.now(timezone.utc)
        pulse = PulseExecutionDB(
            execution_id=exec_id,
            started_at=now - timedelta(minutes=5),
            finished_at=now - timedelta(minutes=4),
            duration_ms=60000,
            status="COMPLETED"
        )
        db.add(pulse)
        db.commit()

    # 3. Check status (should be HEALTHY as it was 4m ago)
    status = PulseWatchdog.get_status()
    print(f"Watchdog Status: {status['status']}")

    if status['status'] == "HEALTHY":
        print("RESULT: PASS")
    else:
        print(f"RESULT: FAIL (Expected HEALTHY, got {status['status']})")

if __name__ == "__main__":
    asyncio.run(test_watchdog())
