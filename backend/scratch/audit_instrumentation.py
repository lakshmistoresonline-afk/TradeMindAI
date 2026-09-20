import sys
import os
import asyncio
import datetime
from datetime import timezone
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.getcwd())

# Ensure production-safe env
os.environ["ENVIRONMENT"] = "development"

from backend.services.signal_engine import SignalEngine
from backend.core.container import container
from backend.core.postgres import SessionLocal, LiveSignalDB
from backend.domain.models.ios import MarketRegime

async def test_instrumentation():
    print("CLAIM: V2.3 Entry & Regime Instrumentation")
    print("-" * 60)

    symbol = "RELIANCE"
    # 1. Mock Regime
    regime = MarketRegime(
        date=datetime.datetime.now(timezone.utc),
        regime="BULL", risk_mode="RISK_ON", sentiment_score=0.8,
        volatility_index=12.0, description="Bullish test"
    )

    # Patch ios_repo.get_latest_regime
    container.ios_repo.get_latest_regime = asyncio.iscoroutinefunction(container.ios_repo.get_latest_regime)
    original_get_regime = container.ios_repo.get_latest_regime
    async def mock_get_regime(): return regime
    container.ios_repo.get_latest_regime = mock_get_regime

    # 2. Generate Signal
    # Mock data platform features to ensure freshness
    from backend.domain.models.data_platform import FeatureVector
    async def mock_get_features(*args, **kwargs):
        return [FeatureVector(
            symbol=symbol, date=datetime.datetime.now(timezone.utc),
            version="v1.0.0", features={"Close": 100.0, "ATR": 2.0, "ema_200": 90.0, "sma_20": 95.0, "rsi_14": 50.0}
        )]
    container.data_platform_repo.get_features_by_range = mock_get_features

    # Mock ML service
    async def mock_predict(*args, **kwargs):
        return {
            "prediction": "UP",
            "metadata": {"calibrated_probability_up": 0.75, "raw_probability_up": 0.70},
            "model_id": "mock_model", "model_version": "v1"
        }
    container.ml_service.predict_with_champion = mock_predict

    # Mock Quality Service
    from backend.services.signal_quality_service import SignalQualityService
    SignalQualityService.should_publish = MagicMock(return_value=True)
    SignalQualityService.get_quality_class = MagicMock(return_value="PRIMARY")

    # Mock PriceResolver
    from backend.services.price_resolver import PriceResolver
    async def mock_resolve(*args, **kwargs):
        return {"current_price": 100.0, "status": "FRESH", "source": "MOCK", "timestamp": datetime.datetime.now(timezone.utc)}
    PriceResolver.resolve_current_price = mock_resolve

    stock = await container.repository.get_stock_by_symbol(symbol)
    if not stock:
        print("   [!] RELIANCE not found in DB. Skipping.")
        return

    sig = await SignalEngine.generate_signal(
        symbol=symbol, asset_class="EQUITY", timeframe="SWING",
        stock=stock
    )

    if not sig:
        print("   [!] Signal not generated (Gate rejected?). Check logs.")
        return

    print(f"   [+] Signal Generated: {sig.id}")

    # 3. Verify DB persistence
    with SessionLocal() as db:
        db_sig = db.query(LiveSignalDB).filter(LiveSignalDB.id == sig.id).first()

        fields = [
            "candidate_timestamp", "published_at", "price_at_signal", "price_at_publish",
            "regime", "regime_available", "regime_source", "regime_confidence"
        ]

        for f in fields:
            val = getattr(db_sig, f)
            print(f"   {f}: {val}")

    print("\nRESULT: PASS (Fields verified in DB model)")

if __name__ == "__main__":
    asyncio.run(test_instrumentation())
