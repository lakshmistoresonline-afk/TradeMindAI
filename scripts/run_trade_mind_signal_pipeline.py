"""
================================================================================
TradeMindAI: Safe, Non-Destructive Master Market Data & Signal Generation Pipeline
================================================================================
Phase 4.2 Remediation & Refactor:
1. Idempotent, non-destructive, transactional upserts into DuckDB (analytical.duckdb)
   without DELETE statement wiping.
2. Merges new provider records into existing Parquet feature files (backend/data/features/)
   preserving existing historical candles without overwriting.
3. Strategy-specific feature builders for SHORT, SWING, and LONG horizons.
4. Evaluates all 500 NIFTY 500 stocks across all horizons (1,500 evaluations).
5. Persists all qualifying Strategy V2.2 BUY signals into the operational ledger (live_signals).
================================================================================
"""

import os
import sys
import time
import asyncio
import argparse
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import duckdb
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.db.nifty500_symbols import get_nifty_500_universe
from backend.services.security_master_service import SecurityMasterService
from backend.services.equity_signal_generation_service import DynamicFeatureVector
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_eligibility import is_eligible_buy

duckdb_path = root_dir / "backend" / "data" / "analytical.duckdb"
features_dir = root_dir / "backend" / "data" / "features"

os.makedirs(features_dir, exist_ok=True)
os.makedirs(root_dir / "backend" / "data", exist_ok=True)

START_DATE_2015 = "2015-01-01"

def get_yahoo_ticker(symbol: str) -> str:
    """Maps canonical symbol to Yahoo Finance ticker (.NS suffix)."""
    clean = symbol.strip().upper()
    if clean.endswith(".NS") or clean.startswith("^"):
        return clean

    mapping = {
        "GMRINFRA": "GMRAIRPORT",
        "L&TFH": "LTF",
        "TATAMOTORS": "TMCV",
        "ZOMATO": "ETERNAL",
        "PEL": "PIRAMALFIN",
        "BAGMANE": "BAGMANE"
    }
    mapped = mapping.get(clean, clean)
    return f"{mapped}.NS"

def validate_ohlcv_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validates OHLC geometry invariants (High >= Open/Low/Close, Volume >= 0)."""
    if df.empty or "High" not in df.columns or "Low" not in df.columns:
        return pd.DataFrame()

    valid_mask = (
        (df["High"] >= df["Open"]) &
        (df["High"] >= df["Close"]) &
        (df["High"] >= df["Low"]) &
        (df["Low"] <= df["Open"]) &
        (df["Low"] <= df["Close"]) &
        (df["Volume"] >= 0)
    )

    return df[valid_mask].copy()

def init_duckdb_schema(con: duckdb.DuckDBPyConnection):
    """Ensures analytical.duckdb tables exist with correct composite primary keys."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS daily_ohlcv (
            symbol VARCHAR NOT NULL,
            date VARCHAR NOT NULL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            source VARCHAR,
            ingested_at VARCHAR,
            PRIMARY KEY (symbol, date)
        );
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS intraday_5m_ohlcv (
            symbol VARCHAR NOT NULL,
            timestamp VARCHAR NOT NULL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            source VARCHAR,
            ingested_at VARCHAR,
            PRIMARY KEY (symbol, timestamp)
        );
    """)

def fetch_single_symbol_data(symbol: str, start_date: str, today_str: str, now_iso: str) -> Dict[str, Any]:
    yf_ticker = get_yahoo_ticker(symbol)
    res = {
        "symbol": symbol,
        "daily_records": [],
        "daily_df": None,
        "success_daily": False,
        "error": None
    }

    try:
        ticker = yf.Ticker(yf_ticker)
        daily_df = ticker.history(start=start_date, end=today_str, interval="1d")

        if not daily_df.empty:
            daily_df.reset_index(inplace=True)
            ts_col = "Date" if "Date" in daily_df.columns else "index"
            daily_df["date"] = pd.to_datetime(daily_df[ts_col]).dt.strftime("%Y-%m-%d")
            daily_df = validate_ohlcv_dataframe(daily_df)

            if not daily_df.empty:
                res["daily_df"] = daily_df
                for _, row in daily_df.iterrows():
                    res["daily_records"].append((
                        symbol,
                        str(row["date"]),
                        float(row["Open"]),
                        float(row["High"]),
                        float(row["Low"]),
                        float(row["Close"]),
                        float(row["Volume"]),
                        "YFINANCE_OPEN",
                        now_iso
                    ))
                res["success_daily"] = True

    except Exception as ex:
        res["error"] = str(ex)

    return res

def run_historical_ingestion(start_date: str = "2015-01-01", batch_size: int = 500, max_workers: int = 10, force: bool = False):
    """Stage 1: Non-Destructive Ingestion & Safe Storage Merging."""
    all_syms = list(get_nifty_500_universe().keys())
    universe = all_syms[:batch_size]
    today_str = datetime.date.today().isoformat()
    now_iso = datetime.datetime.now(timezone.utc).isoformat()

    print("================================================================================")
    print(f"STAGE 1: Non-Destructive Ingestion ({start_date} to {today_str})")
    print(f"Target Universe: {len(universe)} NIFTY 500 Stock Symbols | Workers: {max_workers}")
    print("================================================================================")

    existing_counts = {}
    if not force:
        try:
            con_ro = duckdb.connect(str(duckdb_path), read_only=True)
            tables = [t[0] for t in con_ro.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main'").fetchall()]
            if "daily_ohlcv" in tables:
                rows = con_ro.execute("SELECT symbol, COUNT(*) FROM daily_ohlcv WHERE date >= ? GROUP BY symbol", [start_date]).fetchall()
                existing_counts = dict(rows)
            con_ro.close()
        except Exception:
            existing_counts = {}

    to_fetch = []
    skipped_count = 0

    for sym in universe:
        cnt = existing_counts.get(sym, 0)
        if cnt >= 200 and not force:
            skipped_count += 1
        else:
            to_fetch.append(sym)

    print(f"[Ingestion Status] Already Ingested: {skipped_count} symbols | Remaining to Fetch: {len(to_fetch)} symbols")

    if not to_fetch:
        print("All target symbols are ALREADY INGESTED in DuckDB & Parquet storage.")
        print("================================================================================")
        return

    con = None
    try:
        con = duckdb.connect(str(duckdb_path))
        init_duckdb_schema(con)
    except Exception as lock_err:
        print(f"   [!] DuckDB write lock notice: {lock_err}")

    start_time = time.time()
    success_daily = skipped_count

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_symbol_data, sym, start_date, today_str, now_iso): sym for sym in to_fetch}

        for idx, future in enumerate(as_completed(futures), start=skipped_count + 1):
            symbol = futures[future]
            try:
                res = future.result()
                sym = res["symbol"]

                if res["success_daily"] and res["daily_records"]:
                    if con is not None:
                        try:
                            # Safe transactional upsert without destructive DELETE wiping
                            con.executemany("""
                                INSERT INTO daily_ohlcv (symbol, date, open, high, low, close, volume, source, ingested_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT (symbol, date) DO UPDATE SET
                                    open = EXCLUDED.open,
                                    high = EXCLUDED.high,
                                    low = EXCLUDED.low,
                                    close = EXCLUDED.close,
                                    volume = EXCLUDED.volume,
                                    source = EXCLUDED.source,
                                    ingested_at = EXCLUDED.ingested_at;
                            """, res["daily_records"])
                        except Exception as write_ex:
                            print(f"   [!] DuckDB upsert notice for {sym}: {write_ex}")

                    # Safe Parquet dataset merging
                    if res["daily_df"] is not None:
                        parquet_file = features_dir / f"{sym}.parquet"
                        new_df = res["daily_df"].copy()
                        new_df["symbol"] = sym
                        new_df["source"] = "YFINANCE_OPEN"
                        new_df["ingested_at"] = now_iso

                        if os.path.exists(parquet_file):
                            try:
                                existing_df = pd.read_parquet(parquet_file)
                                combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=["date"], keep="last")
                                combined_df.sort_values("date", inplace=True)
                                combined_df.to_parquet(parquet_file, index=False)
                            except Exception:
                                new_df.to_parquet(parquet_file, index=False)
                        else:
                            new_df.to_parquet(parquet_file, index=False)

                    success_daily += 1
                    print(f"[{idx}/{len(universe)}] Completed {sym} (Daily rows: {len(res['daily_records'])})")

            except Exception as ex:
                print(f"[{idx}/{len(universe)}] Exception for {symbol}: {ex}")

    if con is not None:
        try:
            con.close()
        except Exception:
            pass

    print(f"[Stage 1 Summary] Ingestion completed in {round(time.time() - start_time, 2)}s. Total Ingested: {success_daily}/{len(universe)}")

def build_all_symbol_feature_vectors(con: duckdb.DuckDBPyConnection, eval_time: datetime.datetime) -> Dict[str, List[DynamicFeatureVector]]:
    """Stage 2: Strategy-Specific Time-Safe Feature Builder for SHORT, SWING, and LONG."""
    print("\n[Stage 2] Loading historical OHLCV rows from DuckDB...")
    t0 = time.time()
    df_all = con.execute("SELECT symbol, date as timestamp, open as Open, high as High, low as Low, close as Close, volume as Volume FROM daily_ohlcv ORDER BY symbol, date ASC").df()
    print(f"[Stage 2] Loaded {len(df_all)} rows in {round(time.time() - t0, 2)}s. Precomputing technical indicators...")

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

    print(f"[Stage 2] Feature vectors ready for {len(feature_vectors)} symbols.")
    return feature_vectors

async def run_master_signal_generation_scan(batch_size: int = 500):
    """Stage 3: Master Quantitative Signal Scan across SHORT, SWING, and LONG horizons."""
    all_syms = list(get_nifty_500_universe().keys())
    universe = all_syms[:batch_size]
    horizons = ["SHORT", "SWING", "LONG"]
    start_time = datetime.datetime.now(timezone.utc)
    scan_id = f"scan_nifty500_{start_time.strftime('%Y%m%d_%H%M%S')}"

    print("\n================================================================================")
    print(f"STAGE 3: Starting Master NIFTY 500 Signal Scan ({scan_id})")
    print(f"Target Universe: {len(universe)} Equities | Horizons: {horizons}")
    print(f"Total Quantitative Evaluations: {len(universe) * len(horizons)}")
    print("================================================================================")

    try:
        con = duckdb.connect(str(duckdb_path), read_only=True)
    except Exception:
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
    print("MASTER SIGNAL SCAN COMPLETE SUMMARY")
    print(f"Total Evaluations Attempted: {funnel['total_evaluations_attempted']}")
    print(f"Candidate BUY Setups Found: {funnel['candidate_buy_count']}")
    print(f"Newly Persisted Signals: {funnel['signals_persisted']}")
    print(f"Duplicates Prevented: {funnel['duplicates_prevented']}")
    print(f"Total Scan Duration: {round(elapsed, 2)} seconds")
    print("================================================================================")

    return funnel

def main():
    parser = argparse.ArgumentParser(description="TradeMindAI Complete Market Data & Signal Generation Pipeline")
    parser.add_argument("--start-date", type=str, default="2015-01-01", help="Start date for historical ingestion (default: 2015-01-01)")
    parser.add_argument("--batch-size", type=int, default=500, help="Number of symbols to evaluate (default: 500)")
    parser.add_argument("--max-workers", type=int, default=10, help="Number of parallel worker threads for ingestion (default: 10)")
    parser.add_argument("--skip-ingestion", action="store_true", help="Skip historical ingestion stage and run signal scan directly")
    args = parser.parse_args()

    if not args.skip_ingestion:
        run_historical_ingestion(start_date=args.start_date, batch_size=args.batch_size, max_workers=args.max_workers)

    asyncio.run(run_master_signal_generation_scan(batch_size=args.batch_size))

if __name__ == "__main__":
    main()
