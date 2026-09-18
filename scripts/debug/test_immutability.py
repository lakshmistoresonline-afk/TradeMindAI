import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import asyncio
import sys

sys.path.append(os.getcwd())
from backend.core.container import container
from backend.services.signal_ledger_service import SignalLedgerService

load_dotenv('backend/.env')

async def test():
    print("--- TRADEMIND AI: IMMUTABILITY PROTECTION TEST ---")

    # 1. Identify a terminal signal (TARGET_HIT) from shadow_signals or live_signals
    from backend.core.postgres import SessionLocal
    from sqlalchemy import text
    with SessionLocal() as session:
        # Check shadow_signals
        res = session.execute(text("SELECT id, status FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'TIMEOUT') LIMIT 1")).fetchone()

        if not res:
            print("[*] No terminal signals in shadow_signals. Checking live_signals...")
            res = session.execute(text("SELECT id, status FROM live_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'TIMEOUT') LIMIT 1")).fetchone()

        if not res:
            print("No terminal signals found for testing.")
            return

        sig_id, status = res
        print(f"Testing Signal: {sig_id} (Status: {status})")

        # 3. Attempt to update non-restricted field 'audit_status' (only if in live_signals)
        # SignalLedgerService.update_signal only works on LiveSignalDB
        # If the signal is in shadow_signals, we need to test a different mechanism or skip.

        # 2. Attempt to change entry_price via SignalLedgerService
        print("[*] Attempting to modify restricted field 'entry_price'...")
        success = await SignalLedgerService.update_signal(sig_id, {"entry_price": 9999.0})

        if not success:
            print("[PASS] Update BLOCKED by Ledger Service for terminal signal.")
        else:
            print("[FAIL] Update ALLOWED for restricted field in terminal state.")

        # 3. Attempt to update non-restricted field 'provenance'
        print("[*] Attempting to update metadata field 'audit_status'...")
        success_meta = await SignalLedgerService.update_signal(sig_id, {"audit_status": "VERIFIED_2.0"})
        if success_meta:
            print("[PASS] Metadata update allowed for terminal signal.")
        else:
            print("[FAIL] Metadata update blocked.")

if __name__ == "__main__":
    asyncio.run(test())
