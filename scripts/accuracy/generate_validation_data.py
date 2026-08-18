import os
import sys
import asyncio
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from backend.services.signal_engine import SignalEngine
from backend.services.calibration_service import CalibrationService
from backend.domain.models.ios import LiveSignal, SignalEvent

async def generate():
    print("[*] Generating historical signals for validation audit...")

    # Clear old validation signals
    from sqlalchemy import text
    with container.repository.session_factory() as session:
        session.execute(text("DELETE FROM live_signals WHERE id LIKE 'val_%'"))
        session.commit()

    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "BHARTIARTL", "KOTAKBANK", "LT"]
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=60)

    signals_count = 0

    for symbol in symbols:
        # Fetch history to use for signal generation and outcome
        prices = await container.repository.get_recent_prices(symbol, limit=200)
        if not prices or len(prices) < 50: continue

        import pandas as pd
        df = pd.DataFrame([p.model_dump() for p in prices])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)

        # Capitalize columns for OutcomeEngine
        df.columns = [c.capitalize() for c in df.columns]

        # Pre-calculate SMC events for the entire window
        from backend.analysis.smc import SMCAnalysis
        smc_obs = SMCAnalysis.detect_order_blocks(df)
        smc_fvgs = SMCAnalysis.detect_fvg(df)

        # Simulate signal generation every few days
        for i in range(50, len(df) - 20, 5):
            sig_date = df.index[i]
            if isinstance(sig_date, str):
                sig_date = datetime.fromisoformat(sig_date.split('+')[0])

            price = df.iloc[i]["Close"]

            # Slice for time-safety
            sub_df = df.iloc[:i+1]

            # Get real features
            current_smc = {
                "order_blocks": [ob for ob in smc_obs if ob['index'] <= i],
                "fvgs": [f for f in smc_fvgs if f['index'] <= i],
            }
            ai_features = container.feature_store.extract_institutional_features(sub_df, current_smc)

            # Get real model prediction
            ml_res = await container.ml_service.predict_with_champion(symbol, ai_features)
            if ml_res.get("prediction") == "N/A": continue

            prob = ml_res.get("metadata", {}).get("calibrated_probability_up", 0.5)
            direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
            calibrated_prob = CalibrationService.get_direction_probability(prob, direction)

            if calibrated_prob < 0.52: continue

            target = price * (1.05 if direction == "LONG" else 0.95)
            stop = price * (0.97 if direction == "LONG" else 1.03)

            sig = LiveSignal(
                id=f"val_{symbol}_{sig_date.strftime('%Y%m%d%H%M')}",
                symbol=symbol,
                timestamp=sig_date,
                rating="BUY" if direction == "LONG" else "SELL",
                direction=direction,
                conviction=float(calibrated_prob * 100),
                entry_price=float(price),
                target_price=float(target),
                stop_loss_price=float(stop),
                timeframe="SWING",
                status="WAITING_FOR_ENTRY",
                calibrated_probability=float(calibrated_prob),
                raw_probability=ml_res.get("metadata", {}).get("raw_probability_up", 0.5),
                expected_value=1.0
            )

            # Resolve using real subsequent data
            future_df = df.iloc[i+1 : i+21]
            outcome = OutcomeEngine.evaluate_outcome(sig, future_df)

            sig.status = outcome["status"]
            sig.profit_pct = outcome["profit_pct"]
            sig.outcome_date = outcome["outcome_date"]
            sig.outcome_price = outcome["outcome_price"]
            sig.mfe = outcome["mfe"]
            sig.mae = outcome["mae"]
            sig.events = outcome["events"]

            await container.ios_repo.save_live_signal(sig)
            signals_count += 1

    print(f"[SUCCESS] Generated and resolved {signals_count} historical signals.")

if __name__ == "__main__":
    asyncio.run(generate())
