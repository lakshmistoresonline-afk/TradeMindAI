
import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from backend.domain.models.ios import LiveSignal
from backend.services.calibration_service import CalibrationService

class WalkForwardV2:
    def __init__(self, symbols, windows=4):
        self.symbols = symbols
        self.windows = windows
        self.results = []

    async def run(self):
        print(f"--- WALK-FORWARD VALIDATION V2 ({self.windows} windows) ---")

        end_date = datetime.now()
        window_days = 90

        for w in range(self.windows):
            test_end = end_date - timedelta(days=w * window_days)
            test_start = test_end - timedelta(days=window_days)
            train_end = test_start - timedelta(days=1)

            print(f"\n[*] Window {w+1}: Train until {train_end.date()}, Test {test_start.date()} to {test_end.date()}")

            window_trades = []

            for symbol in self.symbols:
                features = await container.data_platform_repo.get_features_by_range(
                    symbol, datetime(2020, 1, 1), test_end
                )
                if not features: continue

                train_feats = [f for f in features if f.date <= train_end]
                test_feats = [f for f in features if test_start <= f.date <= test_end]

                if len(train_feats) < 200 or not test_feats: continue

                try:
                    # Train model for this window
                    metadata = await container.ml_service.train_and_register(f"wf2_{w}_{symbol}", train_feats)

                    # Fetch prices for outcome resolution
                    prices = await container.repository.get_recent_prices(symbol, limit=2500)
                    price_df = pd.DataFrame([p.model_dump() for p in prices])
                    price_df.set_index('date', inplace=True)
                    price_df.sort_index(inplace=True)
                    price_df.columns = [c.capitalize() for c in price_df.columns]

                    # Pre-calculate indicators for No-Trade filters
                    from backend.analysis.technical import TechnicalAnalysis
                    price_df = TechnicalAnalysis.calculate_indicators(price_df)

                    for f in test_feats:
                        ml_res = await self._predict_custom(f.features, metadata)
                        if ml_res["prediction"] == "N/A": continue

                        direction = "LONG" if ml_res["prediction"] == "UP" else "SHORT"
                        prob = ml_res["metadata"]["calibrated_probability_up"]
                        calibrated_prob = CalibrationService.get_direction_probability(prob, direction)

                        # Apply SignalEngine filters
                        price = price_df.loc[f.date, "Close"] if f.date in price_df.index else 0
                        if isinstance(price, pd.Series): price = float(price.iloc[0])

                        ema200_col = [c for c in price_df.columns if c.upper() == "EMA_200"]
                        ema200 = price_df.loc[f.date, ema200_col[0]] if ema200_col and f.date in price_df.index else price
                        if isinstance(ema200, pd.Series): ema200 = float(ema200.iloc[0])
                        ema200 = float(ema200)

                        # Filters
                        if calibrated_prob < 0.52: continue
                        if direction == "LONG" and price < ema200: continue
                        if direction == "SHORT" and price > ema200: continue

                        # Resolution
                        sig = LiveSignal(
                            id=f"wf2_{w}_{symbol}_{f.date.strftime('%Y%m%d')}",
                            symbol=symbol,
                            timestamp=f.date,
                            entry_price=price,
                            target_price=price * (1.03 if direction == "LONG" else 0.97),
                            stop_loss_price=price * (0.97 if direction == "LONG" else 1.03),
                            direction=direction,
                            status="WAITING_FOR_ENTRY",
                            conviction=calibrated_prob * 100,
                            rating="BUY",
                            timeframe="SWING",
                            model_version=metadata.version,
                            provenance={"window": w+1, "type": "walk_forward_audit"}
                        )

                        future_df = price_df[price_df.index > f.date].head(20)
                        outcome = OutcomeEngine.evaluate_outcome(sig, future_df)

                        if outcome["status"] in ["TARGET_HIT", "STOP_LOSS"]:
                            sig.status = outcome["status"]
                            sig.profit_pct = outcome["profit_pct"]
                            sig.outcome_date = outcome["outcome_date"]
                            sig.outcome_price = outcome["outcome_price"]
                            sig.mfe = outcome["mfe"]
                            sig.mae = outcome["mae"]

                            # Save to database for certification audit
                            await container.ios_repo.save_live_signal(sig)

                            window_trades.append({
                                "status": outcome["status"],
                                "profit": outcome["profit_pct"],
                                "direction": direction
                            })

                except Exception as e:
                    print(f"      [ERROR] {symbol}: {e}")

            if window_trades:
                df_w = pd.DataFrame(window_trades)
                wr = float((df_w['status'] == 'TARGET_HIT').mean() * 100)
                avg_prof = float(df_w['profit'].mean())
                self.results.append({
                    "window": int(w+1),
                    "trades": int(len(df_w)),
                    "win_rate": wr,
                    "avg_profit": avg_prof,
                    "long_count": int((df_w['direction'] == 'LONG').sum()),
                    "short_count": int((df_w['direction'] == 'SHORT').sum())
                })
                print(f"   [RESULT] Window {w+1}: WR={wr:.1f}%, Profit={avg_prof:.2f}%, Trades={len(df_w)}")

        self._finalize()

    async def _predict_custom(self, features, metadata):
        import joblib
        model_path = os.path.join("backend/ml/registry", metadata.name)
        calib_path = os.path.join("backend/ml/registry", metadata.calibration_metadata["calibrator_file"])
        model = joblib.load(model_path)
        calibrator = joblib.load(calib_path)
        feature_names = metadata.hyperparameters["feature_names"]
        X_input = pd.DataFrame([features])[feature_names]
        # Fill missing features with 0
        X_input = X_input.fillna(0)
        raw_prob = model.predict_proba(X_input)[0][1]
        calibrated_prob = float(calibrator.predict_proba(np.array([[raw_prob]])) [0][1])
        prediction_label = "UP" if calibrated_prob > 0.55 else "DOWN" if calibrated_prob < 0.45 else "NEUTRAL"
        return {"prediction": prediction_label, "metadata": {"calibrated_probability_up": calibrated_prob}}

    def _finalize(self):
        os.makedirs("validation/walk_forward", exist_ok=True)
        res_df = pd.DataFrame(self.results)
        res_df.to_markdown("validation/walk_forward/WALK_FORWARD_V2.md")
        with open("validation/walk_forward/WALK_FORWARD_V2.json", "w") as f:
            json.dump(self.results, f, indent=4)

if __name__ == "__main__":
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "ITC", "BHARTIARTL", "KOTAKBANK", "LT"]
    validator = WalkForwardV2(symbols, windows=4)
    asyncio.run(validator.run())
