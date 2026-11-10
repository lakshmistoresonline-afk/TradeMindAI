"""
================================================================================
TradeMindAI: Ultra-Fast Master NIFTY 500 Equity Signal Scan (500 Equities x 3 Horizons)
================================================================================
Evaluates all 500 NIFTY 500 stocks across SHORT, SWING, and LONG horizons (1,500 evaluations).
Uses pre-grouped batch OHLCV loading from analytical.duckdb for ultra-fast performance (<15s).
Calculates Strategy V2.2 ML predictions, regime analysis, probability calibration,
and risk parameters, persisting all qualifying BUY signals to the live operational ledger.
================================================================================
"""

import os
import sys
import time
import asyncio
import datetime
from datetime import timezone
from typing import Dict, Any, List
import duckdb
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.db.nifty500_symbols import get_nifty_500_universe
from backend.services.equity_signal_generation_service import DynamicFeatureVector
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_eligibility import is_eligible_buy
from backend.services.data_quality_service import duckdb_path

def build_all_symbol_feature_vectors(con: duckdb.DuckDBPyConnection, eval_time: datetime.datetime) -> Dict[str, List[DynamicFeatureVector]]:
    """
    Pre-groups and pre-calculates indicators for all 500 symbols in one high-performance batch pass.
    """
    print("[Master Scan] Loading 1.14M historical daily OHLCV rows from DuckDB...")
    t0 = time.time()
    df_all = con.execute("SELECT symbol, date as timestamp, open as Open, high as High, low as Low, close as Close, volume as Volume FROM daily_ohlcv ORDER BY symbol, date ASC").df()
    print(f"[Master Scan] Dataframe loaded ({len(df_all)} rows) in {round(time.time() - t0, 2)}s. Precomputing indicators...")

    feature_vectors = {}
    grouped = df_all.groupby("symbol")

    for symbol, df_group in grouped:
        if len(df_group) < 20:
            continue

        df = df_group.copy()
        df['Close'] = df['Close'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Open'] = df['Open'].astype(float)
        df['Volume'] = df['Volume'].astype(float)

        df['ema_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
        df['sma_20'] = df['Close'].rolling(window=20).mean()

        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean().fillna(df['Close'] * 0.02)

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df['RSI'] = (100 - (100 / (1 + rs))).fillna(50.0)

        last_row = df.iloc[-1]
        feats = {
            'Close': float(last_row['Close']),
            'close': float(last_row['Close']),
            'Open': float(last_row['Open']),
            'High': float(last_row['High']),
            'Low': float(last_row['Low']),
            'Volume': float(last_row['Volume']),
            'ema_20': float(last_row['ema_20']),
            'ema_50': float(last_row['ema_50']),
            'ema_200': float(last_row['ema_200']),
            'sma_20': float(last_row['sma_20']),
            'ATR': float(last_row['ATR'] if last_row['ATR'] > 0 else last_row['Close'] * 0.02),
            'RSI': float(last_row['RSI'])
        }
        feature_vectors[symbol] = [DynamicFeatureVector(eval_time, feats)]

    print(f"[Master Scan] Feature vectors ready for {len(feature_vectors)} symbols.")
    return feature_vectors

async def execute_full_nifty500_signal_scan():
    universe = list(get_nifty_500_universe().keys())
    horizons = ["SHORT", "SWING", "LONG"]
    start_time = datetime.datetime.now(timezone.utc)
    scan_id = f"scan_nifty500_{start_time.strftime('%Y%m%d_%H%M%S')}"

    print("================================================================================")
    print(f"TradeMindAI: Starting Fast Master NIFTY 500 Signal Scan ({scan_id})")
    print(f"Target Universe: {len(universe)} Equities | Horizons: {horizons}")
    print(f"Total Quantitative Evaluations: {len(universe) * len(horizons)}")
    print("================================================================================")

    # 1. Connect to DuckDB once (using read_only=True to prevent file locks)
    try:
        con = duckdb.connect(str(duckdb_path), read_only=True)
    except Exception as e:
        print(f"   [!] DuckDB connection notice: {e}")
        con = duckdb.connect(str(duckdb_path))

    feature_vectors = build_all_symbol_feature_vectors(con, start_time)
    con.close()

    funnel = {
        "scan_id": scan_id,
        "timestamp": start_time.isoformat(),
        "total_symbols": len(universe),
        "total_evaluations_attempted": 0,
        "candidate_buy_count": 0,
        "rejected_non_buy": 0,
        "signals_persisted": 0,
        "duplicates_prevented": 0,
        "persistence_failures": 0,
        "rejection_summary": {},
        "generated_signals": []
    }

    t0 = time.time()

    for horizon in horizons:
        print(f"\n--- Scanning Horizon: {horizon} ({len(universe)} symbols) ---")
        for idx, symbol in enumerate(universe, start=1):
            funnel["total_evaluations_attempted"] += 1
            try:
                fl = feature_vectors.get(symbol)
                if not fl:
                    reason = "INSUFFICIENT_HISTORICAL_DATA"
                    funnel["rejection_summary"][reason] = funnel["rejection_summary"].get(reason, 0) + 1
                    continue

                signal = await SignalEngine.generate_signal(
                    symbol=symbol,
                    asset_class="EQUITY",
                    timeframe=horizon,
                    features_list=fl,
                    evaluation_timestamp=start_time
                )

                if not signal:
                    reason = "NO_QUALIFYING_SETUP_OR_RISK_REJECTED"
                    funnel["rejection_summary"][reason] = funnel["rejection_summary"].get(reason, 0) + 1
                    continue

                if not is_eligible_buy(signal):
                    funnel["rejected_non_buy"] += 1
                    reason = "REJECTED_NON_BUY"
                    funnel["rejection_summary"][reason] = funnel["rejection_summary"].get(reason, 0) + 1
                    continue

                funnel["candidate_buy_count"] += 1

                ledger_res = await SignalLedgerService.persist_signal(signal)
                st = ledger_res.get("status")

                if st == "PERSISTED":
                    funnel["signals_persisted"] += 1
                    funnel["generated_signals"].append({
                        "id": signal.id,
                        "symbol": symbol,
                        "timeframe": horizon,
                        "rating": signal.rating,
                        "direction": signal.direction,
                        "entry_price": signal.entry_price,
                        "confidence": signal.confidence
                    })
                    print(f"   [+] PERSISTED BUY SIGNAL: {symbol} ({horizon}) | Entry: {signal.entry_price} | Rating: {signal.rating}")
                elif st == "DUPLICATE_PREVENTED":
                    funnel["duplicates_prevented"] += 1
                    print(f"   [=] Duplicate Prevented: {symbol} ({horizon}) - Active signal already exists")
                else:
                    funnel["persistence_failures"] += 1

            except Exception as ex:
                err_key = f"EXCEPTION: {ex}"
                funnel["rejection_summary"][err_key] = funnel["rejection_summary"].get(err_key, 0) + 1

    elapsed = time.time() - t0

    print("\n================================================================================")
    print("NIFTY 500 MASTER SIGNAL SCAN SUMMARY")
    print(f"Total Evaluations Attempted: {funnel['total_evaluations_attempted']}")
    print(f"Candidate BUY Setups Found: {funnel['candidate_buy_count']}")
    print(f"Newly Persisted Signals: {funnel['signals_persisted']}")
    print(f"Duplicates Prevented: {funnel['duplicates_prevented']}")
    print(f"Total Scan Duration: {round(elapsed, 2)} seconds")
    print("\nRejection Reason Breakdown:")
    for reason, count in funnel["rejection_summary"].items():
        print(f"   - {reason}: {count}")
    print("================================================================================")

    return funnel

if __name__ == "__main__":
    asyncio.run(execute_full_nifty500_signal_scan())
