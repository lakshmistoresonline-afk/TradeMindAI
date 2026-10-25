"""
================================================================================
TradeMindAI: Full Universe Nifty 500 Historical Signal Generation Engine
================================================================================
Iterates through 10 years of authentic daily price bars (2021 -> 2026) across
all 500 Nifty equities and generates/persists historical signals into ShadowSignalDB.
================================================================================
"""

import os
import sys
import datetime
import asyncio
import logging
import sqlite3
import pandas as pd

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.services.signal_engine import SignalEngine
from backend.services.signal_eligibility import is_eligible_buy
from backend.services.research_replay_service import ResearchReplayService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(base_dir, "backend", "local_operational.db")

async def run_historical_signal_generation():
    logger.info("=== Starting Full Universe Nifty 500 Historical Signal Generation Engine ===")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Query all active 500 Nifty stocks
    cursor.execute("SELECT DISTINCT symbol FROM stocks WHERE symbol IS NOT NULL AND trim(symbol) != '';")
    all_stocks = [r[0].strip() for r in cursor.fetchall()]
    conn.close()

    logger.info(f"Targeting ALL {len(all_stocks)} active Nifty equities for historical timeline replay...")

    total_historical_signals = 0

    for idx, sym in enumerate(all_stocks, 1):
        # Query historical price dates for symbol
        conn = sqlite3.connect(DB_PATH)
        df_dates = pd.read_sql_query(
            "SELECT date FROM historical_prices WHERE symbol = ? AND date >= '2021-01-01' ORDER BY date ASC;",
            conn, params=(sym,)
        )
        conn.close()

        if df_dates.empty:
            continue

        sym_signals = 0
        # Evaluate weekly sample steps across 5-year timeline
        eval_dates = df_dates["date"].tolist()[::5]  # Every 5th trading day (~weekly)

        for d_str in eval_dates:
            eval_dt = pd.to_datetime(d_str).to_pydatetime()
            if eval_dt.tzinfo is None:
                eval_dt = eval_dt.replace(tzinfo=datetime.timezone.utc)

            signal = await SignalEngine.generate_signal(
                symbol=sym,
                asset_class="EQUITY",
                timeframe="SWING",
                evaluation_timestamp=eval_dt
            )

            if signal and is_eligible_buy(signal):
                sym_signals += 1
                await ResearchReplayService._persist_research_signal(signal, "run_historical_nifty500_v22")
                logger.info(f"   [+] HISTORICAL BUY SIGNAL: {sym} on {eval_dt.strftime('%Y-%m-%d')} at ₹{signal.entry_price:.2f} (Prob: {signal.calibrated_probability:.2f})")

        total_historical_signals += sym_signals
        if sym_signals > 0:
            logger.info(f"[{idx}/{len(all_stocks)}] {sym}: Generated {sym_signals} historical BUY signals.")

    logger.info(f"=== Full Universe Historical Replay Complete! Generated {total_historical_signals} historical BUY signals across Nifty 500 timeline. ===")

if __name__ == "__main__":
    asyncio.run(run_historical_signal_generation())
