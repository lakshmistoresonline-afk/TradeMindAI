"""
================================================================================
TradeMindAI: Master Nifty 500 Historical Data Ingestion Pipeline (v3.5-GEOM-FILTER)
================================================================================
Fetches, normalizes, validates, and idempotently persists 10-year daily OHLCV data
(2015-01-01 through current date) across all 500 canonical Nifty equities.
Enforces crash-safe dual-store persistence via durable transaction journal
with transaction-specific source tags, value-level readback verification,
destination path resolution integrity, date-keyed DuckDB upserts, and atomic Parquet promotion.
================================================================================
"""

import os
import sys
import json
import time
import argparse
import duckdb
import hashlib
import tempfile
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime, timezone

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.db.nifty500_symbols import get_nifty_500_universe

features_dir = root_dir / "backend" / "data" / "features"
features_dir.mkdir(parents=True, exist_ok=True)

duckdb_path = root_dir / "backend" / "data" / "analytical.duckdb"
checkpoint_path = root_dir / "backend" / "data" / "ingestion_checkpoint.json"
journal_path = root_dir / "backend" / "data" / "ingestion_journal.json"

ALLOWED_JOURNAL_STATUSES = {"PENDING_DUCKDB", "COMMITTED_DUCKDB", "COMPLETED", "FAILED"}

SYMBOL_ALIAS_MAP = {
    "L&TFH": "LTF.NS",
    "M&M": "M&M.NS",
    "M&MFIN": "M&MFIN.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "L&T": "LT.NS",
    "TATAMOTORS-DVR": "TATAMTRDVR.NS"
}

POST_2015_LISTING_DATES = {
    "LICI": "2022-05-17",
    "ATGL": "2018-11-05",
    "NYKAA": "2021-11-10",
    "PAYTM": "2021-11-18",
    "POLICYBZR": "2021-11-15",
    "DELHIVERY": "2022-05-24",
    "AWL": "2022-02-08",
    "IRFC": "2021-01-29",
    "RVNL": "2019-04-11",
    "MAZDOCK": "2020-10-12",
    "ZOMATO": "2021-07-23",
    "SWIGGY": "2024-11-13",
    "HYUNDAI": "2024-10-22",
    "BAJAJHFL": "2024-09-16"
}

def get_provider_ticker(canonical_symbol: str) -> str:
    if canonical_symbol in SYMBOL_ALIAS_MAP:
        return SYMBOL_ALIAS_MAP[canonical_symbol]
    return f"{canonical_symbol}.NS"

def init_duckdb():
    con = duckdb.connect(str(duckdb_path))
    con.execute("""
        CREATE TABLE IF NOT EXISTS daily_ohlcv (
            symbol VARCHAR,
            date VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            source VARCHAR,
            ingested_at VARCHAR,
            PRIMARY KEY (symbol, date)
        )
    """)
    con.close()

def load_journal(j_path: Path = None) -> dict:
    target = j_path or journal_path
    if target.exists():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise RuntimeError(f"Journal at '{target}' is not a JSON object dictionary")
            return data
        except Exception as ex:
            raise RuntimeError(f"Corrupt or malformed journal file at '{target}': {ex}") from ex
    return {}

def save_journal(journal: dict, j_path: Path = None):
    target = j_path or journal_path
    parent_dir = target.parent
    parent_dir.mkdir(parents=True, exist_ok=True)
    fd, temp_j = tempfile.mkstemp(dir=str(parent_dir), suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(journal, indent=2))
    os.replace(temp_j, str(target))

def recover_pending_transactions(custom_journal_path: Path = None, custom_feat_dir: Path = None, custom_db_path: Path = None) -> int:
    j_path = custom_journal_path or journal_path
    f_dir = custom_feat_dir or features_dir
    db_p = custom_db_path or duckdb_path

    if not j_path.exists():
        return 0

    journal = load_journal(j_path)
    symbols = list(journal.keys())

    # Validate top-level journal object and all entry fields BEFORE database queries or filesystem changes
    for sym in symbols:
        entry = journal.get(sym)
        if not isinstance(entry, dict):
            raise RuntimeError(f"Malformed non-dictionary journal entry for symbol '{sym}' in journal '{j_path}'")
        status = entry.get("status")
        tx_id = entry.get("tx_id")
        staged_p = entry.get("staged_parquet_path")
        target_p = entry.get("target_parquet_path")
        expected_p = f_dir / f"{sym}.parquet"

        if not status or not isinstance(status, str) or status not in ALLOWED_JOURNAL_STATUSES:
            raise RuntimeError(f"Journal entry for symbol '{sym}' contains invalid status '{status}'")
        if status not in ["COMPLETED", "FAILED"] and (not tx_id or not isinstance(tx_id, str)):
            raise RuntimeError(f"Malformed journal entry for symbol '{sym}': missing or non-string 'tx_id'")
        if status not in ["COMPLETED", "FAILED"] and (not staged_p or not target_p):
            raise RuntimeError(f"Malformed journal entry for symbol '{sym}': missing required path fields")
        if status not in ["COMPLETED", "FAILED"] and target_p:
            resolved_target = Path(target_p).resolve()
            resolved_expected = expected_p.resolve()
            if resolved_target != resolved_expected:
                raise RuntimeError(f"Target Parquet path mismatch for symbol '{sym}': expected '{resolved_expected}', got '{resolved_target}'")

    # Check if there are non-completed entries
    pending_symbols = [s for s in symbols if isinstance(journal.get(s), dict) and journal.get(s, {}).get("status") not in ["COMPLETED", "FAILED"]]
    if not pending_symbols:
        return 0

    # Require DuckDB database to exist and be accessible if non-completed transactions exist
    if not db_p or not db_p.exists():
        raise RuntimeError(f"DuckDB database missing or unavailable at '{db_p}' for transaction recovery")

    try:
        con = duckdb.connect(str(db_p))
    except Exception as ex:
        raise RuntimeError(f"Failed to connect to DuckDB database at '{db_p}': {ex}") from ex

    recovered_count = 0

    for sym in pending_symbols:
        entry = journal.get(sym)
        status = entry.get("status")
        staged_p = entry.get("staged_parquet_path")
        tx_id = entry.get("tx_id")
        final_p = f_dir / f"{sym}.parquet"

        # Verify DuckDB for transaction-specific TX_ tag
        df_duck_tx = pd.DataFrame()
        try:
            df_duck_tx = con.execute("""
                SELECT date, open as Open, high as High, low as Low, close as Close, volume as Volume
                FROM daily_ohlcv WHERE symbol = ? AND source = ?
                ORDER BY date
            """, [sym, f"TX_{tx_id}"]).df()
        except Exception as ex:
            con.close()
            raise RuntimeError(f"DuckDB transaction verification query failed for symbol '{sym}': {ex}") from ex

        duck_tx_match = len(df_duck_tx) > 0

        if duck_tx_match:
            if not staged_p or not os.path.exists(staged_p):
                if final_p.exists():
                    # Value-level verification of final Parquet store against DuckDB transaction rows
                    try:
                        df_final = pd.read_parquet(final_p)
                        df_final["date"] = pd.to_datetime(df_final["date"]).dt.strftime("%Y-%m-%d")

                        # Verify required columns exist
                        req_cols = ["date", "Open", "High", "Low", "Close", "Volume"]
                        if not all(col in df_final.columns for col in req_cols):
                            con.close()
                            raise RuntimeError(f"Final Parquet file '{final_p}' missing required OHLCV columns for symbol '{sym}'")

                        # Verify non-finite values (NaN / Inf)
                        if df_final[req_cols[1:]].isna().any().any() or np.isinf(df_final[req_cols[1:]].to_numpy()).any():
                            con.close()
                            raise RuntimeError(f"Final Parquet file '{final_p}' contains NaN or infinite values for symbol '{sym}'")

                        # Verify dates match DuckDB transaction dates
                        if not set(df_duck_tx["date"]).issubset(set(df_final["date"])):
                            con.close()
                            raise RuntimeError(f"Final Parquet file '{final_p}' missing committed DuckDB transaction dates for symbol '{sym}'")

                        # Element-wise comparison on transaction dates
                        common_dates = sorted(list(set(df_duck_tx["date"])))
                        p_sub = df_final.set_index("date").loc[common_dates][["Open", "High", "Low", "Close", "Volume"]]
                        d_sub = df_duck_tx.set_index("date").loc[common_dates][["Open", "High", "Low", "Close", "Volume"]]

                        val_diff = (
                            ((p_sub["Open"] - d_sub["Open"]).abs() > 1e-4) |
                            ((p_sub["High"] - d_sub["High"]).abs() > 1e-4) |
                            ((p_sub["Low"] - d_sub["Low"]).abs() > 1e-4) |
                            ((p_sub["Close"] - d_sub["Close"]).abs() > 1e-4) |
                            ((p_sub["Volume"] - d_sub["Volume"]).abs() > 1e-4)
                        ).sum()

                        if val_diff > 0:
                            con.close()
                            raise RuntimeError(f"Final Parquet file '{final_p}' element-wise value mismatch with committed DuckDB transaction for symbol '{sym}' ({val_diff} mismatches)")
                    except Exception as ex:
                        if con:
                            con.close()
                        raise RuntimeError(f"Final Parquet file verification failed for symbol '{sym}': {ex}") from ex

                    entry["status"] = "COMPLETED"
                    entry["recovered_at"] = datetime.now(timezone.utc).isoformat()
                    continue
                con.close()
                raise RuntimeError(f"Missing required staged Parquet file for committed symbol '{sym}': {staged_p}")

            # Value-level readback verification between staged Parquet file and DuckDB transaction rows
            try:
                df_staged = pd.read_parquet(staged_p)
                df_staged["date"] = pd.to_datetime(df_staged["date"]).dt.strftime("%Y-%m-%d")

                # Verify matching row counts and dates
                if len(df_staged) != len(df_duck_tx) or set(df_staged["date"]) != set(df_duck_tx["date"]):
                    con.close()
                    raise RuntimeError(f"Value-level readback mismatch for symbol '{sym}': row counts or date sets differ between staged Parquet and DuckDB transaction")

                # Element-wise price comparison across common dates
                df_staged_sub = df_staged.set_index("date")[["Open", "High", "Low", "Close", "Volume"]]
                df_duck_sub = df_duck_tx.set_index("date")[["Open", "High", "Low", "Close", "Volume"]]
                common_dates = sorted(list(set(df_staged["date"])))

                p_sub = df_staged_sub.loc[common_dates]
                d_sub = df_duck_sub.loc[common_dates]

                val_diff = (
                    ((p_sub["Open"] - d_sub["Open"]).abs() > 1e-4) |
                    ((p_sub["High"] - d_sub["High"]).abs() > 1e-4) |
                    ((p_sub["Low"] - d_sub["Low"]).abs() > 1e-4) |
                    ((p_sub["Close"] - d_sub["Close"]).abs() > 1e-4) |
                    ((p_sub["Volume"] - d_sub["Volume"]).abs() > 1e-4)
                ).sum()

                if val_diff > 0:
                    con.close()
                    raise RuntimeError(f"Value-level element-wise price/volume mismatch detected during recovery for symbol '{sym}' ({val_diff} mismatches)")
            except Exception as ex:
                con.close()
                raise RuntimeError(f"Staged Parquet value verification failed for symbol '{sym}': {ex}") from ex

            os.replace(staged_p, str(final_p))
            entry["status"] = "COMPLETED"
            entry["recovered_at"] = datetime.now(timezone.utc).isoformat()
            recovered_count += 1
        elif status == "COMMITTED_DUCKDB" and not duck_tx_match:
            con.close()
            raise RuntimeError(f"Journal status COMMITTED_DUCKDB for symbol '{sym}' has no matching DuckDB transaction rows (tx_id: {tx_id}). Storage mismatch!")
        elif status == "PENDING_DUCKDB" and not duck_tx_match:
            # Ambiguous uncommitted transaction state: preserve staged file and journal entry, fail closed
            con.close()
            raise RuntimeError(f"Ambiguous PENDING_DUCKDB transaction for symbol '{sym}' (tx_id: {tx_id}). Preserving staged file and failing closed.")

    con.close()
    save_journal(journal, j_path)
    return recovered_count

def load_checkpoint() -> dict:
    if checkpoint_path.exists():
        try:
            return json.loads(checkpoint_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_checkpoint(data: dict):
    checkpoint_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def validate_and_normalize_ohlcv(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Downloaded DataFrame is empty or None")

    df_clean = df.copy()

    # Reset index if date is index
    if isinstance(df_clean.index, pd.DatetimeIndex):
        df_clean = df_clean.reset_index()

    # Normalize column names
    col_map = {}
    for c in df_clean.columns:
        c_str = str(c).strip()
        if c_str.lower() in ["date", "datetime", "timestamp"]:
            col_map[c] = "date"
        elif c_str.lower() == "open":
            col_map[c] = "Open"
        elif c_str.lower() == "high":
            col_map[c] = "High"
        elif c_str.lower() == "low":
            col_map[c] = "Low"
        elif c_str.lower() == "close":
            col_map[c] = "Close"
        elif c_str.lower() == "volume":
            col_map[c] = "Volume"

    df_clean = df_clean.rename(columns=col_map)
    required = ["date", "Open", "High", "Low", "Close", "Volume"]
    for r in required:
        if r not in df_clean.columns:
            raise ValueError(f"Missing required column '{r}' after normalization.")

    # Normalize date to string YYYY-MM-DD
    df_clean["date"] = pd.to_datetime(df_clean["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df_clean = df_clean.dropna(subset=["date"])

    # Convert numeric price fields
    for price_col in ["Open", "High", "Low", "Close"]:
        df_clean[price_col] = pd.to_numeric(df_clean[price_col], errors="coerce")

    # Drop unformed or NaN candles (e.g. today unformed session)
    valid_mask = (
        (df_clean["Open"] > 0) & (df_clean["Open"].notna()) &
        (df_clean["High"] > 0) & (df_clean["High"].notna()) &
        (df_clean["Low"] > 0) & (df_clean["Low"].notna()) &
        (df_clean["Close"] > 0) & (df_clean["Close"].notna())
    )
    df_clean = df_clean[valid_mask].copy()

    if df_clean.empty:
        raise ValueError("No valid completed OHLCV rows remaining after dropping unformed candles.")

    df_clean["Volume"] = pd.to_numeric(df_clean["Volume"], errors="coerce").fillna(0)
    df_clean = df_clean[df_clean["Volume"] >= 0]

    # Check OHLC Geometry and filter bad tick rows
    geom_invalid = (
        (df_clean["Low"] > df_clean["Open"]) |
        (df_clean["Low"] > df_clean["Close"]) |
        (df_clean["High"] < df_clean["Open"]) |
        (df_clean["High"] < df_clean["Close"]) |
        (df_clean["High"] < df_clean["Low"])
    )
    if geom_invalid.any():
        invalid_count = geom_invalid.sum()
        print(f"[-] Filtered {invalid_count} bad tick rows with OHLC geometry violations for symbol {symbol}.")
        df_clean = df_clean[~geom_invalid].copy()

    if df_clean.empty:
        raise ValueError(f"No valid completed OHLCV rows remaining for symbol {symbol} after filtering geometry violations.")

    # Deduplicate by date timestamp keeping latest
    df_clean = df_clean.drop_duplicates(subset=["date"], keep="last")
    df_clean = df_clean.sort_values("date").reset_index(drop=True)

    # Return required OHLCV columns + any extra columns present in df
    extra = [c for c in df_clean.columns if c not in required]
    return df_clean[required + extra]

def ingest_symbol(symbol: str, start_date: str = "2015-01-01", end_date: str = None) -> dict:
    if not end_date:
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Check if an unresolved FAILED journal entry exists for this symbol before proceeding
    journal = load_journal()
    prior_entry = journal.get(symbol, {})
    if isinstance(prior_entry, dict) and prior_entry.get("status") == "FAILED":
        raise RuntimeError(f"Unresolved FAILED journal entry exists for symbol '{symbol}'. Clear or reconcile prior failure evidence before retrying.")

    provider_ticker = get_provider_ticker(symbol)
    effective_start = POST_2015_LISTING_DATES.get(symbol, start_date)

    print(f"[*] Ingesting {symbol} ({provider_ticker}) from {effective_start} to {end_date}...")

    ticker = yf.Ticker(provider_ticker)
    hist = ticker.history(start=effective_start, end=end_date)

    if hist is None or hist.empty:
        raise ValueError(f"No historical data returned for ticker '{provider_ticker}'")

    df_clean = validate_and_normalize_ohlcv(hist, symbol)

    # 1. Gate 1: Merge incoming rows with existing Parquet store by date to preserve older dates & feature columns
    p_path = features_dir / f"{symbol}.parquet"
    if p_path.exists():
        try:
            df_existing = pd.read_parquet(p_path)
            if "date" in df_existing.columns:
                df_existing["date"] = pd.to_datetime(df_existing["date"]).dt.strftime("%Y-%m-%d")

                # Combine historical dates missing from incoming provider response
                old_only = df_existing[~df_existing["date"].isin(df_clean["date"])]
                if not old_only.empty:
                    df_clean = pd.concat([df_clean, old_only], ignore_index=True).sort_values("date").reset_index(drop=True)

                # Re-merge extra derived feature columns if present
                extra_cols = [c for c in df_existing.columns if c not in df_clean.columns and c != "date"]
                if extra_cols:
                    df_features = df_existing[["date"] + extra_cols].drop_duplicates("date")
                    df_clean = pd.merge(df_clean, df_features, on="date", how="left")
        except Exception as ex:
            raise RuntimeError(f"Failed to read/merge existing Parquet feature store for symbol '{symbol}': {ex}") from ex

    # Stage temporary Parquet file first
    fd, temp_p = tempfile.mkstemp(dir=str(features_dir), suffix=".parquet")
    os.close(fd)
    df_clean.to_parquet(temp_p, index=False)

    tx_id = hashlib.sha256(f"{symbol}_{time.time()}".encode("utf-8")).hexdigest()[:12]

    # Register journal entry: PENDING_DUCKDB
    journal[symbol] = {
        "tx_id": tx_id,
        "status": "PENDING_DUCKDB",
        "staged_parquet_path": str(temp_p),
        "target_parquet_path": str(p_path),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    save_journal(journal)

    # Execute DuckDB transaction with date-keyed upsert (delete only overlapping dates, preserving older dates)
    con = duckdb.connect(str(duckdb_path))
    now_str = datetime.now(timezone.utc).isoformat()

    rows = []
    for _, r in df_clean.iterrows():
        rows.append((
            symbol, str(r["date"]), float(r["Open"]), float(r["High"]),
            float(r["Low"]), float(r["Close"]), float(r["Volume"]),
            f"TX_{tx_id}", now_str
        ))

    try:
        con.begin()
        incoming_dates = [str(r["date"]) for _, r in df_clean.iterrows()]
        con.execute("DELETE FROM daily_ohlcv WHERE symbol = ? AND date IN (SELECT unnest(?))", [symbol, incoming_dates])
        con.executemany("INSERT INTO daily_ohlcv VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
        con.commit()
    except Exception as ex:
        con.rollback()
        con.close()
        if symbol in journal:
            journal[symbol]["status"] = "FAILED"
            journal[symbol]["error"] = str(ex)
            journal[symbol]["failed_at"] = datetime.now(timezone.utc).isoformat()
            save_journal(journal)
        raise RuntimeError(f"DuckDB transaction failed for {symbol}: {ex}") from ex
    con.close()

    # Update journal entry: COMMITTED_DUCKDB IMMEDIATELY POST-COMMIT
    journal[symbol]["status"] = "COMMITTED_DUCKDB"
    journal[symbol]["committed_at"] = datetime.now(timezone.utc).isoformat()
    save_journal(journal)

    # Atomically promote temporary Parquet file after DuckDB transaction succeeds
    os.replace(temp_p, str(p_path))

    # Clear completed journal entry
    journal[symbol]["status"] = "COMPLETED"
    journal[symbol]["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_journal(journal)

    # Independent Readback Verification
    df_readback = pd.read_parquet(p_path)
    readback_count = len(df_readback)
    readback_min = df_readback["date"].min()
    readback_max = df_readback["date"].max()

    return {
        "symbol": symbol,
        "provider_ticker": provider_ticker,
        "effective_start_date": effective_start,
        "retrieved_rows": len(df_clean),
        "persisted_readback_rows": readback_count,
        "earliest_date": readback_min,
        "latest_date": readback_max,
        "status": "SUCCESS"
    }

def main():
    parser = argparse.ArgumentParser(description="TradeMindAI Historical Ingestion Pipeline CLI")
    parser.add_argument("--pilot", action="store_true", help="Run 6-symbol pilot batch")
    parser.add_argument("--symbol", type=str, default="", help="Single symbol to ingest")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for full run")
    args = parser.parse_args()

    init_duckdb()

    # Recover any pending crashed transactions on startup
    recovered = recover_pending_transactions()
    if recovered > 0:
        print(f"[+] Recovered {recovered} pending journal transactions on startup.")

    symbols_dict = get_nifty_500_universe()

    if args.pilot:
        symbols_to_run = ["RELIANCE", "TCS", "ABB", "LICI", "ATGL", "LTF"]
    elif args.symbol:
        symbols_to_run = [args.symbol.strip().upper()]
    else:
        symbols_to_run = list(symbols_dict.keys())

    print(f"=== [INGESTION] Historical Ingestion Started across {len(symbols_to_run)} symbols ===")
    checkpoint = load_checkpoint()

    success_count = 0
    failure_count = 0

    for idx, sym in enumerate(symbols_to_run, 1):
        if checkpoint.get(sym, {}).get("status") == "SUCCESS":
            success_count += 1
            print(f"    [{idx}/{len(symbols_to_run)}] SKIPPED (Already SUCCESS): {sym}")
            continue

        try:
            res = ingest_symbol(sym)
            checkpoint[sym] = {
                "status": "SUCCESS",
                "rows": res["persisted_readback_rows"],
                "earliest_date": res["earliest_date"],
                "latest_date": res["latest_date"],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            success_count += 1
            print(f"    [{idx}/{len(symbols_to_run)}] SUCCESS: {sym} -> {res['persisted_readback_rows']} rows ({res['earliest_date']} to {res['latest_date']})")
        except Exception as e:
            checkpoint[sym] = {
                "status": "FAILED",
                "error": str(e),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            failure_count += 1
            print(f"    [{idx}/{len(symbols_to_run)}] FAILED: {sym} -> {e}")

        save_checkpoint(checkpoint)
        time.sleep(0.1)

    print(f"\n=== [INGESTION] Completed: Success={success_count}, Failures={failure_count} ===")

if __name__ == "__main__":
    main()
