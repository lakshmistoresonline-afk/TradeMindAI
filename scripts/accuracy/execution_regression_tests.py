import os
import sys
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.services.outcome_engine import OutcomeEngine
from backend.domain.models.ios import LiveSignal

def create_mock_data(open_val, high, low, close):
    return pd.DataFrame([{
        "Open": open_val, "High": high, "Low": low, "Close": close, "Volume": 10_000_000
    }], index=[pd.to_datetime("2026-08-20")])

async def test_scenarios():
    base_signal = {
        "id": "test", "symbol": "TEST", "timestamp": datetime(2026, 8, 19),
        "rating": "BUY", "timeframe": "SWING", "status": "WAITING_FOR_ENTRY",
        "conviction": 60.0
    }

    scenarios = [
        {
            "name": "1. LONG favorable gap (misnomer: Gap Against) then intrabar fill",
            "direction": "LONG", "entry": 100, "target": 103, "stop": 97,
            "data": [101, 102, 99.5, 101.5], # Open, High, Low, Close
            "expected_entry": 100, "expected_status": "ACTIVE"
        },
        {
            "name": "2. LONG favorable gap below stop (Gap through stop)",
            "direction": "LONG", "entry": 100, "target": 103, "stop": 97,
            "data": [95, 96, 94, 95.5],
            "expected_entry": None, "expected_status": "WAITING_FOR_ENTRY" # Rule B
        },
        {
            "name": "3. SHORT favorable gap below entry but above target",
            "direction": "SHORT", "entry": 100, "target": 97, "stop": 103,
            "data": [99, 100.5, 98.5, 99.5],
            "expected_entry": 100, "expected_status": "ACTIVE"
        },
        {
            "name": "4. SHORT favorable gap above stop (Gap through stop)",
            "direction": "SHORT", "entry": 100, "target": 97, "stop": 103,
            "data": [105, 106, 104, 105.5],
            "expected_entry": None, "expected_status": "WAITING_FOR_ENTRY" # Rule B
        },
        {
            "name": "5. Normal intrabar entry",
            "direction": "LONG", "entry": 100, "target": 103, "stop": 97,
            "data": [101, 102, 99, 100.5],
            "expected_entry": 100, "expected_status": "ACTIVE"
        },
        {
            "name": "6. Gap against entry",
            "direction": "LONG", "entry": 100, "target": 103, "stop": 97,
            "data": [105, 106, 104, 105.5],
            "expected_entry": None, "expected_status": "WAITING_FOR_ENTRY"
        },
        {
            "name": "7. Entry exactly at stop",
            "direction": "LONG", "entry": 100, "target": 103, "stop": 97,
            "data": [97, 98, 96, 97.5],
            "expected_entry": None, "expected_status": "WAITING_FOR_ENTRY" # Boundary Rule B
        }
    ]

    print("--- EXECUTION REGRESSION TESTS ---")
    all_passed = True
    for s in scenarios:
        sig = LiveSignal(**base_signal, direction=s['direction'],
                         entry_price=s['entry'], target_price=s['target'], stop_loss_price=s['stop'])
        df = create_mock_data(*s['data'])

        outcome = OutcomeEngine.evaluate_outcome(sig, df)

        passed = (outcome['status'] == s['expected_status'] and
                  outcome.get('actual_entry_price') == s['expected_entry'])

        if not passed:
            all_passed = False
            print(f"[FAIL] {s['name']}")
            print(f"       Expected: {s['expected_status']} at {s['expected_entry']}")
            print(f"       Actual:   {outcome['status']} at {outcome.get('actual_entry_price')}")
        else:
            print(f"[PASS] {s['name']}")

    if all_passed:
        print("\n[SUCCESS] All execution scenarios verified.")
    else:
        print("\n[ERROR] Execution regression failed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_scenarios())
