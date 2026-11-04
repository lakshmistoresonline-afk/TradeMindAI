"""
================================================================================
TradeMindAI: Master Nifty 500 Historical Data Ingestion Pipeline (v5.9-STRICT-RECONCILIATION)
================================================================================
Fetches, normalizes, validates, and idempotently persists 10-year daily OHLCV data
(2015-01-01 through current date) across all 500 canonical Nifty equities.
Enforces crash-safe dual-store persistence via durable transaction journal
with transaction-specific source tags, value-level readback verification,
destination path resolution integrity, date-keyed DuckDB upserts, temporary backup preservation,
post-commit failure isolation, SHA-256 intent hashing, and atomic Parquet promotion.
Enforces validate_mutation_target() before modifying protected paths.
Includes strictly isolated test-only failpoint guard (_check_test_failpoint)
requiring TRADEMIND_TEST_MODE="true" for all 9 crash boundaries.
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
from backend.core.mutation_guard import validate_mutation_target, ProductionDataMutationError

features_dir = root_dir / "backend" / "data" / "features"
duckdb_path = root_dir / "backend" / "data" / "analytical.duckdb"
checkpoint_path = root_dir / "backend" / "data" / "ingestion_checkpoint.json"
journal_path = root_dir / "backend" / "data" / "ingestion_journal.json"

ALLOWED_JOURNAL_STATUSES = {"PENDING_STAGED", "COMMITTED_DUCKDB", "PROMOTED_PARQUET", "COMPLETED", "FAILED_PRE_COMMIT", "FAILED_POST_COMMIT", "FAILED"}

VALID_FAILPOINTS = {
    "POST_STAGING",
    "POST_INTENT_JOURNAL",
    "PRE_DUCKDB_COMMIT",
    "POST_DUCKDB_COMMIT",
    "POST_COMMITTED_JOURNAL",
    "POST_PARQUET_PROMOTION",
    "POST_PROMOTED_JOURNAL",
    "POST_CHECKPOINT_SAVE",
    "DURING_RECOVERY"
}

SYMBOL_ALIAS_MAP = {
    "L&TFH": "LTF.NS",
    "M&M": "M&M.NS",
    "M&MFIN": "M&MFIN.NS",
    "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
    "L&T": "LT.NS",
    "TATAMOTORS-DVR": "TATAMTRDVR.NS",
    "BIRET": "BIRET-RR.NS",
    "EMBASSY": "EMBASSY-RR.NS"
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

def _check_test_failpoint(fp_name: str) -> None:
    """
    Test-only failpoint trigger for process crash testing.
    Execution is strictly impossible unless TRADEMIND_TEST_MODE='true' is set in environment,
    and fp_name is in VALID_FAILPOINTS allowlist.
    """
    if os.environ.get("TRADEMIND_TEST_MODE") == "true":
        target_fp = os.environ.get("INGESTION_TEST_FAILPOINT")
        if target_fp and target_fp in VALID_FAILPOINTS and target_fp == fp_name:
            os._exit(99)

def get_provider_ticker(canonical_symbol: str) -> str:
    if canonical_symbol in SYMBOL_ALIAS_MAP:
        return SYMBOL_ALIAS_MAP[canonical_symbol]
    return f"{canonical_symbol}.NS"

def init_duckdb(db_p: Path = None, custom_db_path: Path = None):
    target_p = custom_db_path or db_p or duckdb_path
    validate_mutation_target(target_p)
    target_p.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(target_p))
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

def load_journal(j_path: Path = None, custom_journal_path: Path = None) -> dict:
    target = custom_journal_path or j_path or journal_path
    if target.exists():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise RuntimeError(f"Corrupt or malformed journal file at '{target}': not a JSON object")
            return data
        except Exception as ex:
            raise RuntimeError(f"Corrupt or malformed journal file at '{target}': {ex}") from ex
    return {}

def save_journal(data: dict, j_path: Path = None, custom_journal_path: Path = None):
    target = custom_journal_path or j_path or journal_path
    validate_mutation_target(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_j = tempfile.mkstemp(dir=str(target.parent), prefix="tmp_j_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_j, str(target))
    except Exception:
        if os.path.exists(temp_j):
            try: os.unlink(temp_j)
            except Exception: pass
        raise

def load_checkpoint(cp_p: Path = None) -> dict:
    target = cp_p or checkpoint_path
    if target.exists():
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise RuntimeError(f"Corrupt or malformed checkpoint file at '{target}': not a JSON object")
            return data
        except Exception as ex:
            raise RuntimeError(f"Corrupt or malformed checkpoint file at '{target}': {ex}") from ex
    return {}

def save_checkpoint(data: dict, target: Path = None):
    out_p = target or checkpoint_path
    validate_mutation_target(out_p)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_cp = tempfile.mkstemp(dir=str(out_p.parent), prefix="tmp_cp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2))
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_cp, str(out_p))
    except Exception:
        if os.path.exists(temp_cp):
            try: os.unlink(temp_cp)
            except Exception: pass
        raise

def verify_ohlcv_value_equality(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    label_a: str,
    label_b: str,
    symbol: str,
    tolerance: float = 1e-4
) -> None:
    """
    Compares two OHLCV DataFrames element-wise for exact symbol/date match:
    1. Verifies non-empty and matching row counts.
    2. Verifies exact sorted date-key set equality and no duplicate dates.
    3. Verifies no missing (NaN), infinite, or non-finite values.
    4. Compares element-wise values across Open, High, Low, Close, Volume within numeric tolerance.
    Raises RuntimeError if any check fails.
    """
    req_cols = ["date", "Open", "High", "Low", "Close", "Volume"]

    if df_a is None or df_a.empty or df_b is None or df_b.empty:
        raise RuntimeError(f"OHLCV verification failed for '{symbol}': '{label_a}' or '{label_b}' is empty or None")

    if not all(c in df_a.columns for c in req_cols) or not all(c in df_b.columns for c in req_cols):
        raise RuntimeError(f"OHLCV verification failed for '{symbol}': missing required OHLCV columns in '{label_a}' or '{label_b}'")

    if len(df_a) != len(df_b):
        raise RuntimeError(f"OHLCV row count mismatch for symbol '{symbol}': {label_a} has {len(df_a)} rows, {label_b} has {len(df_b)} rows")

    a_dates = list(pd.to_datetime(df_a["date"]).dt.strftime("%Y-%m-%d"))
    b_dates = list(pd.to_datetime(df_b["date"]).dt.strftime("%Y-%m-%d"))

    if a_dates != b_dates:
        raise RuntimeError(f"OHLCV date set mismatch for symbol '{symbol}' between '{label_a}' and '{label_b}'")

    if len(a_dates) != len(set(a_dates)):
        raise RuntimeError(f"Duplicate dates detected in '{label_a}' for symbol '{symbol}'")

    # Numeric finite check
    num_cols = ["Open", "High", "Low", "Close", "Volume"]
    if df_a[num_cols].isna().any().any() or np.isinf(df_a[num_cols].to_numpy()).any():
        raise RuntimeError(f"Non-finite or NaN values detected in '{label_a}' for symbol '{symbol}'")
    if df_b[num_cols].isna().any().any() or np.isinf(df_b[num_cols].to_numpy()).any():
        raise RuntimeError(f"Non-finite or NaN values detected in '{label_b}' for symbol '{symbol}'")

    # Element-wise absolute differences
    a_sub = df_a.set_index("date")[num_cols].sort_index()
    b_sub = df_b.set_index("date")[num_cols].sort_index()

    mismatches = (
        ((a_sub["Open"] - b_sub["Open"]).abs() > tolerance) |
        ((a_sub["High"] - b_sub["High"]).abs() > tolerance) |
        ((a_sub["Low"] - b_sub["Low"]).abs() > tolerance) |
        ((a_sub["Close"] - b_sub["Close"]).abs() > tolerance) |
        ((a_sub["Volume"] - b_sub["Volume"]).abs() > tolerance)
    ).sum()

    if mismatches > 0:
        raise RuntimeError(f"Value-level OHLCV mismatch detected for symbol '{symbol}' between '{label_a}' and '{label_b}': {mismatches} rows exceed tolerance {tolerance}")

def validate_and_normalize_ohlcv(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError(f"Downloaded DataFrame is empty or None for symbol {symbol}")

    df_clean = df.copy()

    # Flatten multi-index columns if present
    if isinstance(df_clean.columns, pd.MultiIndex):
        df_clean.columns = [c[0] if isinstance(c, tuple) else c for c in df_clean.columns]

    # Reset index if date is index or multi-index
    if isinstance(df_clean.index, pd.DatetimeIndex):
        df_clean = df_clean.reset_index()

    # Normalize column names
    col_map = {}
    for c in df_clean.columns:
        c_str = str(c).strip()
        if c_str.lower() in ["date", "datetime", "timestamp", "index"]:
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
    req_cols = ["date", "Open", "High", "Low", "Close", "Volume"]

    if not all(col in df_clean.columns for col in req_cols):
        missing = [c for c in req_cols if c not in df_clean.columns]
        raise ValueError(f"Missing required OHLCV columns for symbol {symbol}: {missing}")

    # Check non-finite values (NaN / Inf)
    num_cols = ["Open", "High", "Low", "Close", "Volume"]
    if df_clean[num_cols].isna().any().any() or np.isinf(df_clean[num_cols].to_numpy()).any():
        raise ValueError(f"Non-finite or NaN values detected in OHLCV rows for symbol {symbol}")

    df_clean["date"] = pd.to_datetime(df_clean["date"]).dt.strftime("%Y-%m-%d")

    # Reject duplicate dates explicitly
    dup_count = df_clean["date"].duplicated().sum()
    if dup_count > 0:
        raise ValueError(f"Duplicate dates detected for symbol {symbol}: {dup_count} duplicate rows found")

    # Geometry check: High >= Low, High >= Open, High >= Close, Low <= Open, Low <= Close
    geom_mask = (df_clean["High"] >= df_clean["Low"]) & (df_clean["High"] >= df_clean["Open"]) & (df_clean["High"] >= df_clean["Close"]) & (df_clean["Low"] <= df_clean["Open"]) & (df_clean["Low"] <= df_clean["Close"])
    bad_geom_cnt = len(df_clean) - geom_mask.sum()
    if bad_geom_cnt > 0:
        raise ValueError(f"OHLC geometry violations detected for symbol {symbol}: {bad_geom_cnt} invalid tick rows found")

    # Validate non-positive prices and negative volume
    price_cols = ["Open", "High", "Low", "Close"]
    if (df_clean[price_cols] <= 0).any().any():
        raise ValueError(f"Non-positive prices detected for symbol {symbol}")
    if (df_clean["Volume"] < 0).any():
        raise ValueError(f"Negative volume detected for symbol {symbol}")

    return df_clean[req_cols].sort_values("date").reset_index(drop=True)

def commit_symbol_ingestion(
    symbol: str,
    df_clean: pd.DataFrame,
    con,
    f_dir: Path,
    checkpoint: dict,
    journal: dict,
    tx_id: str,
    checkpoint_p: Path = None,
    journal_p: Path = None
) -> dict:
    """
    Executes a transactional ingestion commit for symbol:
    1. Validates mutation targets via validate_mutation_target().
    2. Stages Parquet file in atomic temporary path & calculates SHA-256 intent.
    3. Saves durable journal entry (status PENDING_STAGED) BEFORE DuckDB transaction.
    4. Preserves existing committed Parquet file via temporary backup copy.
    5. Executes date-keyed DuckDB deletion and insertion inside DuckDB transaction (BEGIN ... COMMIT).
    6. Performs value-level readback verification between DuckDB transaction rows and staged Parquet file.
    7. Promotes staged Parquet file to final feature store path via atomic os.replace.
    8. Updates and saves journal and checkpoint files.

    Differentiates pre-commit failures (rolled back with backup restored) from post-commit failures
    (DuckDB rows preserved, journal set to FAILED_POST_COMMIT for safe recovery).
    Includes test failpoint checks (_check_test_failpoint) requiring TRADEMIND_TEST_MODE="true".
    """
    final_p = f_dir / f"{symbol}.parquet"

    # Enforce mutation guard on final destination
    validate_mutation_target(final_p)
    if checkpoint_p:
        validate_mutation_target(checkpoint_p)
    if journal_p:
        validate_mutation_target(journal_p)

    f_dir.mkdir(parents=True, exist_ok=True)
    fd, staged_p_str = tempfile.mkstemp(dir=str(f_dir), prefix=f"tmp_{symbol}_", suffix=".parquet")
    os.close(fd)
    staged_p = Path(staged_p_str)

    # Preserve existing final Parquet file in backup if present
    backup_p = f_dir / f".tmp_backup_{symbol}_{tx_id}.parquet"
    previous_sha256 = None
    if final_p.exists():
        try:
            p_bytes = final_p.read_bytes()
            previous_sha256 = hashlib.sha256(p_bytes).hexdigest()
            backup_p.write_bytes(p_bytes)
        except Exception as ex:
            if staged_p.exists():
                try: os.unlink(staged_p)
                except Exception: pass
            raise RuntimeError(f"Failed to create backup copy of existing Parquet file for symbol '{symbol}': {ex}") from ex

    source_tag = f"TX_{tx_id}"
    duckdb_committed = False

    try:
        # 1. Write staged Parquet and calculate SHA-256
        df_clean.to_parquet(staged_p)
        staged_sha256 = hashlib.sha256(staged_p.read_bytes()).hexdigest()

        _check_test_failpoint("POST_STAGING")

        min_date = str(df_clean["date"].min())
        max_date = str(df_clean["date"].max())

        # Save durable intent BEFORE DuckDB transaction
        journal[symbol] = {
            "tx_id": tx_id,
            "status": "PENDING_STAGED",
            "staged_parquet_path": str(staged_p),
            "target_parquet_path": str(final_p),
            "staged_sha256": staged_sha256,
            "expected_rows": len(df_clean),
            "earliest_date": min_date,
            "latest_date": max_date,
            "previous_parquet_sha256": previous_sha256,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        save_journal(journal, j_path=journal_p)

        _check_test_failpoint("POST_INTENT_JOURNAL")

        # 2. DuckDB Transaction
        con.execute("BEGIN TRANSACTION")
        con.execute("DELETE FROM daily_ohlcv WHERE symbol = ? AND date >= ? AND date <= ?", [symbol, min_date, max_date])

        ingested_at = datetime.now(timezone.utc).isoformat()
        insert_rows = []
        for _, row in df_clean.iterrows():
            insert_rows.append((
                symbol, str(row["date"]), float(row["Open"]), float(row["High"]),
                float(row["Low"]), float(row["Close"]), float(row["Volume"]), source_tag, ingested_at
            ))

        con.executemany("""
            INSERT INTO daily_ohlcv VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, insert_rows)

        # 3. Readback Verification (value-level equality)
        df_duck_tx = con.execute("""
            SELECT date, open as Open, high as High, low as Low, close as Close, volume as Volume
            FROM daily_ohlcv WHERE symbol = ? AND source = ? ORDER BY date
        """, [symbol, source_tag]).df()

        verify_ohlcv_value_equality(df_clean, df_duck_tx, "candidate_df", "duckdb_tx_readback", symbol)

        _check_test_failpoint("PRE_DUCKDB_COMMIT")

        con.execute("COMMIT")
        duckdb_committed = True

        _check_test_failpoint("POST_DUCKDB_COMMIT")

        journal[symbol]["status"] = "COMMITTED_DUCKDB"
        save_journal(journal, j_path=journal_p)

        _check_test_failpoint("POST_COMMITTED_JOURNAL")

        # 4. Atomic Parquet Promotion after DuckDB COMMIT
        os.replace(staged_p, str(final_p))

        _check_test_failpoint("POST_PARQUET_PROMOTION")

        journal[symbol]["status"] = "PROMOTED_PARQUET"
        save_journal(journal, j_path=journal_p)

        _check_test_failpoint("POST_PROMOTED_JOURNAL")

        # Clean up temporary backup on successful promotion
        if backup_p.exists():
            try: os.unlink(backup_p)
            except Exception: pass

        # 5. Checkpoint & Journal Finalization (retain full audit metadata)
        checkpoint[symbol] = {
            "status": "SUCCESS",
            "rows": len(df_clean),
            "earliest_date": min_date,
            "latest_date": max_date,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        journal[symbol] = {
            "tx_id": tx_id,
            "status": "COMPLETED",
            "staged_parquet_path": str(staged_p),
            "target_parquet_path": str(final_p),
            "staged_sha256": staged_sha256,
            "expected_rows": len(df_clean),
            "earliest_date": min_date,
            "latest_date": max_date,
            "previous_parquet_sha256": previous_sha256,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }

        save_checkpoint(checkpoint, target=checkpoint_p)

        _check_test_failpoint("POST_CHECKPOINT_SAVE")

        save_journal(journal, j_path=journal_p)

        return checkpoint[symbol]

    except Exception as ex:
        if not duckdb_committed:
            # Pre-commit failure: Roll back DuckDB and restore previous Parquet from backup
            try: con.execute("ROLLBACK")
            except Exception: pass

            if backup_p.exists():
                try: os.replace(backup_p, str(final_p))
                except Exception: pass

            if staged_p.exists():
                try: os.unlink(staged_p)
                except Exception: pass

            journal[symbol] = {
                "tx_id": tx_id,
                "status": "FAILED_PRE_COMMIT",
                "error": str(ex),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            try: save_journal(journal, j_path=journal_p)
            except Exception: pass

            raise RuntimeError(f"Ingestion transaction failed pre-commit for symbol '{symbol}': {ex}") from ex
        else:
            # Post-commit failure: DuckDB rows remain committed! Record FAILED_POST_COMMIT for safe recovery.
            journal[symbol] = {
                "tx_id": tx_id,
                "status": "FAILED_POST_COMMIT",
                "error": str(ex),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            try: save_journal(journal, j_path=journal_p)
            except Exception: pass

            raise RuntimeError(f"Ingestion transaction failed post-commit for symbol '{symbol}': {ex}") from ex

def recover_pending_transactions(
    j_path: Path = None,
    cp_path: Path = None,
    db_p: Path = None,
    f_dir_p: Path = None,
    custom_journal_path: Path = None,
    custom_feat_dir: Path = None,
    custom_db_path: Path = None
) -> int:
    """
    Recovers any pending, interrupted, or post-commit failed transactions in the journal.
    Fails closed if journal is malformed, missing DuckDB, or has ambiguous uncommitted transaction.
    Verifies DuckDB vs Parquet value equality before marking COMPLETED.
    """
    _check_test_failpoint("DURING_RECOVERY")

    target_j = custom_journal_path or j_path or journal_path
    target_f_dir = custom_feat_dir or f_dir_p or features_dir
    target_cp = cp_path or (custom_journal_path.parent / "checkpoint.json" if custom_journal_path else checkpoint_path)
    target_db = custom_db_path or db_p or duckdb_path

    journal = load_journal(target_j)
    checkpoint = load_checkpoint(target_cp)

    if not journal:
        return 0

    if not target_db.exists():
        raise RuntimeError(f"DuckDB database missing or unavailable at '{target_db}' during recovery")

    con = duckdb.connect(str(target_db))
    recovered_count = 0

    for sym, entry in journal.items():
        if not isinstance(entry, dict):
            con.close()
            raise RuntimeError(f"Malformed non-dictionary journal entry for symbol '{sym}'")

        status = entry.get("status")

        # Skip already completed or pre-commit failed transactions
        if status in ("COMPLETED", "FAILED_PRE_COMMIT", "FAILED"):
            continue

        staged_p = entry.get("staged_parquet_path")
        target_p = entry.get("target_parquet_path")
        tx_id = entry.get("tx_id")
        final_p = target_f_dir / f"{sym}.parquet"

        if target_p and Path(target_p).name != f"{sym}.parquet":
            con.close()
            raise RuntimeError(f"Target Parquet path mismatch for symbol '{sym}'")

        df_duck_tx = con.execute("""
            SELECT date, open as Open, high as High, low as Low, close as Close, volume as Volume
            FROM daily_ohlcv WHERE symbol = ? AND source = ? ORDER BY date
        """, [sym, f"TX_{tx_id}"]).df()

        duck_tx_match = len(df_duck_tx) > 0

        if duck_tx_match:
            expected_hash = entry.get("staged_sha256")
            expected_rows = entry.get("expected_rows")

            if expected_rows and len(df_duck_tx) != expected_rows:
                con.close()
                raise RuntimeError(f"Row count mismatch for committed transaction '{tx_id}' symbol '{sym}': expected {expected_rows}, got {len(df_duck_tx)}")

            if final_p.exists():
                df_final = pd.read_parquet(final_p)
                verify_ohlcv_value_equality(df_final, df_duck_tx, "final_parquet", "duckdb_tx", sym)
                if entry.get("status") != "COMPLETED":
                    entry["status"] = "COMPLETED"
                    checkpoint[sym] = {
                        "status": "SUCCESS",
                        "rows": len(df_duck_tx),
                        "earliest_date": str(df_duck_tx["date"].min()),
                        "latest_date": str(df_duck_tx["date"].max()),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    recovered_count += 1
            elif staged_p and os.path.exists(staged_p):
                actual_staged_hash = hashlib.sha256(Path(staged_p).read_bytes()).hexdigest()
                if expected_hash and actual_staged_hash != expected_hash:
                    con.close()
                    raise RuntimeError(f"Corrupt staged Parquet file for symbol '{sym}': SHA-256 hash mismatch (expected {expected_hash}, got {actual_staged_hash})")

                df_staged = pd.read_parquet(staged_p)
                verify_ohlcv_value_equality(df_staged, df_duck_tx, "staged_parquet", "duckdb_tx", sym)

                os.replace(staged_p, str(final_p))
                entry["status"] = "COMPLETED"
                checkpoint[sym] = {
                    "status": "SUCCESS",
                    "rows": len(df_duck_tx),
                    "earliest_date": str(df_duck_tx["date"].min()),
                    "latest_date": str(df_duck_tx["date"].max()),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                recovered_count += 1
            else:
                con.close()
                raise RuntimeError(f"Missing required staged Parquet file for committed symbol '{sym}': {staged_p}")

        elif status == "FAILED_POST_COMMIT" and final_p.exists():
            df_final = pd.read_parquet(final_p)
            df_duck_all = con.execute("""
                SELECT date, open as Open, high as High, low as Low, close as Close, volume as Volume
                FROM daily_ohlcv WHERE symbol = ? ORDER BY date
            """, [sym]).df()
            verify_ohlcv_value_equality(df_final, df_duck_all, "final_parquet", "duckdb_all", sym)
            entry["status"] = "COMPLETED"
            recovered_count += 1
        elif status == "PENDING_STAGED" and not duck_tx_match:
            if staged_p and os.path.exists(staged_p):
                try: os.unlink(staged_p)
                except Exception: pass
            entry["status"] = "FAILED_PRE_COMMIT"
            entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        elif status in ("COMMITTED_DUCKDB", "PENDING_DUCKDB") and not duck_tx_match:
            con.close()
            raise RuntimeError(f"Ambiguous PENDING_DUCKDB transaction: Journal status {status} for symbol '{sym}' has no matching DuckDB transaction rows")

    con.close()
    save_checkpoint(checkpoint, target=target_cp)
    save_journal(journal, j_path=target_j)
    return recovered_count

def is_symbol_current(symbol: str, target_latest_date: str, cp_info: dict, f_dir: Path, db_p: Path, tolerance: float = 1e-4) -> bool:
    """
    Independently verifies that a symbol is completely current and consistent:
    1. Checkpoint status is SUCCESS.
    2. Final Parquet file exists, can be read, and has no duplicate dates.
    3. DuckDB data exists for symbol with no duplicate dates.
    4. Exact date set equality between DuckDB and Parquet.
    5. Element-wise OHLCV value equality between DuckDB and Parquet within tolerance (1e-4).
    6. Latest stored date >= target_latest_date.
    """
    if not cp_info or cp_info.get("status") != "SUCCESS":
        return False

    target_p = f_dir / f"{symbol}.parquet"
    if not target_p.exists() or not db_p.exists():
        return False

    try:
        df_p = pd.read_parquet(target_p)
        if df_p.empty or "date" not in df_p.columns:
            return False

        p_dates = list(pd.to_datetime(df_p["date"]).dt.strftime("%Y-%m-%d"))
        if len(p_dates) != len(set(p_dates)):
            return False

        p_latest = max(p_dates)
        p_rows = len(df_p)

        con = duckdb.connect(str(db_p))
        df_d = con.execute("""
            SELECT date, open as Open, high as High, low as Low, close as Close, volume as Volume
            FROM daily_ohlcv WHERE symbol = ? ORDER BY date
        """, [symbol]).df()
        con.close()

        if df_d.empty or "date" not in df_d.columns:
            return False

        d_dates = list(pd.to_datetime(df_d["date"]).dt.strftime("%Y-%m-%d"))
        if len(d_dates) != len(set(d_dates)):
            return False

        d_latest = max(d_dates)
        d_rows = len(df_d)

        # 1. Require row count match, date set match, and latest date >= target_latest_date
        if p_rows != d_rows or p_latest != d_latest or p_dates != d_dates:
            return False

        # 2. Checkpoint metadata agreement
        if cp_info.get("rows") != p_rows or cp_info.get("latest_date") != p_latest:
            return False

        # 3. Element-wise OHLCV value comparison
        verify_ohlcv_value_equality(df_p, df_d, "parquet_store", "duckdb_store", symbol, tolerance=tolerance)

        if p_latest >= target_latest_date:
            return True

    except Exception:
        return False

    return False

def ingest_symbol(
    symbol: str,
    start_date: str = "2015-01-01",
    end_date: str = None,
    j_path: Path = None,
    cp_path: Path = None,
    db_p: Path = None,
    f_dir_p: Path = None
) -> dict:
    target_j = j_path or journal_path
    target_cp = cp_path or checkpoint_path
    target_db = db_p or duckdb_path
    target_f_dir = f_dir_p or features_dir

    journal = load_journal(target_j)
    checkpoint = load_checkpoint(target_cp)

    if symbol in journal and journal[symbol].get("status") == "FAILED":
        raise RuntimeError(f"Unresolved FAILED journal entry exists for symbol '{symbol}'")

    tx_id = hashlib.md5(f"{symbol}_{time.time()}".encode()).hexdigest()[:12]
    ticker = get_provider_ticker(symbol)
    end_str = end_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    target_parquet = target_f_dir / f"{symbol}.parquet"

    # Check if existing valid dataset is present for incremental fetch
    if target_parquet.exists() and target_db.exists():
        try:
            con_check = duckdb.connect(str(target_db))
            duck_info = con_check.execute("SELECT count(*), min(date), max(date) FROM daily_ohlcv WHERE symbol = ?", [symbol]).fetchone()
            con_check.close()

            if duck_info and duck_info[0] > 0 and duck_info[2]:
                last_stored_date = str(duck_info[2])
                df_existing = pd.read_parquet(target_parquet)

                # Validate existing dataset
                if df_existing["date"].duplicated().any():
                    raise ValueError(f"Duplicate dates detected in existing Parquet dataset for symbol {symbol}")

                # Fetch incrementally starting 5 days before last_stored_date to avoid boundary gaps
                fetch_start = (pd.to_datetime(last_stored_date) - pd.Timedelta(days=5)).strftime("%Y-%m-%d")
                df_raw = yf.download(ticker, start=fetch_start, end=end_str, progress=False)

                if df_raw is not None and not df_raw.empty:
                    df_incr = validate_and_normalize_ohlcv(df_raw, symbol)

                    # Determine overlap dates
                    overlap_dates = sorted(list(set(df_existing["date"]).intersection(set(df_incr["date"]))))
                    if overlap_dates:
                        ex_sub = df_existing[df_existing["date"].isin(overlap_dates)].set_index("date")[["Open", "High", "Low", "Close", "Volume"]]
                        inc_sub = df_incr[df_incr["date"].isin(overlap_dates)].set_index("date")[["Open", "High", "Low", "Close", "Volume"]]

                        # Compare overlapping dates element-wise for conflicts
                        mismatches = (
                            ((ex_sub["Open"] - inc_sub["Open"]).abs() > 1e-4) |
                            ((ex_sub["High"] - inc_sub["High"]).abs() > 1e-4) |
                            ((ex_sub["Low"] - inc_sub["Low"]).abs() > 1e-4) |
                            ((ex_sub["Close"] - inc_sub["Close"]).abs() > 1e-4) |
                            ((ex_sub["Volume"] - inc_sub["Volume"]).abs() > 1e-4)
                        )
                        if mismatches.any():
                            bad_dates = list(mismatches[mismatches].index)
                            raise ValueError(f"Conflicting OHLCV values detected during incremental merge for symbol {symbol} on dates {bad_dates}")

                    # Combine non-overlapping existing with incremental
                    df_non_overlap_existing = df_existing[~df_existing["date"].isin(set(df_incr["date"]))]
                    df_combined = pd.concat([df_non_overlap_existing, df_incr], ignore_index=True).sort_values("date").reset_index(drop=True)

                    con = duckdb.connect(str(target_db))
                    try:
                        res = commit_symbol_ingestion(
                            symbol=symbol,
                            df_clean=df_combined,
                            con=con,
                            f_dir=target_f_dir,
                            checkpoint=checkpoint,
                            journal=journal,
                            tx_id=tx_id,
                            checkpoint_p=target_cp,
                            journal_p=target_j
                        )
                        res["incremental"] = True
                        res["new_rows"] = len(df_combined) - len(df_existing)
                        return res
                    finally:
                        con.close()
        except Exception as ex:
            # Fall back to full historical fetch ONLY for recoverable provider network errors
            if "HTTP" in str(ex) or "Connection" in str(ex) or "Timeout" in str(ex):
                pass
            else:
                raise

    # Full historical fetch
    df_raw = yf.download(ticker, start=start_date, end=end_str, progress=False)
    df_clean = validate_and_normalize_ohlcv(df_raw, symbol)

    con = duckdb.connect(str(target_db))
    try:
        res = commit_symbol_ingestion(
            symbol=symbol,
            df_clean=df_clean,
            con=con,
            f_dir=target_f_dir,
            checkpoint=checkpoint,
            journal=journal,
            tx_id=tx_id,
            checkpoint_p=target_cp,
            journal_p=target_j
        )
        res["incremental"] = False
        res["new_rows"] = len(df_clean)
        return res
    finally:
        con.close()

def main():
    parser = argparse.ArgumentParser(description="Master Nifty 500 Historical Data Ingestion Pipeline")
    parser.add_argument("--start-date", type=str, default="2015-01-01", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", type=str, default="2026-10-30", help="End date in YYYY-MM-DD format")
    parser.add_argument("--symbol", type=str, default=None, help="Single symbol to ingest (optional)")
    parser.add_argument("--force", action="store_true", help="Force re-ingestion of already current symbols")
    args = parser.parse_args()

    # Determine target latest date required (yfinance end date is exclusive, so 2026-10-30 requests up through 2026-10-29)
    if args.end_date:
        target_latest_date = (pd.to_datetime(args.end_date) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        target_latest_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # First run recovery on any pending transactions
    print("[+] Checking for pending recovery transactions...")
    recovered = recover_pending_transactions()
    if recovered > 0:
        print(f"[+] Recovered {recovered} pending transactions.")

    symbols_dict = get_nifty_500_universe()
    target_symbols = [args.symbol] if args.symbol else list(symbols_dict.keys())

    print(f"[+] Starting ingestion batch for {len(target_symbols)} constituents (target_latest_date={target_latest_date})...")

    init_duckdb()
    checkpoint = load_checkpoint()

    updated_cnt = 0
    current_cnt = 0
    latest_unavailable_cnt = 0
    blocked_cnt = 0
    failed_cnt = 0

    for idx, sym in enumerate(target_symbols, 1):
        if sym == "BAGMANE":
            print(f"[{idx}/{len(target_symbols)}] BLOCKED: BAGMANE (unlisted on provider API)")
            blocked_cnt += 1
            continue

        cp_info = checkpoint.get(sym, {})
        if not args.force and is_symbol_current(sym, target_latest_date, cp_info, features_dir, duckdb_path):
            print(f"[{idx}/{len(target_symbols)}] CURRENT: {sym} (verified: {cp_info.get('rows', 0)} rows, {cp_info.get('earliest_date')} to {cp_info.get('latest_date')})")
            current_cnt += 1
            continue

        try:
            res = ingest_symbol(sym, start_date=args.start_date, end_date=args.end_date)
            res_latest = res.get("latest_date", "")
            if res_latest >= target_latest_date:
                print(f"[{idx}/{len(target_symbols)}] UPDATED: {sym} ({res['rows']} total rows, earliest {res['earliest_date']} to latest {res['latest_date']})")
                updated_cnt += 1
            else:
                print(f"[{idx}/{len(target_symbols)}] LATEST_UNAVAILABLE: {sym} (provider latest available date {res_latest} < target {target_latest_date}; {res['rows']} rows)")
                latest_unavailable_cnt += 1
        except Exception as ex:
            print(f"[{idx}/{len(target_symbols)}] FAILED: {sym} — {ex}")
            failed_cnt += 1

    print(f"\n[+] Batch complete.")
    print(f"    - UPDATED           : {updated_cnt}")
    print(f"    - CURRENT           : {current_cnt}")
    print(f"    - LATEST_UNAVAILABLE: {latest_unavailable_cnt}")
    print(f"    - BLOCKED           : {blocked_cnt}")
    print(f"    - FAILED            : {failed_cnt}")
    print(f"    - TOTAL             : {len(target_symbols)}")

    if failed_cnt > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
