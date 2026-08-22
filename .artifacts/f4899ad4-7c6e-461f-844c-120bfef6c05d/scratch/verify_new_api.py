
import os
import sys
import asyncio
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.api.v1.endpoints.shadow import get_shadow_status, get_shadow_summary, get_active_signals
from backend.core.database import db_client

async def verify():
    print("--- API VERIFICATION ---")

    if not db_client:
        print("db_client is None. Check Firebase config.")
        return

    # 1. Test Status
    status = await get_shadow_status()
    print(f"Status Data Source: {status.get('data_source')}")
    print(f"Baseline Start: {status.get('baseline_start')}")

    # 2. Test Summary
    summary = await get_shadow_summary()
    print(f"Summary Active Signals: {summary.get('active_signals')}")
    print(f"Summary Completed Trades: {summary.get('completed_trades')}")

    # 3. Test Active Signals
    active = await get_active_signals()
    print(f"Active Signals Count: {len(active)}")
    for s in active:
        print(f"  - {s.get('symbol')} ({s.get('status')})")

    # 4. Direct Firestore Check for Comparison
    print("\n--- DIRECT FIRESTORE CHECK ---")
    latest = db_client.collection("shadow_summary").document("latest").get().to_dict()
    if latest:
        print(f"Firestore Equity: {latest.get('equity')}")
        print(f"Firestore Active Positions: {latest.get('active_positions')}")

    active_docs = list(db_client.collection("shadow_signals").where("status", "==", "ACTIVE").stream())
    print(f"Firestore Active Signals Count: {len(active_docs)}")

if __name__ == "__main__":
    asyncio.run(verify())
