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
    # 1. Fetch all features to identify the test set
    features = await container.data_platform_repo.get_features_by_range(
        symbol, datetime(2020, 1, 1), datetime(2026, 8, 14)
    )

    if len(features) < 300: return None
    features.sort(key=lambda x: x.date)
    test_feats = features[int(len(features) * 0.8):]

    # 2. Load Prices
    with container.repository.session_factory() as session:
        from backend.core.postgres import PriceDB
        prices = session.query(PriceDB).filter(PriceDB.symbol == symbol).order_by(PriceDB.date).all()
        if not prices: return None
        price_df = pd.DataFrame([{"date": p.date, "Open": p.open, "High": p.high, "Low": p.low, "Close": p.close} for p in prices])
        price_df.set_index('date', inplace=True)
        if price_df.index.tz is None: price_df.index = price_df.index.tz_localize(pytz.UTC)

    trades = []
    ml_service = container.ml_service

    for f in test_feats:
        ref_date = f.date
        if ref_date.tzinfo is None: ref_date = pytz.UTC.localize(ref_date)

        ml_res = await ml_service.predict_with_champion(symbol, f.features)
        if ml_res.get("prediction") == "N/A": continue

        calibrated_prob_up = ml_res.get("metadata", {}).get("calibrated_probability_up", 0.5)

        try:
            curr_price = price_df.loc[ref_date]["Close"]
            if isinstance(curr_price, pd.Series): curr_price = curr_price.iloc[-1]
        except KeyError: continue

        atr = f.features.get("volatility_atr", curr_price * 0.02)
        direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
        risk_params = RiskEngine.calculate_trade_parameters(symbol, curr_price, direction, atr)
        if not risk_params: continue

        # BROKEN LOGIC: Always use prob_up
        reward_amt = risk_params["target"] - curr_price
        risk_amt = curr_price - risk_params["stop_loss"]
        ev = CalibrationService.calculate_expected_value(calibrated_prob_up, reward_amt, risk_amt)

        # BROKEN FILTER: Always check if prob_up < 0.52 for EDGE
        if calibrated_prob_up < 0.52: continue
        if ev <= 0: continue

        # construct signal
        sig = LiveSignal(
            id=f"audit_{symbol}_{ref_date.strftime('%Y%m%d')}",
            symbol=symbol, timestamp=ref_date, rating="BUY" if direction == "LONG" else "SELL",
            direction=direction, conviction=float(calibrated_prob_up * 100),
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

        trades.append({"status": outcome['status'], "realized_r": realized_r, "win": outcome['status'] == "TARGET_HIT"})

    if not trades: return {"symbol": symbol, "trades": 0}
    df_t = pd.DataFrame(trades)
    return {"symbol": symbol, "trades": len(df_t), "win_rate": df_t['win'].mean(), "avg_r": df_t['realized_r'].mean()}

async def run():
    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "ITC", "HINDUNILVR"]
    results = []
    for s in symbols:
        res = await audit_symbol(s)
        if res: results.append(res)

    if not results: return
    total_trades = sum(r['trades'] for r in results)
    avg_wr = np.mean([r['win_rate'] for r in results if r['trades'] > 0])
    avg_r = np.mean([r['avg_r'] for r in results if r['trades'] > 0])
    print(f"Broken Total Trades: {total_trades}")
    print(f"Broken Avg Win Rate: {avg_wr:.2%}")
    print(f"Broken Avg Realized R: {avg_r:.2f}")

if __name__ == "__main__":
    asyncio.run(run())
