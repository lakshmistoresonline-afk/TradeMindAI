import os
import pytest
import duckdb
import pandas as pd
import numpy as np
from pathlib import Path
from backend.services.intraday_ingestion_service import IntradayIngestionService

def test_validate_5m_candles_valid():
    timestamps = pd.date_range("2026-10-30 09:15:00", periods=5, freq="5min", tz="Asia/Kolkata")
    df_raw = pd.DataFrame({
        "timestamp": timestamps,
        "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
        "High": [105.0, 106.0, 107.0, 108.0, 109.0],
        "Low": [95.0, 96.0, 97.0, 98.0, 99.0],
        "Close": [102.0, 103.0, 104.0, 105.0, 106.0],
        "Volume": [1000, 2000, 3000, 4000, 5000]
    })
    df_clean, stats = IntradayIngestionService.validate_5m_candles(df_raw, "TEST_SYM")
    assert len(df_clean) == 5
    assert list(df_clean.columns) == ["timestamp", "Open", "High", "Low", "Close", "Volume"]
    assert stats["accepted_count"] == 5
    assert stats["rejected_count"] == 0

def test_validate_5m_candles_geometry_violation_filtering():
    timestamps = pd.date_range("2026-10-30 09:15:00", periods=1, freq="5min", tz="Asia/Kolkata")
    df_raw = pd.DataFrame({
        "timestamp": timestamps,
        "Open": [100.0],
        "High": [90.0], # High < Low geometry violation
        "Low": [95.0],
        "Close": [102.0],
        "Volume": [1000]
    })
    with pytest.raises(ValueError, match="No valid 5-minute OHLCV candles remaining"):
        IntradayIngestionService.validate_5m_candles(df_raw, "TEST_SYM")

def test_sync_symbol_5m_idempotent_persistence(tmp_path):
    db_path = tmp_path / "test.duckdb"
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()

    # Pre-populate raw dataframe mocking yfinance
    timestamps = pd.date_range("2026-10-30 09:15:00", periods=3, freq="5min", tz="Asia/Kolkata")
    df_mock = pd.DataFrame({
        "timestamp": timestamps,
        "Open": [100.0, 101.0, 102.0],
        "High": [105.0, 106.0, 107.0],
        "Low": [95.0, 96.0, 97.0],
        "Close": [102.0, 103.0, 104.0],
        "Volume": [1000, 2000, 3000]
    })

    # Validate candles
    df_clean, stats = IntradayIngestionService.validate_5m_candles(df_mock, "TEST_5M")
    assert len(df_clean) == 3

    IntradayIngestionService.init_intraday_duckdb(db_path)
    con = duckdb.connect(str(db_path))

    # Perform DuckDB insertion
    con.execute("BEGIN TRANSACTION")
    for _, row in df_clean.iterrows():
        con.execute("INSERT INTO intraday_5m_ohlcv VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            "TEST_5M", str(row["timestamp"]), float(row["Open"]), float(row["High"]),
            float(row["Low"]), float(row["Close"]), float(row["Volume"]), "MOCK", "TS"
        ))
    con.execute("COMMIT")

    rows_1 = con.execute("SELECT count(*) FROM intraday_5m_ohlcv WHERE symbol = 'TEST_5M'").fetchone()[0]
    assert rows_1 == 3
    con.close()
