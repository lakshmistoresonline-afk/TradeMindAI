import sys
import os
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from backend.services.outcome_engine import OutcomeEngine
from backend.services.risk_engine import RiskEngine
from backend.services.calibration_service import CalibrationService
from backend.domain.models.ios import LiveSignal

async def audit_realized_performance(symbol: str):
    print(f"\n--- Realized Performance Audit: {symbol} ---")

    # 1. Fetch all features to identify the test set
    features = await container.data_platform_repo.get_features_by_range(
        symbol, datetime(2020, 1, 1), datetime(2026, 8, 14)
    )

    if len(features) < 300:
        print(f"[SKIP] {symbol} has insufficient features")
        return None

    features.sort(key=lambda x: x.date)
    n = len(features)
    calib_end = int(n * 0.8)
    test_feats = features[calib_end:]

    # We also need the actual price data for OutcomeEngine
    # We'll load it into a DataFrame
    with container.repository.session_factory() as session:
        from backend.core.postgres import PriceDB
        prices = session.query(PriceDB).filter(PriceDB.symbol == symbol).order_by(PriceDB.date).all()
        price_df = pd.DataFrame([{"date": p.date, "Open": p.open, "High": p.high, "Low": p.low, "Close": p.close} for p in prices])
        price_df.set_index('date', inplace=True)
        # Ensure it matches timezone if OutcomeEngine expects it
        import pytz
        if price_df.index.tz is None:
            price_df.index = price_df.index.tz_localize(pytz.UTC)

    trades = []
    total_signals_attempted = len(test_feats)
    signals_generated = 0
    rejection_reasons = {}

    ml_service = container.ml_service

    # Iterate through test set and simulate signal generation
    for f in test_feats:
        ref_date = f.date
        # Ensure ref_date is UTC
        if ref_date.tzinfo is None:
            ref_date = pytz.UTC.localize(ref_date)

        # Manually reproduce SignalEngine logic for this ref_date
        # 1. ML Predict
        ml_res = await ml_service.predict_with_champion(symbol, f.features)
        if ml_res.get("prediction") == "N/A": continue

        calibrated_prob = ml_res.get("metadata", {}).get("calibrated_probability_up", 0.5)
        raw_prob = ml_res.get("metadata", {}).get("raw_probability_up", 0.5)

        # 2. Risk Calculation
        # We need the price AT ref_date
        try:
            curr_price = price_df.loc[ref_date]["Close"]
            # If multiple prices for same date (unlikely in 1D), take last
            if isinstance(curr_price, pd.Series): curr_price = curr_price.iloc[-1]
        except KeyError:
            continue

        atr = f.features.get("volatility_atr", curr_price * 0.02)
        direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"

        risk_params = RiskEngine.calculate_trade_parameters(symbol, curr_price, direction, atr)
        if not risk_params: continue

        # 3. Expected Value
        reward_amt = risk_params["target"] - curr_price
        risk_amt = curr_price - risk_params["stop_loss"]
        expected_val = CalibrationService.calculate_expected_value(calibrated_prob, reward_amt, risk_amt)

        # 4. No-Trade Filters (Mirror SignalEngine)
        reject = None
        if calibrated_prob < 0.52 and direction == "LONG": reject = "WEAK_EDGE"
        if calibrated_prob > 0.48 and direction == "SHORT": reject = "WEAK_EDGE" # Simplified for audit
        if expected_val <= 0: reject = "NEGATIVE_EXPECTANCY"
        if risk_params["risk_pct"] > 12: reject = "EXCESSIVE_VOLATILITY"

        if reject:
            rejection_reasons[reject] = rejection_reasons.get(reject, 0) + 1
            continue

        signals_generated += 1

        # Construct Signal for OutcomeEngine
        sig = LiveSignal(
            id=f"audit_{symbol}_{ref_date.strftime('%Y%m%d')}",
            symbol=symbol,
            timestamp=ref_date,
            rating="BUY" if direction == "LONG" else "SELL",
            direction=direction,
            conviction=float(calibrated_prob * 100),
            entry_price=curr_price,
            target_price=risk_params["target"],
            stop_loss_price=risk_params["stop_loss"],
            timeframe="SWING",
            status="WAITING_FOR_ENTRY"
        )

        # 5. Outcome Evaluation
        # Only pass data AFTER ref_date
        future_data = price_df[price_df.index > ref_date]
        outcome = OutcomeEngine.evaluate_outcome(sig, future_data)

        # Calculate Realized R
        realized_r = 0
        if outcome['status'] in ['TARGET_HIT', 'STOP_LOSS', 'EXPIRED']:
            exit_price = outcome['outcome_price']
            if exit_price:
                entry = sig.entry_price
                stop = sig.stop_loss_price
                risk = abs(entry - stop)
                if risk > 0:
                    if direction == "LONG":
                        realized_r = (exit_price - entry) / risk
                    else:
                        realized_r = (entry - exit_price) / risk

        trades.append({
            "date": ref_date,
            "direction": direction,
            "prob": calibrated_prob,
            "ev": expected_val,
            "status": outcome['status'],
            "realized_r": realized_r
        })

    # Summary
    if not trades:
        print("   [INFO] No trades generated for this test period.")
        return {
            "symbol": symbol,
            "signals": signals_generated,
            "trades": 0,
            "rejections": rejection_reasons
        }

    df_trades = pd.DataFrame(trades)
    completed = df_trades[df_trades['status'].isin(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'])]

    win_rate = (completed['status'] == 'TARGET_HIT').mean() if not completed.empty else 0
    avg_r = completed['realized_r'].mean() if not completed.empty else 0
    profit_factor = abs(completed[completed['realized_r'] > 0]['realized_r'].sum() /
                       completed[completed['realized_r'] < 0]['realized_r'].sum()) if len(completed[completed['realized_r'] < 0]) > 0 else np.inf

    print(f"Signals Attempted: {total_signals_attempted}")
    print(f"Signals Generated: {signals_generated}")
    print(f"Completed Trades: {len(completed)}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Avg Realized R: {avg_r:.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Rejection Summary: {rejection_reasons}")

    return {
        "symbol": symbol,
        "signals": signals_generated,
        "trades": len(completed),
        "win_rate": win_rate,
        "avg_r": avg_r,
        "profit_factor": profit_factor,
        "rejections": rejection_reasons
    }

async def run_audit():
    print("============================================================")
    print(" STEP 2: REALIZED TRADE VALIDATION AUDIT")
    print("============================================================")

    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "ITC", "HINDUNILVR"]
    all_results = []

    for s in symbols:
        res = await audit_realized_performance(s)
        if res: all_results.append(res)

    if not all_results: return

    # Global aggregation
    total_trades = sum(r['trades'] for r in all_results)
    avg_win_rate = np.mean([r['win_rate'] for r in all_results if r['trades'] > 0])
    avg_expectancy = np.mean([r['avg_r'] for r in all_results if r['trades'] > 0])

    print("\n============================================================")
    print(" AGGREGATE REALIZED PERFORMANCE")
    print("============================================================")
    print(f"Total Trades: {total_trades}")
    print(f"Avg Win Rate: {avg_win_rate:.2%}")
    print(f"Avg Expectancy: {avg_expectancy:.2f}R")

if __name__ == "__main__":
    asyncio.run(run_audit())
