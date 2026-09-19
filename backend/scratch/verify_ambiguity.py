import pandas as pd
import datetime
from datetime import timezone
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.outcome_service import OutcomeService
from backend.domain.models.ios import LiveSignal

def test_ambiguity():
    ts = datetime.datetime.now(timezone.utc)
    signal = LiveSignal(
        id="sig_test", symbol="TEST", direction="LONG",
        entry_price=100.0, target_price=110.0, stop_price=90.0,
        timestamp=ts, status="ACTIVE"
    )

    # Case: Both target and stop hit in one bar
    data = pd.DataFrame([
        {"Open": 100.0, "High": 115.0, "Low": 85.0, "Close": 105.0}
    ], index=[ts + datetime.timedelta(hours=1)])

    res = OutcomeService.evaluate_signal_outcome(signal, data)

    print("CLAIM: Same-bar High/Low trigger => AMBIGUOUS")
    print("-" * 60)
    print(f"Status: {res['status']}")
    print(f"Reason: {res.get('exit_reason')}")
    print(f"Verified: {res['outcome_verified']}")

    if res['status'] == "AMBIGUOUS":
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

if __name__ == "__main__":
    test_ambiguity()
