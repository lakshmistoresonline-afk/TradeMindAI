import asyncio
import datetime
from datetime import timezone
import os
import sys
import uuid
import pandas as pd
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# Force environment to development
os.environ["ENVIRONMENT"] = "development"

from backend.core.container import container
from backend.services.ingestion_service import IngestionService
from backend.services.equity_signal_generation_service import EquitySignalGenerationService
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.outcome_service import OutcomeService
from backend.core.postgres import SessionLocal, ShadowSignalDB, LiveSignalDB, ModelMetadataDB, StockDB, RegimeDB
from backend.domain.models.stock import Stock

async def generate():
    print("=== [TradeMind AI] Universal Local Data & Signal Generator (Aggressive Mode) ===")

    # Target Universe: Top 50 constituents for massive population
    symbols = container.universe_service.NIFTY_200_CONSTITUENTS[:50]

    end_date = datetime.datetime.now(timezone.utc)
    start_date = end_date - datetime.timedelta(days=120)

    ingestor = IngestionService(container.repository, container.provider)

    # --- PHASE 1: DATA INGESTION ---
    print("\n[*] PHASE 1: Ingesting Historical Context...")
    for symbol in symbols:
        print(f"   - {symbol}...", end=" ", flush=True)
        res = await ingestor.ingest_historical_data(symbol, start_date, end_date, "1d")
        if res["status"] == "SUCCESS":
            stock = await container.repository.get_stock_by_symbol(symbol)
            if not stock:
                await container.repository.save_stock(Stock(
                    symbol=symbol, name=f"{symbol} Limited", sector="UNKNOWN",
                    last_price=0.0
                ))
            try:
                await container.feature_store.update_features(symbol)
                print("OK.")
            except: print("Feature Calc Failed.")
        else:
            print(f"FAILED: {res.get('reason')}")

    # --- PHASE 2: ENSURE MODELS & REGIME ---
    print("\n[*] PHASE 2: Verifying Champion Models & Market Regime...")
    with SessionLocal() as db:
        for symbol in symbols:
            for h in ["SHORT", "SWING", "LONG"]:
                name = f"mod_{symbol}_v2.2_{h}"
                db.query(ModelMetadataDB).filter(ModelMetadataDB.name == name).delete()
                db.add(ModelMetadataDB(
                    name=name, symbol=symbol, version="v2.2", horizon=h,
                    type="RANDOM_FOREST", status="CHAMPION", is_champion=True,
                    accuracy=0.65, precision=0.62, recall=0.58,
                    roc_auc=0.72, brier_score=0.18,
                    last_trained=datetime.datetime.now(timezone.utc),
                    hyperparameters="{\"feature_names\": [\"Close\", \"ATR\", \"ema_200\", \"sma_20\", \"rsi_14\"], \"test_size\": 100, \"positives_test\": 30}",
                    feature_importances="{}"
                ))

        db.query(RegimeDB).delete() # Refresh regime
        db.add(RegimeDB(
            date=datetime.datetime.now(timezone.utc),
            regime="BULL", risk_mode="RISK_ON", sentiment_score=0.78,
            volatility_index=12.0, description="Hardened Local Bull Regime"
        ))
        db.commit()

    # --- PHASE 3: MOCKING FOR DETERMINISTIC POPULATION ---
    async def mock_predict(*args, **kwargs):
        return {
            "prediction": "UP",
            "confidence": 85.0,
            "model_version": "v2.2-local-mock",
            "metadata": {
                "calibrated_probability_up": 0.82,
                "raw_probability_up": 0.80,
                "is_calibrated": True
            }
        }

    # --- PHASE 4: AGGRESSIVE SIGNAL POPULATION ---
    print("\n[*] PHASE 4: Generating Massive Signal Population (History + Live)...")
    history_start = end_date - datetime.timedelta(days=30)

    # We patch all safety valves to ensure data population
    with patch("backend.services.ml_service.MLService.predict_with_champion", side_effect=mock_predict), \
         patch("backend.services.signal_validator_service.SignalValidatorService.validate_publication", return_value={"is_valid": True}), \
         patch("backend.services.signal_quality_service.SignalQualityService.should_publish", return_value=True):

        for symbol in symbols:
            # 4.1 History (Replay)
            df = await container.provider.get_history(symbol, start_date=history_start, end_date=end_date)
            if not df.empty:
                # Ensure index is timezone-aware datetime for comparison
                if not isinstance(df.index[0], datetime.datetime):
                    df.index = pd.to_datetime(df.index).tz_localize(timezone.utc)
                elif df.index[0].tzinfo is None:
                    df.index = df.index.tz_localize(timezone.utc)

                sample_indices = [len(df)//4, 2*len(df)//4, 3*len(df)//4]
                for idx in sample_indices:
                    if idx >= len(df): continue
                    ts = df.index[idx]
                    if hasattr(ts, 'to_pydatetime'): ts = ts.to_pydatetime()
                    elif isinstance(ts, datetime.date): ts = datetime.datetime.combine(ts, datetime.time.min)
                    if ts.tzinfo is None: ts = ts.replace(tzinfo=timezone.utc)

                    signal = await SignalEngine.generate_signal(symbol, "EQUITY", "SWING", evaluation_timestamp=ts)
                    if signal:
                        future_data = df[df.index >= ts]
                        outcome = OutcomeService.evaluate_signal_outcome(signal, future_data)
                        with SessionLocal() as db:
                            s_data = signal.model_dump()
                            s_data.update(outcome)
                            s_data["id"] = f"hist_{signal.id}"
                            s_data["status"] = outcome.get("status", "EXPIRED")
                            s_data["signal_type"] = s_data.get("timeframe")
                            s_data["signal_rating"] = s_data.get("rating")
                            db.add(ShadowSignalDB(**{k: v for k, v in s_data.items() if hasattr(ShadowSignalDB, k)}))
                            db.commit()

            # 4.2 Live Signal
            try:
                live_sig = await SignalEngine.generate_signal(symbol, "EQUITY", "SWING")
                if live_sig:
                    await SignalLedgerService.create_signal(live_sig)
                    print(f"   [+] {symbol} -> POPULATED (Live + History)")
            except Exception as e:
                print(f"   [!] {symbol} Error: {e}")

    # --- PHASE 5: MIRROR TO FIRESTORE ---
    print("\n[*] PHASE 5: Syncing to Global Web App (Firestore)...")
    from backend.scripts.mirror_local_to_firestore import mirror
    await mirror()

    print("\n=== [TradeMind AI] Massive Population Complete. ===")

if __name__ == "__main__":
    asyncio.run(generate())
