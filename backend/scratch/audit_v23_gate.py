import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.signal_quality_gate import SignalQualityGate
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

def test_gate():
    print("CLAIM: V2.3 Quality Gate - 60% Probability Floor")
    print(f"Configured Threshold: {settings.V23_MIN_CALIBRATED_PROBABILITY}")
    print("-" * 60)

    cases = [
        (0.599, "BLOCK"),
        (0.600, "PUBLISH"),
        (0.601, "PUBLISH")
    ]

    features = {"rsi_14": 50.0}

    for prob, expected in cases:
        sig = LiveSignal(
            id="test", symbol="TEST", direction="LONG",
            calibrated_probability=prob, conviction=prob*100,
            status="ACTIVE", expected_value=10.0, risk_reward_ratio=2.0
        )
        res = SignalQualityGate.evaluate_v23_gate(sig, features)
        actual = res["decision"]
        status = "PASS" if actual == expected else "FAIL"
        print(f"Prob {prob:.3f} -> Actual: {actual:<10} | Expected: {expected:<10} | {status}")

if __name__ == "__main__":
    test_gate()
