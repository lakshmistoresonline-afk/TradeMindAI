import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.signal_engine import SignalEngine
from backend.domain.models.ios import LiveSignal

async def test_failure_isolation():
    print("CLAIM: V2.3 Failure Isolation (V2.2 Production Safety)")
    print("-" * 60)

    # Mock all dependencies to isolate the gate/recording logic
    with patch("backend.services.signal_shadow_service.SignalShadowService.record_shadow_decision") as mock_record:
        # 1. Simulate Shadow DB Failure
        mock_record.side_effect = Exception("Neon Connection Timed Out")

        # We need to mock the rest of generate_signal to get to the point of recording
        with patch("backend.core.container.container.repository.get_stock_by_symbol") as mock_stock, \
             patch("backend.core.container.container.data_platform_repo.get_features_by_range") as mock_feat, \
             patch("backend.core.container.container.ml_service.predict_with_champion") as mock_ml, \
             patch("backend.core.container.container.ios_repo.get_latest_regime") as mock_regime, \
             patch("backend.services.signal_validator_service.SignalValidatorService.validate_publication") as mock_val:

             mock_stock_obj = MagicMock()
             mock_stock_obj.symbol = "TEST"
             mock_stock_obj.avg_volume = 20000000
             mock_stock_obj.name = "Test Co"
             mock_stock_obj.isin = "INE001"
             mock_stock_obj.instrument_id = "NSE_TEST"
             mock_stock.return_value = mock_stock_obj
             from datetime import datetime, timezone
             mock_feat.return_value = [MagicMock(date=datetime.now(timezone.utc), features={"Close": 100.0, "ATR": 2.0, "ema_200": 90.0, "sma_20": 95.0})]
             mock_ml.return_value = {
                 "prediction": "UP",
                 "metadata": {"calibrated_probability_up": 0.8, "raw_probability_up": 0.8},
                 "model_id": "mock", "model_version": "v1"
             }
             mock_regime.return_value = MagicMock(regime="BULL", sentiment_score=0.8)
             mock_val.return_value = {"is_valid": True}

             from backend.services.signal_quality_service import SignalQualityService
             with patch.object(SignalQualityService, "should_publish", return_value=True), \
                  patch.object(SignalQualityService, "get_quality_class", return_value="PRIMARY"):

                 print("Executing SignalEngine.generate_signal with shadow failure...")
                 sig = await SignalEngine.generate_signal("TEST", "EQUITY", "SWING")

             if sig:
                 print("   [PASS] V2.2 Signal returned despite shadow failure.")
             else:
                 print("   [FAIL] V2.2 Signal blocked by shadow error.")

             if sig:
                 print("\nRESULT: PASS")
             else:
                 print("\nRESULT: FAIL")

if __name__ == "__main__":
    asyncio.run(test_failure_isolation())
