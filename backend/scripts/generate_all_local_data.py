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
    print("=== [TradeMind AI] Universal Local Data & Signal Generator (NIFTY 200 Full Population) ===")

    # Target Universe: ALL NIFTY 200 Constituents
    symbols = container.universe_service.NIFTY_200_CONSTITUENTS

    # 0. Sync Universe (Ensure Stock Master is populated)
    print("[*] PHASE 0: Synchronizing Universe Constituents...")
    await container.universe_service.sync_universe()

    end_date = datetime.datetime.now(timezone.utc)
    start_date = end_date - datetime.timedelta(days=120)

    ingestor = IngestionService(container.repository, container.provider)

    # --- PHASE 1: DATA INGESTION ---
    print("\n[*] PHASE 1: Ingesting Historical Context (N=200)...")
    # Batch ingestion to avoid timeouts
    for symbol in symbols:
        try:
            # Check if we already have prices
            count = await container.repository.get_price_count(symbol)
            if count > 50:
                print(f"   - {symbol}... SKIP (Already has {count} prices)")
                continue
        except: pass

        print(f"   - {symbol}...", end=" ", flush=True)
        try:
            res = await ingestor.ingest_historical_data(symbol, start_date, end_date, "1d")
            if res["status"] == "SUCCESS":
                # Ensure last_price is set for signal engine
                stock = await container.repository.get_stock_by_symbol(symbol)
                if stock and (not stock.last_price or stock.last_price == 0):
                    prices = await container.repository.get_recent_prices(symbol, limit=1)
                    if prices:
                        stock.last_price = prices[0].close
                        await container.repository.save_stock(stock)

                await container.feature_store.update_features(symbol)
                print("OK.")
            else:
                print(f"FAILED: {res.get('reason')}")
        except Exception as e:
            print(f"ERROR: {e}")

    # --- PHASE 2: ENSURE MODELS & REGIME ---
    print("\n[*] PHASE 2: Verifying Champion Models & Market Regime...")
    with SessionLocal() as db:
        for symbol in symbols:
            for h in ["SHORT", "SWING", "LONG"]:
                name = f"mod_{symbol}_v2.2_{h}"
                existing = db.query(ModelMetadataDB).filter(ModelMetadataDB.name == name).first()
                if not existing:
                    db.add(ModelMetadataDB(
                        name=name, symbol=symbol, version="v2.2", horizon=h,
                        type="RANDOM_FOREST", status="CHAMPION", is_champion=True,
                        accuracy=0.65, precision=0.62, recall=0.58,
                        roc_auc=0.72, brier_score=0.18,
                        last_trained=datetime.datetime.now(timezone.utc),
                        hyperparameters="{\"feature_names\": [\"Close\", \"ATR\", \"ema_200\", \"sma_20\", \"rsi_14\"], \"test_size\": 100, \"positives_test\": 30}",
                        feature_importances="{}"
                    ))

        db.query(RegimeDB).delete()
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

    with patch("backend.services.ml_service.MLService.predict_with_champion", side_effect=mock_predict), \
         patch("backend.services.signal_validator_service.SignalValidatorService.validate_publication", return_value={"is_valid": True}), \
         patch("backend.services.signal_quality_service.SignalQualityService.should_publish", return_value=True):

        for symbol in symbols:
            # 4.1 History (Replay) - 1 signal per symbol for speed
            df = await container.provider.get_history(symbol, start_date=history_start, end_date=end_date)
            if not df.empty:
                if not isinstance(df.index[0], datetime.datetime):
                    df.index = pd.to_datetime(df.index).tz_localize(timezone.utc)
                elif df.index[0].tzinfo is None:
                    df.index = df.index.tz_localize(timezone.utc)

                # Just 1 historical signal per symbol for maximum coverage speed
                ts = df.index[len(df)//2]

                signal = await SignalEngine.generate_signal(symbol, "EQUITY", "SWING", evaluation_timestamp=ts)
                if signal:
                    future_data = df[df.index >= ts]
                    outcome = OutcomeService.evaluate_signal_outcome(signal, future_data)
                    with SessionLocal() as db:
                        s_data = signal.model_dump()
                        s_data.update(outcome)
                        s_data["id"] = f"hist_{symbol}_{ts.strftime('%Y%m%d%H')}" # Unique string ID
                        s_data["status"] = outcome.get("status", "EXPIRED")
                        s_data["signal_type"] = s_data.get("timeframe")
                        s_data["signal_rating"] = s_data.get("rating")

                        existing = db.query(ShadowSignalDB).filter(ShadowSignalDB.id == s_data["id"]).first()
                        if not existing:
                            db.add(ShadowSignalDB(**{k: v for k, v in s_data.items() if hasattr(ShadowSignalDB, k)}))
                            db.commit()

            # 4.2 Live Signal
            try:
                live_sig = await SignalEngine.generate_signal(symbol, "EQUITY", "SWING")
                if live_sig:
                    with SessionLocal() as db:
                        existing = db.query(LiveSignalDB).filter(LiveSignalDB.symbol == symbol, LiveSignalDB.status == 'ACTIVE').first()
                        if not existing:
                            await SignalLedgerService.create_signal(live_sig)
                            print(f"   [+] {symbol} -> POPULATED")
            except Exception as e:
                print(f"   [!] {symbol} Live Error: {e}")

    # --- PHASE 5: MIRROR TO FIRESTORE ---
    print("\n[*] PHASE 5: Syncing to Global Web App (Firestore)...")
    from backend.scripts.mirror_local_to_firestore import mirror
    await mirror()

    print("\n=== [TradeMind AI] Universal Generation Complete. ===")

if __name__ == "__main__":
    asyncio.run(generate())
