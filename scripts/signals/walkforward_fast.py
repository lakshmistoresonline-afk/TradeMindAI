"""
================================================================================
TradeMindAI: Time-Safe Walk-Forward Historical Signal Engine
================================================================================
Read-only, time-safe chronological walk-forward scan across Nifty 500 stocks.
Stores replay results in isolated output files without mutating operational LiveSignalDB.
================================================================================
"""

import os
import sys
import json
import datetime
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(base_dir)

from backend.core.postgres import DATABASE_URL, SessionLocal, StockDB, PriceDB, LiveSignalDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS, validate_nifty500_universe

def run_fast_walkforward(read_only: bool = True):
    print("================================================================================")
    print("  TRADEMIND AI: TIME-SAFE WALK-FORWARD SIGNAL REPLAY ENGINE")
    print("================================================================================\n")

    validate_nifty500_universe(NIFTY_500_SYMBOLS)
    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

    with SessionLocal() as session:
        if not read_only:
            print("[SAFETY NOTICE] Read-only set to False. Operational signals will be backed up.")

        start_date = datetime(2015, 1, 1)
        today_baseline = datetime(2026, 10, 17)

        print("[*] Reading historical prices into DataFrame...")
        query = "SELECT symbol, date, open, high, low, close, volume FROM historical_prices WHERE date >= '2015-01-01' ORDER BY symbol, date ASC"
        df_prices = pd.read_sql_query(query, con=engine)
        if df_prices.empty:
            print("[WARN] No historical prices found in PriceDB.")
            return

        df_prices['date'] = pd.to_datetime(df_prices['date'])
        print(f"   [+] Loaded {len(df_prices)} price bars across all stocks.")

        history_records = []
        active_signals = []
        active_symbols_set = set()
        sig_counter = 1

        symbols_grouped = df_prices.groupby('symbol')
        print(f"[*] Executing walk-forward signal detection across {len(symbols_grouped)} symbols...")

        for sym, group in symbols_grouped:
            if len(group) < 30:
                continue

            group = group.copy().reset_index(drop=True)
            interval = 40
            for i in range(30, len(group), interval):
                row = group.iloc[i]
                entry_dt = row['date']
                entry_p = float(row['close'])

                if entry_p <= 5.0 or row['volume'] < 1000:
                    continue

                target_p = round(entry_p * 1.08, 2)
                stop_p = round(entry_p * 0.95, 2)

                future_group = group.iloc[i+1 : i+21]

                if len(future_group) == 0 or entry_dt >= today_baseline - timedelta(days=25):
                    if sym not in active_symbols_set and len(active_signals) < 500:
                        sig_id = f"live_wf_{sym}"
                        rr_ratio = round((target_p - entry_p) / (entry_p - stop_p), 2) if entry_p > stop_p else 1.6
                        active_signals.append({
                            "id": sig_id,
                            "symbol": sym,
                            "asset_class": "EQUITY",
                            "timeframe": "SWING",
                            "direction": "LONG",
                            "rating": "BUY",
                            "entry_price": entry_p,
                            "current_price": entry_p,
                            "target_price": target_p,
                            "stop_price": stop_p,
                            "status": "ACTIVE",
                            "risk_reward_ratio": rr_ratio,
                            "timestamp": entry_dt,
                            "created_at": entry_dt,
                            "universe_version": "NIFTY_500_CANONICAL"
                        })
                        active_symbols_set.add(sym)
                    continue

                status = "EXPIRED"
                exit_p = float(future_group.iloc[-1]['close'])
                net_pnl = round(((exit_p - entry_p) / entry_p) * 100, 2)
                outcome_dt = future_group.iloc[-1]['date']

                for _, f_row in future_group.iterrows():
                    if f_row['high'] >= target_p:
                        status = "TARGET_HIT"
                        exit_p = target_p
                        net_pnl = 8.0
                        outcome_dt = f_row['date']
                        break
                    elif f_row['low'] <= stop_p:
                        status = "STOP_LOSS"
                        exit_p = stop_p
                        net_pnl = -5.0
                        outcome_dt = f_row['date']
                        break

                sig_id = f"sig_wf_{sig_counter:06d}"
                sig_counter += 1

                record = {
                    "id": sig_id,
                    "symbol": sym,
                    "asset_class": "EQUITY",
                    "timeframe": "SWING",
                    "direction": "LONG",
                    "rating": "BUY",
                    "entry_price": entry_p,
                    "current_price": exit_p,
                    "exit_price": exit_p,
                    "target_price": target_p,
                    "stop_price": stop_p,
                    "net_pnl": net_pnl,
                    "status": status,
                    "outcome_verified": False,
                    "evaluation_mode": "READ_ONLY_REPLAY",
                    "created_at": entry_dt.isoformat(),
                    "signal_timestamp": entry_dt.isoformat(),
                    "outcome_timestamp": outcome_dt.isoformat(),
                    "universe_version": "NIFTY_500_CANONICAL"
                }

                if outcome_dt <= today_baseline:
                    history_records.append(record)

        print(f"   [+] Walk-forward completed: {len(history_records)} historical closed signals, {len(active_signals)} open signals.")

        history_export = {
            "dataset_type": "NIFTY_500_WALKFORWARD_ARCHIVE",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_records": len(history_records),
            "records": history_records
        }

        os.makedirs("reports", exist_ok=True)
        with open("reports/walkforward_replay_results.json", "w", encoding="utf-8") as f:
            json.dump(history_export, f, indent=2)

        print("[SUCCESS] Walk-forward signal replay completed successfully (read-only mode preserved).")

if __name__ == "__main__":
    run_fast_walkforward(read_only=True)
