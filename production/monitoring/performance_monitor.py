
import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import text
from dotenv import load_dotenv
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import engine

async def detect_market_regime():
    # Detect regime using NIFTY index
    try:
        prices = await container.repository.get_recent_prices("^NSEI", limit=250)
        if not prices: return "UNKNOWN"

        df = pd.DataFrame([p.model_dump() for p in prices])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)

        close = df['close'].iloc[-1]
        ema200 = df['close'].ewm(span=200).mean().iloc[-1]
        vol = df['close'].pct_change().std() * np.sqrt(252)

        trend = "BULLISH" if close > ema200 else "BEARISH"
        volatility = "HIGH_VOL" if vol > 0.20 else "LOW_VOL"

        return f"{trend}_{volatility}"
    except:
        return "STABLE"

async def monitor_drift():
    print("--- PRODUCTION DRIFT MONITORING ---")

    # 1. Baseline
    BASELINE_PROB = 0.587
    BASELINE_WR = 58.77
    BASELINE_EV = 0.3262

    # 2. Fetch Shadow Data
    with engine.connect() as conn:
        # Prob Drift
        csv_path = "validation/shadow/shadow_observations.csv"
        if os.path.exists(csv_path):
            obs_df = pd.read_csv(csv_path)
            current_probs = obs_df['calibrated_probability'].dropna()
            mean_prob = float(current_probs.mean()) if not current_probs.empty else BASELINE_PROB
        else:
            mean_prob = BASELINE_PROB

        # Outcome Drift
        query = text("SELECT status, net_return FROM shadow_signals WHERE status != 'ACTIVE'")
        perf_df = pd.read_sql(query, conn)

    regime = await detect_market_regime()
    print(f"Current Regime: {regime}")

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "regime": regime,
        "probability": {
            "baseline": BASELINE_PROB,
            "current": round(mean_prob, 4),
            "drift": round(mean_prob - BASELINE_PROB, 4)
        },
        "performance": {
            "baseline_wr": BASELINE_WR,
            "baseline_ev": BASELINE_EV,
            "current_wr": 0.0,
            "current_ev": 0.0,
            "trades": 0
        },
        "status": "STABLE"
    }

    if not perf_df.empty:
        resolved = perf_df[perf_df['status'].isin(['TARGET_HIT', 'STOP_LOSS'])]
        if not resolved.empty:
            live_wr = (resolved['status'] == 'TARGET_HIT').mean() * 100
            live_ev = resolved['net_return'].mean()
            report["performance"]["current_wr"] = round(float(live_wr), 2)
            report["performance"]["current_ev"] = round(float(live_ev), 4)
            report["performance"]["trades"] = len(resolved)

            # Milestone Gate for Drift Conclusion
            if len(resolved) < 20:
                report["status"] = "INSUFFICIENT_SAMPLE_FOR_DRIFT_CONCLUSION"
            elif abs(live_wr - BASELINE_WR) > 15: # Critical WR threshold
                report["status"] = "DRIFT_DETECTED"

    os.makedirs("production/monitoring", exist_ok=True)
    with open("production/monitoring/DRIFT_REPORT.json", "w") as f:
        json.dump(report, f, indent=4)

    print(f"Drift Status: {report['status']} (Prob Drift: {report['probability']['drift']})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(monitor_drift())
