import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from tqdm import tqdm
import pytz

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from backend.services.outcome_engine import OutcomeEngine
from backend.services.risk_engine import RiskEngine
from backend.services.calibration_service import CalibrationService
from backend.domain.models.ios import LiveSignal

REPORT_FILE = "docs/STEP4_FULL_REALIZED_BACKTEST_REPORT.md"

class RealizedBacktester:
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.results = []
        self.rejections = {}

    async def run_symbol_backtest(self, symbol: str):
        # 1. Fetch Features
        features = await container.data_platform_repo.get_features_by_range(
            symbol, datetime(2020, 1, 1), datetime(2026, 8, 17)
        )
        if len(features) < 300:
            return None

        features.sort(key=lambda x: x.date)

        # 2. Chronological Split
        n = len(features)
        train_end = int(n * 0.6)
        calib_end = int(n * 0.8)

        train_calib_feats = features[:calib_end]
        test_feats = features[calib_end:]

        # 3. Train & Calibrate (using existing production service)
        # This will save the champion model and its calibrator in the registry
        ml_service = container.ml_service
        try:
            metadata = await ml_service.train_and_register(symbol, train_calib_feats)
        except Exception as e:
            print(f"   [ERROR] Training failed for {symbol}: {e}")
            return None

        # 4. Load Prices for Outcome Evaluation
        with container.repository.session_factory() as session:
            from backend.core.postgres import PriceDB
            prices = session.query(PriceDB).filter(PriceDB.symbol == symbol).order_by(PriceDB.date).all()
            price_df = pd.DataFrame([{"date": p.date, "Open": p.open, "High": p.high, "Low": p.low, "Close": p.close} for p in prices])
            price_df.set_index('date', inplace=True)
            if price_df.index.tz is None:
                price_df.index = price_df.index.tz_localize(pytz.UTC)

        trades = []
        symbol_stats = {
            "symbol": symbol,
            "candidates_long": 0, "accepted_long": 0,
            "candidates_short": 0, "accepted_short": 0,
            "rejections": {}
        }

        # 5. Walk-Forward Test Loop
        for f in test_feats:
            ref_date = f.date
            if ref_date.tzinfo is None:
                ref_date = pytz.UTC.localize(ref_date)

            # Get Prediction
            res = await ml_service.predict_with_champion(symbol, f.features)
            if res.get("prediction") == "N/A": continue

            direction = "LONG" if res.get("prediction") == "UP" else "SHORT"
            if direction == "LONG": symbol_stats["candidates_long"] += 1
            else: symbol_stats["candidates_short"] += 1

            # Replicate SignalEngine logic
            prob_up = res.get("metadata", {}).get("calibrated_probability_up", 0.5)
            raw_prob_up = res.get("metadata", {}).get("raw_probability_up", 0.5)

            calibrated_prob = CalibrationService.get_direction_probability(prob_up, direction)
            raw_prob = CalibrationService.get_direction_probability(raw_prob_up, direction)

            try:
                curr_price = price_df.loc[ref_date]["Close"]
                if isinstance(curr_price, pd.Series): curr_price = curr_price.iloc[-1]
            except KeyError:
                continue

            atr = f.features.get("volatility_atr", curr_price * 0.02)
            risk_params = RiskEngine.calculate_trade_parameters(symbol, curr_price, direction, atr)
            if not risk_params: continue

            reward_amt = abs(risk_params["target"] - curr_price)
            risk_amt = abs(curr_price - risk_params["stop_loss"])
            ev = CalibrationService.calculate_expected_value(calibrated_prob, reward_amt, risk_amt)

            # Filters
            reject = None
            if reward_amt <= 0 or risk_amt <= 0: reject = "INVALID_GEOMETRY"
            elif calibrated_prob < 0.52: reject = "WEAK_EDGE"
            elif ev <= 0: reject = "NEGATIVE_EXPECTANCY"
            elif risk_params["risk_pct"] > 12: reject = "EXCESSIVE_VOLATILITY"

            if reject:
                symbol_stats["rejections"][reject] = symbol_stats["rejections"].get(reject, 0) + 1
                self.rejections[reject] = self.rejections.get(reject, 0) + 1
                continue

            if direction == "LONG": symbol_stats["accepted_long"] += 1
            else: symbol_stats["accepted_short"] += 1

            # 6. Evaluate Outcome
            sig = LiveSignal(
                id=f"bt_{symbol}_{ref_date.strftime('%Y%m%d')}",
                symbol=symbol, timestamp=ref_date, rating="BUY" if direction == "LONG" else "SELL",
                direction=direction, conviction=float(calibrated_prob * 100),
                entry_price=curr_price, target_price=risk_params["target"], stop_loss_price=risk_params["stop_loss"],
                timeframe="SWING", status="WAITING_FOR_ENTRY"
            )

            future_data = price_df[price_df.index > ref_date]
            outcome = OutcomeEngine.evaluate_outcome(sig, future_data)

            realized_r = 0
            if outcome['status'] in ['TARGET_HIT', 'STOP_LOSS', 'EXPIRED']:
                exit_price = outcome['outcome_price']
                if exit_price:
                    risk = abs(sig.entry_price - sig.stop_loss_price)
                    if risk > 0:
                        if direction == "LONG": realized_r = (exit_price - sig.entry_price) / risk
                        else: realized_r = (sig.entry_price - exit_price) / risk

            trades.append({
                "symbol": symbol,
                "date": ref_date,
                "direction": direction,
                "status": outcome['status'],
                "realized_r": realized_r,
                "prob": calibrated_prob,
                "win": 1 if outcome['status'] == "TARGET_HIT" else 0
            })

        return trades, symbol_stats

    async def run_all(self):
        print("============================================================")
        print(" TRADEMIND AI - FULL REALIZED WALK-FORWARD BACKTEST")
        print("============================================================")

        all_trades = []
        all_symbol_stats = []

        for s in tqdm(self.symbols, desc="Backtesting Symbols"):
            res = await self.run_symbol_backtest(s)
            if res:
                trades, stats = res
                all_trades.extend(trades)
                all_symbol_stats.append(stats)

        if not all_trades:
            print("[!] No trades generated.")
            return

        self.generate_report(all_trades, all_symbol_stats)

    def generate_report(self, trades: List[Dict], symbol_stats: List[Dict]):
        df = pd.DataFrame(trades)
        completed = df[df['status'].isin(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'])]

        # 1. Global Metrics
        total_signals = sum(s['candidates_long'] + s['candidates_short'] for s in symbol_stats)
        accepted_signals = len(df)
        completed_trades = len(completed)
        wins = completed[completed['status'] == 'TARGET_HIT']
        losses = completed[completed['status'] == 'STOP_LOSS']
        timeouts = completed[completed['status'] == 'EXPIRED']

        win_rate = len(wins) / completed_trades if completed_trades > 0 else 0
        avg_win_r = wins['realized_r'].mean() if not wins.empty else 0
        avg_loss_r = losses['realized_r'].mean() if not losses.empty else 0
        expectancy = completed['realized_r'].mean() if completed_trades > 0 else 0

        # Profit Factor
        gross_profit = wins['realized_r'].sum()
        gross_loss = abs(losses['realized_r'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

        # Drawdown (R-based)
        completed = completed.sort_values('date')
        completed['cum_r'] = completed['realized_r'].cumsum()
        completed['peak'] = completed['cum_r'].cummax()
        completed['drawdown'] = completed['cum_r'] - completed['peak']
        max_dd = completed['drawdown'].min()

        # 2. Confidence Buckets
        df['bucket'] = (df['prob'] // 0.05 * 5).astype(int)
        bucket_stats = df.groupby('bucket').agg({
            'win': ['count', 'mean'],
            'realized_r': 'mean'
        }).reset_index()

        # 3. Write Report
        with open(REPORT_FILE, "w") as f:
            f.write("# Step 4: Full Realized Walk-Forward Backtest Report\n\n")
            f.write(f"**Generated**: {datetime.utcnow()} UTC\n\n")

            f.write("## 1. Global Baseline Metrics\n\n")
            f.write(f"| Metric | Value | Note |\n")
            f.write(f"| :--- | :--- | :--- |\n")
            f.write(f"| Total Signals Attempted | {total_signals} | All test-period bars |\n")
            f.write(f"| Signals Accepted (Signal Accuracy) | {accepted_signals} ({accepted_signals/total_signals:.2%}) | Passed EV/Edge Gate |\n")
            f.write(f"| Completed Trades | {completed_trades} | Outcome reached |\n")
            f.write(f"| **Trade Win Rate** | **{win_rate:.2%}** | Target Hit / Total Completed |\n")
            f.write(f"| Avg Win R | {avg_win_r:.2f}R | Realized payoff |\n")
            f.write(f"| Avg Loss R | {avg_loss_r:.2f}R | Realized risk |\n")
            f.write(f"| **Realized Expectancy** | **{expectancy:.2f}R** | Per trade average |\n")
            f.write(f"| Profit Factor | {profit_factor:.2f} | Gross Win / Gross Loss |\n")
            f.write(f"| Max Drawdown | {max_dd:.2f}R | Peak-to-trough equity |\n")
            f.write(f"| Cumulative R | {completed['cum_r'].iloc[-1]:.2f}R | Total baseline return |\n\n")

            f.write("## 2. Directional Performance\n\n")
            for d in ['LONG', 'SHORT']:
                d_trades = completed[completed['direction'] == d]
                d_wr = d_trades['win'].mean() if not d_trades.empty else 0
                d_exp = d_trades['realized_r'].mean() if not d_trades.empty else 0
                f.write(f"### {d}\n")
                f.write(f"- Trades: {len(d_trades)}\n")
                f.write(f"- Win Rate: {d_wr:.2%}\n")
                f.write(f"- Expectancy: {d_exp:.2f}R\n\n")

            f.write("## 3. Confidence Calibration Analysis\n\n")
            f.write(bucket_stats.to_markdown())
            f.write("\n\n")

            f.write("## 4. Rejection Analysis\n\n")
            rejection_df = pd.DataFrame(list(self.rejections.items()), columns=['Reason', 'Count'])
            f.write(rejection_df.to_markdown(index=False))
            f.write("\n\n")

            f.write("## 5. Per-Symbol Baseline (Top 50 by Trades)\n\n")
            symbol_df = completed.groupby('symbol').agg({
                'win': ['count', 'mean'],
                'realized_r': 'mean'
            }).reset_index()
            symbol_df.columns = ['Symbol', 'Trades', 'Win Rate', 'Avg R']
            f.write(symbol_df.sort_values('Trades', ascending=False).head(50).to_markdown(index=False))

        print(f"\n[SUCCESS] Baseline backtest complete. Report: {REPORT_FILE}")

if __name__ == "__main__":
    from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
    # Run subset for faster audit if needed, or full for baseline.
    # Instruction says FULL.
    tester = RealizedBacktester(NIFTY_200_CONSTITUENTS)
    asyncio.run(tester.run_all())
