
import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import ShadowSignalDB, SessionLocal, ShadowEventDB
from production.shadow.shadow_service import ShadowService
from production.reports.shadow_reporter import ShadowReporter

async def trigger_test():
    print("[*] Triggering Test Outcome for SBIN...")

    with SessionLocal() as session:
        sig = session.query(ShadowSignalDB).filter(ShadowSignalDB.symbol == 'SBIN', ShadowSignalDB.status == 'ACTIVE').first()
        if not sig:
            print("[!] No active SBIN signal found.")
            return

        print(f"[*] Found active signal: {sig.id}")

        # Simulate a WIN (TARGET_HIT)
        sig.status = 'TARGET_HIT'
        sig.outcome_timestamp = datetime.utcnow()
        sig.realized_return = 3.0
        sig.realized_mfe = 3.5
        sig.realized_mae = -0.5
        sig.transaction_cost = 0.10
        sig.slippage = 0.10
        sig.net_return = 2.80

        # Log Event
        event = ShadowEventDB(
            event_type="OUTCOME_RESOLUTION",
            signal_id=sig.id,
            symbol=sig.symbol,
            timestamp=datetime.utcnow(),
            decision=sig.status,
            payload_json='{"status": "TARGET_HIT", "profit_pct": 3.0, "mfe": 3.5, "mae": -0.5}'
        )
        session.add(event)
        session.commit()

        print(f"[SUCCESS] SBIN signal resolved to TARGET_HIT in DB.")

        # Trigger Automated Reporting
        ShadowReporter.generate_outcome_reports(sig.id)

        # Update daily report
        from production.reports.generate_shadow_report import generate
        generate()

if __name__ == "__main__":
    asyncio.run(trigger_test())
