import sys
import os
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
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

async def audit_symbol(symbol: str):
    print(f"\n--- Realized Performance Audit: {symbol} ---")

    # 1. Fetch all features to identify the test set
    features = await container.data_platform_repo.get_features_by_range(
        symbol, datetime(2020, 1, 1), datetime(2026, 8, 14)
    )

    if len(features) < 300:
        print(f"[SKIP] {symbol} has insufficient features ({len(features)})")
        return None

    features.sort(key=lambda x: x.date)
    n = len(features)
    calib_end = int(n * 0.8)
    test_feats = features[calib_end:]

    # 2. Load Prices
    with container.repository.session_factory() as session:
        from backend.core.postgres import PriceDB
        prices = session.query(PriceDB).filter(PriceDB.symbol == symbol).order_by(PriceDB.date).all()
        if not prices:
            print(f"[ERROR] No prices for {symbol}")
            return None
        price_df = pd.DataFrame([{"date": p.date, "Open": p.open, "High": p.high, "Low": p.low, "Close": p.close} for p in prices])
        price_df.set_index('date', inplace=True)
        if price_df.index.tz is None:
            price_df.index = price_df.index.tz_localize(pytz.UTC)

    trades = []
    rejection_reasons = {}

    ml_service = container.ml_service

    # 3. Simulate Signal -> Outcome
    for f in test_feats:
        ref_date = f.date
        if ref_date.tzinfo is None:
            ref_date = pytz.UTC.localize(ref_date)

        ml_res = await ml_service.predict_with_champion(symbol, f.features)
        if ml_res.get("prediction") == "N/A": continue

        calibrated_prob_up = ml_res.get("metadata", {}).get("calibrated_probability_up", 0.5)

        try:
            curr_price = price_df.loc[ref_date]["Close"]
            if isinstance(curr_price, pd.Series): curr_price = curr_price.iloc[-1]
        except KeyError:
            continue

        atr = f.features.get("volatility_atr", curr_price * 0.02)
        direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"

        risk_params = RiskEngine.calculate_trade_parameters(symbol, curr_price, direction, atr)
        if not risk_params: continue

        # AUDIT DEFECT INVESTIGATION: Aligned Probability
        aligned_prob = calibrated_prob_up if direction == "LONG" else (1.0 - calibrated_prob_up)

        abs_reward = abs(risk_params["target"] - curr_price)
        abs_risk = abs(curr_price - risk_params["stop_loss"])

        ev = CalibrationService.calculate_expected_value(aligned_prob, abs_reward, abs_risk)

        # Rejection Filters
        reject = None
        if aligned_prob < 0.52: reject = "WEAK_EDGE"
        if not reject and ev <= 0: reject = "NEGATIVE_EXPECTANCY"
        if not reject and risk_params["risk_pct"] > 12: reject = "EXCESSIVE_VOLATILITY"

        if reject:
            rejection_reasons[reject] = rejection_reasons.get(reject, 0) + 1
            continue

        # construct signal
        sig = LiveSignal(
            id=f"audit_{symbol}_{ref_date.strftime('%Y%m%d')}",
            symbol=symbol, timestamp=ref_date, rating="BUY" if direction == "LONG" else "SELL",
            direction=direction, conviction=float(aligned_prob * 100),
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
            "date": ref_date,
            "direction": direction,
            "status": outcome['status'],
            "realized_r": realized_r,
            "win": outcome['status'] == "TARGET_HIT"
        })

    if not trades:
        print(f"   [INFO] No trades. Rejections: {rejection_reasons}")
        return {"symbol": symbol, "trades": 0, "rejections": rejection_reasons}

    df_t = pd.DataFrame(trades)
    completed = df_t[df_t['status'].isin(['TARGET_HIT', 'STOP_LOSS', 'EXPIRED'])]

    wr = completed['win'].mean() if not completed.empty else 0
    avg_r = completed['realized_r'].mean() if not completed.empty else 0

    print(f"   Signals: {len(trades)}, Completed: {len(completed)}, WR: {wr:.2%}, Avg R: {avg_r:.2f}")
    return {"symbol": symbol, "trades": len(completed), "win_rate": wr, "avg_r": avg_r, "rejections": rejection_reasons}

async def run():
    print("============================================================")
    print(" QUANTITATIVE AUDIT: REALIZED TRADE OUTCOMES (HYPOTHETICAL ALIGNED)")
    print("============================================================")

    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "ITC", "HINDUNILVR"]
    results = []
    for s in symbols:
        res = await audit_symbol(s)
        if res: results.append(res)

    if not results: return

    # Aggregate
    all_rejections = {}
    for r in results:
        for k, v in r.get("rejections", {}).items():
            all_rejections[k] = all_rejections.get(k, 0) + v

    total_trades = sum(r['trades'] for r in results if 'trades' in r)
    avg_wr = np.mean([r['win_rate'] for r in results if r.get('trades', 0) > 0])
    avg_r = np.mean([r['avg_r'] for r in results if r.get('trades', 0) > 0])

    print("\n--- AGGREGATE RESULTS ---")
    print(f"Total Trades: {total_trades}")
    print(f"Avg Win Rate: {avg_wr:.2%}")
    print(f"Avg Realized R: {avg_r:.2f}")
    print(f"Rejection Totals: {all_rejections}")

if __name__ == "__main__":
    asyncio.run(run())
