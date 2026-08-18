
import os
import sys
import json
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from backend.services.calibration_service import CalibrationService
from backend.domain.models.ios import LiveSignal
from backend.domain.models.data_platform import FeatureVector

class WalkForwardValidator:
    def __init__(self, symbols, windows=3):
        self.symbols = symbols
        self.windows = windows
        self.results = []

    async def run(self):
        print(f"--- WALK-FORWARD VALIDATION ({self.windows} windows) ---")

        # Define windows
        # Window 1: Train 2020-2023, Test 2024-01 to 2024-03
        # Window 2: Train 2020-2024-03, Test 2024-04 to 2024-06
        # etc.

        end_date = datetime.now()
        test_size_days = 90

        for w in range(self.windows):
            test_end = end_date - timedelta(days=w * test_size_days)
            test_start = test_end - timedelta(days=test_size_days)
            train_end = test_start - timedelta(days=1)

            print(f"\n[*] Window {w+1}: Train until {train_end.date()}, Test {test_start.date()} to {test_end.date()}")

            window_metrics = []

            for symbol in self.symbols:
                # 1. Prepare Data
                features = await container.data_platform_repo.get_features_by_range(
                    symbol, datetime(2020, 1, 1), test_end
                )
                if not features or len(features) < 200: continue

                # 2. Split
                train_feats = [f for f in features if f.date <= train_end]
                test_feats = [f for f in features if test_start <= f.date <= test_end]

                if len(train_feats) < 150 or not test_feats: continue

                # 3. Train Model (on train_feats)
                # We use MLService directly
                try:
                    metadata = await container.ml_service.train_and_register(f"{symbol}_wf_{w}", train_feats)

                    # 4. Test on test_feats
                    prices = await container.repository.get_recent_prices(symbol, limit=2000)
                    price_df = pd.DataFrame([p.model_dump() for p in prices])
                    price_df.set_index('date', inplace=True)
                    price_df.columns = [c.capitalize() for c in price_df.columns]

                    symbol_signals = []
                    predictions = []
                    for f in test_feats:
                        ml_res = await self._predict_custom(symbol, f.features, metadata)
                        if ml_res["prediction"] == "N/A": continue
                        predictions.append(ml_res["prediction"])

                        # Outcome resolution
                        entry_price = price_df.loc[f.date, "Close"] if f.date in price_df.index else 0
                        if isinstance(entry_price, pd.Series): entry_price = float(entry_price.iloc[0])
                        else: entry_price = float(entry_price)

                        if entry_price == 0: continue

                        sig = LiveSignal(
                            id=f"wf_{symbol}_{f.date.strftime('%Y%m%d')}",
                            symbol=symbol,
                            timestamp=f.date,
                            rating="BUY" if ml_res["prediction"] == "UP" else "SELL",
                            direction="LONG" if ml_res["prediction"] == "UP" else "SHORT",
                            conviction=float(ml_res["metadata"]["calibrated_probability_up"] * 100),
                            entry_price=entry_price,
                            target_price=0, stop_loss_price=0,
                            timeframe="SWING",
                            status="ACTIVE",
                            calibrated_probability=float(ml_res["metadata"]["calibrated_probability_up"])
                        )

                        # Set target/stop
                        direction = sig.direction
                        sig.target_price = sig.entry_price * (1.05 if direction == "LONG" else 0.95)
                        sig.stop_loss_price = sig.entry_price * (0.97 if direction == "LONG" else 1.03)

                        future_df = price_df[price_df.index > f.date].head(20)
                        outcome = OutcomeEngine.evaluate_outcome(sig, future_df)

                        symbol_signals.append(outcome["status"])

                    if symbol_signals:
                        wins = symbol_signals.count("TARGET_HIT")
                        losses = symbol_signals.count("STOP_LOSS")
                        total = wins + losses
                        wr = (wins / total * 100) if total > 0 else 0
                        window_metrics.append({
                            "symbol": symbol,
                            "win_rate": wr,
                            "trades": total,
                            "losses": losses,
                            "wins": wins,
                            "up_preds": predictions.count("UP"),
                            "down_preds": predictions.count("DOWN")
                        })

                except Exception as e:
                    print(f"      [ERROR] {symbol}: {e}")

            if window_metrics:
                avg_wr = sum([m["win_rate"] for m in window_metrics]) / len(window_metrics)
                total_trades = sum([m["trades"] for m in window_metrics])
                self.results.append({
                    "window": w+1,
                    "test_start": test_start.isoformat(),
                    "test_end": test_end.isoformat(),
                    "win_rate": avg_wr,
                    "total_trades": total_trades,
                    "details": window_metrics
                })
                print(f"   [RESULT] Window {w+1} Avg Win Rate: {avg_wr:.2f}% ({total_trades} trades)")

        self._save_results()

    async def _predict_custom(self, symbol, features, metadata):
        # Simplified manual prediction to avoid champion promotion overhead
        import joblib
        model_path = os.path.join("backend/ml/registry", metadata.name)
        calib_path = os.path.join("backend/ml/registry", metadata.calibration_metadata["calibrator_file"])

        model = joblib.load(model_path)
        calibrator = joblib.load(calib_path)

        feature_names = metadata.hyperparameters["feature_names"]
        X_input = pd.DataFrame([features])[feature_names]

        raw_prob = model.predict_proba(X_input)[0][1]
        calibrated_prob = float(calibrator.predict_proba(np.array([[raw_prob]])) [0][1])

        prediction_label = "UP" if calibrated_prob > 0.55 else "DOWN" if calibrated_prob < 0.45 else "NEUTRAL"

        return {
            "prediction": prediction_label,
            "metadata": {
                "raw_probability_up": raw_prob,
                "calibrated_probability_up": calibrated_prob
            }
        }

    def _save_results(self):
        os.makedirs("validation/walk_forward", exist_ok=True)
        with open("validation/walk_forward/WALK_FORWARD_RESULTS.json", "w") as f:
            json.dump(self.results, f, indent=4)

        with open("validation/walk_forward/WALK_FORWARD_REPORT.md", "w") as f:
            f.write("# Walk-Forward Validation Report\n\n")
            df = pd.DataFrame(self.results)
            f.write(df.to_markdown(index=False))

if __name__ == "__main__":
    validator = WalkForwardValidator(["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"], windows=2)
    asyncio.run(validator.run())
