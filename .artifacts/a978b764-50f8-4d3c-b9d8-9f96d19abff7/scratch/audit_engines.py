import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.services.signal_engine import SignalEngine
from backend.services.outcome_engine import OutcomeEngine
from backend.domain.models.ios import LiveSignal
from datetime import datetime, timedelta

def audit_engines():
    print("============================================================")
    print(" SIGNAL & OUTCOME ENGINE FORENSIC AUDIT")
    print("============================================================")

    # 1. Test Same-Candle Ambiguity in OutcomeEngine
    print("\n[*] Testing Same-Candle Ambiguity Policy...")
    # Target=110, Stop=90, Entry=100
    # Candle High=115, Low=85 -> Both hit
    signal = LiveSignal(
        id="test_sig", symbol="TEST", timestamp=datetime(2026, 1, 1),
        rating="BUY", direction="LONG", conviction=80,
        entry_price=100.0, target_price=110.0, stop_loss_price=90.0,
        timeframe="SWING", status="ACTIVE"
    )

    future_data = pd.DataFrame([
        {"Open": 100, "High": 115, "Low": 85, "Close": 105}
    ], index=[datetime(2026, 1, 1, 10, 0)])

    outcome = OutcomeEngine.evaluate_outcome(signal, future_data)
    print(f"   Status: {outcome['status']}")
    if outcome['status'] == "STOP_LOSS":
        print("   [PASS] Conservative policy enforced (Assuming Stop Hit first).")
    else:
        print(f"   [FAIL] Expected STOP_LOSS, got {outcome['status']}.")

    # 2. Test Time-Safety (Look-ahead)
    print("\n[*] Testing Time-Safety in OutcomeEngine...")
    # Signal at 12:00. Data at 11:55 should be excluded.
    future_data_leak = pd.DataFrame([
        {"Open": 100, "High": 120, "Low": 90, "Close": 110}, # Leak (before signal)
        {"Open": 110, "High": 112, "Low": 108, "Close": 111} # Valid (at/after signal)
    ], index=[datetime(2026, 1, 1, 11, 55), datetime(2026, 1, 1, 12, 0)])

    outcome_safe = OutcomeEngine.evaluate_outcome(signal, future_data_leak)
    # Target is 110. High in 11:55 bar is 120. If leak, it should be TARGET_HIT.
    if outcome_safe['status'] == "TARGET_HIT" and outcome_safe['outcome_price'] == 110:
        # Actually in the loop it might hit target at 12:00 bar too if price is 110.
        # Let's adjust to make it unambiguous.
        pass

    # Redo for clarity
    future_data_leak_v2 = pd.DataFrame([
        {"Open": 100, "High": 120, "Low": 90, "Close": 100}, # Leak
        {"Open": 100, "High": 105, "Low": 95, "Close": 102}  # No trigger
    ], index=[datetime(2026, 1, 1, 11, 55), datetime(2026, 1, 1, 12, 0)])

    outcome_leak = OutcomeEngine.evaluate_outcome(signal, future_data_leak_v2)
    if outcome_leak['status'] == "TARGET_HIT":
        print("   [FAIL] Look-ahead leakage detected! Signal hit target using data from BEFORE its timestamp.")
    else:
        print("   [PASS] No look-ahead leakage detected.")

if __name__ == "__main__":
    audit_engines()
 domestic_audit = audit_engines()
