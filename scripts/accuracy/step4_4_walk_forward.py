import os
import sys
import asyncio
import pandas as pd
import numpy as np
import json
import joblib
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from tqdm import tqdm
import pytz
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from backend.services.risk_engine import RiskEngine
from backend.services.calibration_service import CalibrationService
from backend.domain.models.ios import LiveSignal
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

class WalkForwardEngine:
    def __init__(self, symbols: List[str], output_dir: str = "data/results/step4_4_2"):
        self.symbols = symbols
        self.results = []
        self.window_metadata = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.windows = [
            {"id": "W1", "train_end": "2021-06-01", "test_start": "2021-06-01", "test_end": "2022-06-01"},
            {"id": "W2", "train_end": "2022-06-01", "test_start": "2022-06-01", "test_end": "2023-06-01"},
            {"id": "W3", "train_end": "2023-06-01", "test_start": "2023-06-01", "test_end": "2024-06-01"},
            {"id": "W4", "train_end": "2024-06-01", "test_start": "2024-06-01", "test_end": "2025-06-01"},
            {"id": "W5", "train_end": "2025-06-01", "test_start": "2025-06-01", "test_end": "2026-08-01"}
        ]

    async def train_model(self, symbol: str, features: List[Any], train_end_dt: datetime, window_id: str):
        # Local training logic (mimics MLService but without registry persistence)
        df = pd.DataFrame([{"date": f.date, **f.features, "target": f.target} for f in features])
        df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
        df = df[df['date'] < train_end_dt.replace(tzinfo=None)].sort_values('date')

        for col in df.columns:
            if col != 'date': df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(inplace=True)

        if len(df) < 150: return None, None, None

        n = len(df)
        train_split = int(n * 0.75) # 75% train, 25% calibration

        X = df.drop(['target', 'date'], axis=1)
        y = df['target'].astype(int)
        feature_names = list(X.columns)

        X_train, y_train = X.iloc[:train_split], y.iloc[:train_split]
        X_calib, y_calib = X.iloc[train_split:], y.iloc[train_split:]

        model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=10, random_state=42, class_weight='balanced')
        model.fit(X_train, y_train)

        probs_calib = model.predict_proba(X_calib)[:, 1].reshape(-1, 1)
        calibrator = LogisticRegression(C=1e10)
        calibrator.fit(probs_calib, y_calib)

        # Record Metadata (Phase 6)
        self.window_metadata.append({
            "window_id": window_id,
            "symbol": symbol,
            "training_start": df['date'].min().isoformat(),
            "training_end": train_end_dt.isoformat(),
            "training_sample_count": len(X_train),
            "validation_sample_count": len(X_calib),
            "model_version": f"WF_{window_id}_{datetime.now().strftime('%Y%m%d')}"
        })

        return model, calibrator, feature_names

    async def run_symbol(self, symbol: str):
        # 1. Fetch ALL features for symbol
        features = await container.data_platform_repo.get_features_by_range(
            symbol, datetime(2017, 6, 1), datetime(2026, 8, 20)
        )
        if not features: return []

        # 2. Load Prices
        prices = await container.repository.get_recent_prices(symbol, limit=5000)
        price_df = pd.DataFrame([{"date": p.date, "Open": p.open, "High": p.high, "Low": p.low, "Close": p.close} for p in prices])
        price_df.set_index('date', inplace=True)
        price_df.index = pd.to_datetime(price_df.index).tz_localize(None)

        symbol_trades = []

        for win in self.windows:
            train_end = pd.to_datetime(win['train_end'])
            test_start = pd.to_datetime(win['test_start'])
            test_end = pd.to_datetime(win['test_end'])

            # Train model for this window
            model, calibrator, feature_names = await self.train_model(symbol, features, train_end, win['id'])
            if not model: continue

            # 3. Test on this window's segment
            test_feats = [f for f in features if test_start <= f.date.replace(tzinfo=None) < test_end]

            for f in test_feats:
                ref_date = f.date.replace(tzinfo=None)

                # Inference
                X_input = pd.DataFrame([f.features])[feature_names]
                raw_prob = model.predict_proba(X_input)[0][1]
                calibrated_prob = float(calibrator.predict_proba(np.array([[raw_prob]])) [0][1])

                # Rule v2.2 Threshold
                if calibrated_prob < 0.52: continue

                direction = "LONG" if calibrated_prob > 0.5 else "SHORT" # Simplified for WF

                try:
                    curr_price = price_df.loc[ref_date]["Close"]
                    if isinstance(curr_price, pd.Series): curr_price = curr_price.iloc[-1]
                except KeyError: continue

                # Target/Stop (3%/3% Rule)
                target = curr_price * (1.03 if direction == "LONG" else 0.97)
                stop = curr_price * (0.97 if direction == "LONG" else 1.03)

                sig = LiveSignal(
                    id=f"wf_{symbol}_{ref_date.strftime('%Y%m%d')}",
                    symbol=symbol, timestamp=ref_date, rating="BUY",
                    direction=direction, conviction=float(calibrated_prob * 100),
                    entry_price=curr_price, target_price=target, stop_loss_price=stop,
                    timeframe="SWING", status="WAITING_FOR_ENTRY"
                )

                # Evaluate via Patched OutcomeEngine (Step 4.1.1 logic)
                future_data = price_df[price_df.index > ref_date]
                outcome = OutcomeEngine.evaluate_outcome(sig, future_data)

                if outcome['status'] in ['TARGET_HIT', 'STOP_LOSS', 'EXPIRED']:
                    symbol_trades.append({
                        "symbol": symbol,
                        "signal_date": ref_date.isoformat(),
                        "direction": direction,
                        "probability": calibrated_prob,
                        "intended_entry": curr_price,
                        "actual_entry": outcome.get("actual_entry_price"),
                        "entry_execution_type": outcome.get("entry_execution_type"),
                        "target": target,
                        "stop": stop,
                        "exit": outcome.get("outcome_price"),
                        "outcome": outcome['status'],
                        "profit_pct": outcome.get("profit_pct", 0.0),
                        "bars_to_entry": outcome.get("bars_to_entry"),
                        "bars_in_position": outcome.get("bars_in_position"),
                        "window_id": win['id'],
                        "model_version": f"WF_{win['id']}_{datetime.now().strftime('%Y%m%d')}"
                    })

        return symbol_trades

    async def run(self):
        print(f"--- TRUE WALK-FORWARD START ({len(self.symbols)} symbols) ---")
        all_trades = []

        for symbol in tqdm(self.symbols):
            res = await self.run_symbol(symbol)
            all_trades.extend(res)

        print(f"\n[+] WF Complete. Total Trades: {len(all_trades)}")

        output = {
            "metadata": {
                "type": "walk_forward",
                "timestamp": datetime.now().isoformat(),
                "windows": self.windows
            },
            "results": all_trades
        }

        with open(self.output_dir / "walk_forward_trades.json", 'w') as f:
            json.dump(output, f, indent=4)

        pd.DataFrame(self.window_metadata).to_csv(self.output_dir / "walk_forward_windows.csv", index=False)
        print(f"Saved to {self.output_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Limit symbols")
    parser.add_argument("--start", type=int, default=0, help="Start index")
    args = parser.parse_args()

    symbols = NIFTY_200_CONSTITUENTS
    start = args.start
    end = (start + args.limit) if args.limit else len(symbols)
    symbols_to_run = symbols[start:end]

    engine = WalkForwardEngine(symbols_to_run)
    asyncio.run(engine.run())
