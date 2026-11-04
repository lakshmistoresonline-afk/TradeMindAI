"""
================================================================================
TradeMindAI: Hardened 5-Minute Intraday Market-Data Ingestion Service (v3.0)
================================================================================
1. Fetches real 5-minute OHLCV candles for canonical Nifty 500 equities from yfinance provider API.
2. Validates Asia/Kolkata timestamps against NSE market hours (09:15 to 15:30 IST) and 5m alignment (minute % 5 == 0).
3. Handles both timezone-naive and timezone-aware provider timestamps safely.
4. Rejects duplicates, non-finite values (NaN/Inf), negative volume, non-positive prices, and geometry violations.
5. Idempotently persists validated 5-minute candles into DuckDB table `intraday_5m_ohlcv` via
   `INSERT INTO ... ON CONFLICT (symbol, timestamp) DO UPDATE` transactional upserts.
6. Idempotently updates per-symbol Parquet files `backend/data/features/{symbol}_5m.parquet` using atomic
   temporary file creation and atomic replacement (`os.replace`).
7. Enforces validate_mutation_target() before modifying storage files.
================================================================================
"""

import os
import sys
import time
import duckdb
import hashlib
import tempfile
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime, timezone, time as dtime
import pytz

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.db.nifty500_symbols import get_nifty_500_universe
from backend.core.mutation_guard import validate_mutation_target
from scripts.ingest_historical_nifty500 import get_provider_ticker

duckdb_path = root_dir / "backend" / "data" / "analytical.duckdb"
features_dir = root_dir / "backend" / "data" / "features"

KOLKATA_TZ = pytz.timezone("Asia/Kolkata")

class IntradayIngestionService:

    @staticmethod
    def init_intraday_duckdb(db_p: Path = None):
        target_p = db_p or duckdb_path
        validate_mutation_target(target_p)
        target_p.parent.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect(str(target_p))
        con.execute("""
            CREATE TABLE IF NOT EXISTS intraday_5m_ohlcv (
                symbol VARCHAR,
                timestamp VARCHAR,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE,
                source VARCHAR,
                ingested_at VARCHAR,
                PRIMARY KEY (symbol, timestamp)
            )
        """)
        # Ensure unique constraint index exists
        try:
            con.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_intraday_5m_sym_ts ON intraday_5m_ohlcv (symbol, timestamp)")
        except Exception:
            pass
        con.close()

    @staticmethod
    def validate_5m_candles(df_raw: pd.DataFrame, symbol: str) -> tuple[pd.DataFrame, dict]:
        rejection_reasons = []
        if df_raw is None or df_raw.empty:
            raise ValueError(f"No 5-minute intraday data returned for symbol '{symbol}'")

        df_clean = df_raw.copy()

        # Flatten multi-index columns if present
        if isinstance(df_clean.columns, pd.MultiIndex):
            df_clean.columns = [c[0] if isinstance(c, tuple) else c for c in df_clean.columns]

        # Reset index if datetime is in index
        if isinstance(df_clean.index, pd.DatetimeIndex):
            df_clean = df_clean.reset_index()

        col_map = {}
        for c in df_clean.columns:
            c_str = str(c).strip().lower()
            if c_str in ["datetime", "date", "timestamp", "index"]:
                col_map[c] = "timestamp"
            elif c_str == "open":
                col_map[c] = "Open"
            elif c_str == "high":
                col_map[c] = "High"
            elif c_str == "low":
                col_map[c] = "Low"
            elif c_str == "close":
                col_map[c] = "Close"
            elif c_str == "volume":
                col_map[c] = "Volume"

        df_clean = df_clean.rename(columns=col_map)
        req_cols = ["timestamp", "Open", "High", "Low", "Close", "Volume"]

        if not all(col in df_clean.columns for col in req_cols):
            missing = [c for c in req_cols if c not in df_clean.columns]
            raise ValueError(f"Missing required 5m OHLCV columns for symbol '{symbol}': {missing}")

        # Check non-finite values (NaN / Inf)
        num_cols = ["Open", "High", "Low", "Close", "Volume"]
        nan_mask = df_clean[num_cols].isna().any(axis=1) | np.isinf(df_clean[num_cols].to_numpy()).any(axis=1)
        if nan_mask.sum() > 0:
            rejection_reasons.append(f"Rejected {nan_mask.sum()} non-finite/NaN rows")
            df_clean = df_clean[~nan_mask]

        if df_clean.empty:
            raise ValueError(f"No valid 5-minute OHLCV candles remaining for symbol '{symbol}' after non-finite filtering")

        # Format ISO timestamp in Asia/Kolkata timezone (handling naive vs tz-aware)
        ts_s = pd.to_datetime(df_clean["timestamp"])
        if ts_s.dt.tz is None:
            ts_s = ts_s.dt.tz_localize("Asia/Kolkata")
        else:
            ts_s = ts_s.dt.tz_convert("Asia/Kolkata")

        df_clean["dt_obj"] = ts_s
        df_clean["timestamp"] = ts_s.dt.strftime("%Y-%m-%d %H:%M:%S")

        # Report and reject duplicates
        dup_mask = df_clean["timestamp"].duplicated(keep="last")
        dup_count = dup_mask.sum()
        if dup_count > 0:
            rejection_reasons.append(f"Rejected {dup_count} duplicate timestamp rows")
            df_clean = df_clean[~dup_mask]

        # 5-minute alignment check (minute % 5 == 0 and second == 0)
        align_mask = (df_clean["dt_obj"].dt.minute % 5 == 0) & (df_clean["dt_obj"].dt.second == 0)
        unaligned_count = (~align_mask).sum()
        if unaligned_count > 0:
            rejection_reasons.append(f"Rejected {unaligned_count} unaligned 5-minute timestamp rows")
            df_clean = df_clean[align_mask]

        # Filter future-dated candles
        now_kolkata = datetime.now(KOLKATA_TZ)
        future_mask = df_clean["dt_obj"] > now_kolkata
        future_count = future_mask.sum()
        if future_count > 0:
            rejection_reasons.append(f"Rejected {future_count} future-dated candle rows")
            df_clean = df_clean[~future_mask]

        # Filter NSE market hours (09:15 to 15:30 IST)
        market_mask = (df_clean["dt_obj"].dt.time >= dtime(9, 15)) & (df_clean["dt_obj"].dt.time <= dtime(15, 30))
        out_market_count = (~market_mask).sum()
        if out_market_count > 0:
            rejection_reasons.append(f"Rejected {out_market_count} out-of-market-hours rows")
            df_clean = df_clean[market_mask]

        if df_clean.empty:
            raise ValueError(f"No valid 5-minute OHLCV candles remaining for symbol '{symbol}' after timestamp validation")

        # Geometry validation
        geom_mask = (df_clean["High"] >= df_clean["Low"]) & (df_clean["High"] >= df_clean["Open"]) & (df_clean["High"] >= df_clean["Close"]) & (df_clean["Low"] <= df_clean["Open"]) & (df_clean["Low"] <= df_clean["Close"])
        bad_geom_count = (~geom_mask).sum()
        if bad_geom_count > 0:
            rejection_reasons.append(f"Rejected {bad_geom_count} OHLC geometry violation rows")
            df_clean = df_clean[geom_mask]

        if df_clean.empty:
            raise ValueError(f"No valid 5-minute OHLCV candles remaining for symbol '{symbol}' after geometry validation")

        # Price and volume validity
        price_cols = ["Open", "High", "Low", "Close"]
        invalid_price_mask = (df_clean[price_cols] <= 0).any(axis=1) | (df_clean["Volume"] < 0)
        invalid_price_count = invalid_price_mask.sum()
        if invalid_price_count > 0:
            rejection_reasons.append(f"Rejected {invalid_price_count} non-positive price/volume rows")
            df_clean = df_clean[~invalid_price_mask]

        stats = {
            "accepted_count": len(df_clean),
            "rejected_count": len(df_raw) - len(df_clean),
            "rejection_reasons": rejection_reasons
        }

        return df_clean[req_cols].sort_values("timestamp").reset_index(drop=True), stats

    @classmethod
    def sync_symbol_5m(cls, symbol: str, period: str = "1d", db_p: Path = None, f_dir_p: Path = None, max_retries: int = 3) -> dict:
        target_db = db_p or duckdb_path
        target_f_dir = f_dir_p or features_dir

        cls.init_intraday_duckdb(target_db)

        ticker = get_provider_ticker(symbol)
        df_raw = None
        last_ex = None

        # Bounded retry with exponential backoff for provider fetch
        for attempt in range(1, max_retries + 1):
            try:
                df_raw = yf.download(ticker, period=period, interval="5m", progress=False)
                if df_raw is not None and not df_raw.empty:
                    break
            except Exception as ex:
                last_ex = ex
                if attempt < max_retries:
                    time.sleep(attempt * 1.5)

        if df_raw is None or df_raw.empty:
            err_msg = f"INTRADAY_PROVIDER_UNSUPPORTED: Provider API returned no 5m data for symbol '{symbol}'"
            if last_ex:
                err_msg += f" ({last_ex})"
            raise ValueError(err_msg)

        df_clean, stats = cls.validate_5m_candles(df_raw, symbol)

        # Transactional ON CONFLICT UPSERT in DuckDB
        con = duckdb.connect(str(target_db))
        tx_id = hashlib.md5(f"5m_{symbol}_{time.time()}".encode()).hexdigest()[:12]
        source_tag = f"5M_SYNC_{tx_id}"
        ingested_at = datetime.now(timezone.utc).isoformat()

        min_ts = str(df_clean["timestamp"].min())
        max_ts = str(df_clean["timestamp"].max())

        con.execute("BEGIN TRANSACTION")
        insert_rows = []
        for _, row in df_clean.iterrows():
            insert_rows.append((
                symbol, str(row["timestamp"]), float(row["Open"]), float(row["High"]),
                float(row["Low"]), float(row["Close"]), float(row["Volume"]), source_tag, ingested_at
            ))

        con.executemany("""
            INSERT INTO intraday_5m_ohlcv VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (symbol, timestamp) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                source = EXCLUDED.source,
                ingested_at = EXCLUDED.ingested_at
        """, insert_rows)
        con.execute("COMMIT")
        con.close()

        # Atomic Parquet temporary file creation and replacement
        target_parquet = target_f_dir / f"{symbol}_5m.parquet"
        validate_mutation_target(target_parquet)

        fd, tmp_parquet_str = tempfile.mkstemp(dir=str(target_f_dir), prefix=f"tmp_5m_{symbol}_", suffix=".parquet")
        os.close(fd)
        tmp_parquet = Path(tmp_parquet_str)

        try:
            if target_parquet.exists():
                df_existing = pd.read_parquet(target_parquet)
                df_combined = pd.concat([df_existing, df_clean], ignore_index=True)
                df_combined = df_combined.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp").reset_index(drop=True)
                df_combined.to_parquet(tmp_parquet)
            else:
                df_clean.to_parquet(tmp_parquet)

            # Atomic replace
            os.replace(tmp_parquet, target_parquet)
        except Exception as ex:
            if tmp_parquet.exists():
                try: os.unlink(tmp_parquet)
                except Exception: pass
            raise RuntimeError(f"Failed atomic Parquet persistence for 5m symbol '{symbol}': {ex}") from ex

        return {
            "symbol": symbol,
            "status": "SUCCESS",
            "candles_fetched": len(df_raw),
            "candles_persisted": stats["accepted_count"],
            "candles_rejected": stats["rejected_count"],
            "rejection_reasons": stats["rejection_reasons"],
            "earliest_timestamp": min_ts,
            "latest_timestamp": max_ts,
            "source": source_tag
        }
