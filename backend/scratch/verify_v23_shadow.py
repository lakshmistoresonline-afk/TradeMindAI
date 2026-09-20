import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Mock environment
os.environ["ENVIRONMENT"] = "development"

from backend.services.signal_quality_gate import SignalQualityGate
from backend.domain.models.ios import LiveSignal

def test_v23_gate():
    print("CLAIM: V2.3 Quality Gate enforces 60% probability floor")
    print("-" * 60)

    mock_signal_low = LiveSignal(
        id="test_low", symbol="TEST", direction="LONG",
        calibrated_probability=0.55, conviction=55.0, status="ACTIVE",
        entry_price=100.0, target_price=130.0, stop_price=90.0, expected_value=5.0,
        risk_reward_ratio=3.0
    )

    mock_signal_high = LiveSignal(
        id="test_high", symbol="TEST", direction="LONG",
        calibrated_probability=0.65, conviction=65.0, status="ACTIVE",
        entry_price=100.0, target_price=130.0, stop_price=90.0, expected_value=15.0,
        risk_reward_ratio=3.0
    )

    features = {"rsi_14": 50.0}

    res_low = SignalQualityGate.evaluate_v23_gate(mock_signal_low, features)
    res_high = SignalQualityGate.evaluate_v23_gate(mock_signal_high, features)

    print(f"Prob 55% -> Decision: {res_low['decision']} (Expected: BLOCK)")
    print(f"Prob 65% -> Decision: {res_high['decision']} (Expected: PUBLISH)")

    if res_low['decision'] == "BLOCK" and res_high['decision'] == "PUBLISH":
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")
        if res_high['decision'] == "BLOCK":
             print(f"DEBUG: reasons = {res_high['reasons']}")

def test_rsi_gate():
    print("\nCLAIM: RSI Exhaustion filter works in shadow mode")
    print("-" * 60)

    from backend.core.config import settings
    settings.V23_RSI_EXHAUSTION_ENABLED = True

    mock_signal = LiveSignal(
        id="test_rsi", symbol="TEST", direction="LONG",
        calibrated_probability=0.80, conviction=80.0, status="ACTIVE",
        entry_price=100.0, target_price=140.0, stop_price=80.0, expected_value=20.0,
        risk_reward_ratio=2.0
    )

    # RSI > 75 for LONG
    features_exhausted = {"rsi_14": 80.0}
    features_ok = {"rsi_14": 40.0}

    res_exhausted = SignalQualityGate.evaluate_v23_gate(mock_signal, features_exhausted)
    res_ok = SignalQualityGate.evaluate_v23_gate(mock_signal, features_ok)

    print(f"RSI 80 (LONG) -> Decision: {res_exhausted['decision']} (Expected: BLOCK)")
    print(f"RSI 40 (LONG) -> Decision: {res_ok['decision']} (Expected: PUBLISH)")

    if res_exhausted['decision'] == "BLOCK" and res_ok['decision'] == "PUBLISH":
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

    # Reset
    settings.V23_RSI_EXHAUSTION_ENABLED = False

if __name__ == "__main__":
    test_v23_gate()
    test_rsi_gate()
