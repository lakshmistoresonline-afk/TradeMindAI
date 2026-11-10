"""
================================================================================
TradeMindAI: Smart Resumable Historical Data Ingestion (2015-01-01 to Present)
================================================================================
Fetches, validates, normalizes, and idempotently persists daily and 5-minute intraday
OHLCV market data for NIFTY 500 stocks from 2015-01-01 through current date.

Features:
- Smart Auto-Resume: Automatically skips symbols already ingested into DuckDB.
- Multi-Threaded ThreadPoolExecutor (10 Workers) for high performance.
- Dual-Store Persistence: DuckDB (analytical.duckdb) + Parquet (backend/data/features/).
- OHLC Geometry & Non-Negative Volume Validation.
- Concurrency-safe: Handles background DuckDB file locks gracefully.
================================================================================
"""

import os
import sys
import time
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

duckdb_path = root_dir / "backend" / "data" / "analytical.duckdb"
features_dir = root_dir / "backend" / "data" / "features"

os.makedirs(features_dir, exist_ok=True)
os.makedirs(root_dir / "backend" / "data", exist_ok=True)

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
    """Ensures analytical.duckdb tables exist with correct schemas."""
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
            ingested_at VARCHAR
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
            ingested_at VARCHAR
        );
    """)

def fetch_single_symbol_data(symbol: str, start_date: str, today_str: str, now_iso: str, include_intraday: bool = False) -> Dict[str, Any]:
    yf_ticker = get_yahoo_ticker(symbol)
    res = {
        "symbol": symbol,
        "daily_records": [],
        "intraday_records": [],
        "daily_df": None,
        "success_daily": False,
        "success_5m": False,
        "error": None
    }

    try:
        ticker = yf.Ticker(yf_ticker)

        # 1. Fetch Daily History (start_date to Present)
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

        # 2. Fetch Optional Intraday 5m History (~60d)
        if include_intraday:
            intraday_df = ticker.history(period="60d", interval="5m")
            if not intraday_df.empty:
                intraday_df.reset_index(inplace=True)
                ts_col = "Datetime" if "Datetime" in intraday_df.columns else "Date"
                intraday_df["timestamp"] = pd.to_datetime(intraday_df[ts_col]).dt.strftime("%Y-%m-%d %H:%M:%S")
                intraday_df = validate_ohlcv_dataframe(intraday_df)

                if not intraday_df.empty:
                    for _, row in intraday_df.iterrows():
                        res["intraday_records"].append((
                            symbol,
                            str(row["timestamp"]),
                            float(row["Open"]),
                            float(row["High"]),
                            float(row["Low"]),
                            float(row["Close"]),
                            float(row["Volume"]),
                            "YFINANCE_OPEN",
                            now_iso
                        ))
                    res["success_5m"] = True

    except Exception as ex:
        res["error"] = str(ex)

    return res

def run_historical_ingestion(start_date: str = "2015-01-01", batch_size: int = 500, max_workers: int = 10, include_intraday: bool = False, force: bool = False):
    all_syms = list(get_nifty_500_universe().keys())
    universe = all_syms[:batch_size]
    today_str = datetime.date.today().isoformat()
    now_iso = datetime.datetime.now(timezone.utc).isoformat()

    print("================================================================================")
    print(f"TradeMindAI: Smart Resumable Ingestion ({start_date} to {today_str})")
    print(f"Target Universe: {len(universe)} NIFTY 500 Stock Symbols | Workers: {max_workers}")
    print("================================================================================")

    # Inspect existing DuckDB database records safely using read_only connection
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
        # If stock already has >= 200 daily rows in DuckDB, skip it automatically
        if cnt >= 200 and not force:
            skipped_count += 1
        else:
            to_fetch.append(sym)

    print(f"[Auto-Resume Status] Already Ingested: {skipped_count} symbols | Remaining to Fetch: {len(to_fetch)} symbols")

    if not to_fetch:
        print("\nAll target symbols are ALREADY INGESTED in DuckDB!")
        print("================================================================================")
        return

    success_daily = skipped_count
    success_5m = 0
    failed_symbols = []

    start_time = time.time()

    # Open DuckDB connection for writing if available
    con = None
    try:
        con = duckdb.connect(str(duckdb_path))
        init_duckdb_schema(con)
    except Exception as lock_err:
        print(f"   [!] DuckDB write connection notice (Server running in background): {lock_err}")
        print("   [!] Ingestion will save Parquet feature files directly to backend/data/features/.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_symbol_data, sym, start_date, today_str, now_iso, include_intraday): sym for sym in to_fetch}

        for idx, future in enumerate(as_completed(futures), start=skipped_count + 1):
            symbol = futures[future]
            try:
                res = future.result()
                sym = res["symbol"]

                if res["success_daily"] and res["daily_records"]:
                    if con is not None:
                        try:
                            con.execute("DELETE FROM daily_ohlcv WHERE symbol = ? AND date >= ?", [sym, start_date])
                            con.executemany("""
                                INSERT INTO daily_ohlcv (symbol, date, open, high, low, close, volume, source, ingested_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            """, res["daily_records"])
                        except Exception as write_ex:
                            print(f"   [!] DuckDB write warning for {sym}: {write_ex}")

                    # Always save Parquet
                    if res["daily_df"] is not None:
                        parquet_file = features_dir / f"{sym}.parquet"
                        df_copy = res["daily_df"].copy()
                        df_copy["symbol"] = sym
                        df_copy["source"] = "YFINANCE_OPEN"
                        df_copy["ingested_at"] = now_iso
                        df_copy.to_parquet(parquet_file, index=False)

                    success_daily += 1

                if res["success_5m"] and res["intraday_records"]:
                    if con is not None:
                        try:
                            min_ts = min([r[1] for r in res["intraday_records"]])
                            con.execute("DELETE FROM intraday_5m_ohlcv WHERE symbol = ? AND timestamp >= ?", [sym, min_ts])
                            con.executemany("""
                                INSERT INTO intraday_5m_ohlcv (symbol, timestamp, open, high, low, close, volume, source, ingested_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            """, res["intraday_records"])
                        except Exception as write_ex:
                            print(f"   [!] DuckDB intraday write warning for {sym}: {write_ex}")

                    success_5m += 1

                print(f"[{idx}/{len(universe)}] Completed {sym} (Daily rows: {len(res['daily_records'])})")

            except Exception as ex:
                print(f"[{idx}/{len(universe)}] Exception for {symbol}: {ex}")
                failed_symbols.append({"symbol": symbol, "error": str(ex)})

    if con is not None:
        try:
            con.close()
        except Exception:
            pass

    elapsed = time.time() - start_time

    print("\n================================================================================")
    print("INGESTION COMPLETE SUMMARY")
    print(f"Total Universe Symbols: {len(universe)}")
    print(f"Previously Ingested Skipped: {skipped_count}")
    print(f"Newly Ingested: {len(to_fetch)}")
    print(f"Daily Historical Total: {success_daily}/{len(universe)}")
    print(f"Failed Symbols Count: {len(failed_symbols)}")
    print(f"Execution Duration: {round(elapsed, 2)} seconds")
    print("================================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest historical OHLCV data for NIFTY 500 stocks")
    parser.add_argument("--start-date", type=str, default="2015-01-01", help="Start date in YYYY-MM-DD format (default: 2015-01-01)")
    parser.add_argument("--batch-size", type=int, default=500, help="Number of symbols to ingest (default: 500)")
    parser.add_argument("--max-workers", type=int, default=10, help="Number of parallel worker threads (default: 10)")
    parser.add_argument("--include-intraday", action="store_true", help="Include 5m intraday history retrieval")
    parser.add_argument("--force", action="store_true", help="Force re-downloading existing stocks")
    args = parser.parse_args()

    run_historical_ingestion(start_date=args.start_date, batch_size=args.batch_size, max_workers=args.max_workers, include_intraday=args.include_intraday, force=args.force)
