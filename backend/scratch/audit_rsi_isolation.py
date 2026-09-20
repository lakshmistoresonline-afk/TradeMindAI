import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.signal_quality_gate import SignalQualityGate
from backend.domain.models.ios import LiveSignal
from backend.core.config import settings

def test_rsi():
    print("CLAIM: RSI Exhaustion Isolation (Shadow Only)")
    print("-" * 60)

    # 1. Test with RSI Disabled (Default)
    settings.V23_RSI_EXHAUSTION_ENABLED = False
    sig = LiveSignal(
        id="test", symbol="TEST", direction="LONG",
        calibrated_probability=0.8, conviction=80.0, status="ACTIVE",
        entry_price=100.0, target_price=150.0, stop_price=50.0, expected_value=10.0,
        risk_reward_ratio=2.0
    )

    # RSI is exhausted (80 > 75)
    features = {"rsi_14": 80.0}

    res_disabled = SignalQualityGate.evaluate_v23_gate(sig, features)
    print(f"RSI 80 (LONG) | RSI Enabled: {settings.V23_RSI_EXHAUSTION_ENABLED} -> Decision: {res_disabled['decision']}")

    # 2. Test with RSI Enabled
    settings.V23_RSI_EXHAUSTION_ENABLED = True
    res_enabled = SignalQualityGate.evaluate_v23_gate(sig, features)
    print(f"RSI 80 (LONG) | RSI Enabled: {settings.V23_RSI_EXHAUSTION_ENABLED} -> Decision: {res_enabled['decision']} (Reasons: {res_enabled['reasons']})")

    if res_disabled['decision'] == "PUBLISH" and res_enabled['decision'] == "BLOCK":
        print("\nRESULT: PASS")
    else:
        print("\nRESULT: FAIL")

if __name__ == "__main__":
    test_rsi()
