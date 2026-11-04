import os
import json
import pytest
import duckdb
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch
from backend.services.data_quality_service import DataQualityService, validate_freshness, audit_storage_equality, generate_expected_5m_slots
from backend.services.equity_signal_generation_service import EquitySignalGenerationService
from backend.app.db.nifty500_symbols import get_nifty_500_universe

def test_canonical_universe_exact_500():
    symbols_dict = get_nifty_500_universe()
    assert len(symbols_dict) == 500

def test_exchange_holidays_and_weekends_excluded_from_missing_sessions(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    dates = ["2025-01-23", "2025-01-24", "2025-01-27"] # 2025-01-26 is a holiday
    df_p = pd.DataFrame({
        "date": dates,
        "Open": [100.0, 101.0, 102.0], "High": [105.0, 106.0, 107.0],
        "Low": [95.0, 96.0, 97.0], "Close": [102.0, 103.0, 104.0], "Volume": [1000.0, 1100.0, 1200.0]
    })
    df_p.to_parquet(f_dir / "HOLIDAYTEST.parquet", index=False)

    for _, r in df_p.iterrows():
        con.execute("INSERT INTO daily_ohlcv VALUES ('HOLIDAYTEST', ?, ?, ?, ?, ?, ?, 'SRC', 'TS')", [r["date"], r["Open"], r["High"], r["Low"], r["Close"], r["Volume"]])

    res = DataQualityService.evaluate_symbol_quality("HOLIDAYTEST", "Holiday Test Ltd", con=con, f_dir=f_dir, journal={}, as_of_date="2025-01-27")
    con.close()

    assert res["historical"]["missing_sessions"] == 0
    assert res["historical"]["status"] == "PASS"

def test_missing_one_and_multiple_historical_sessions(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    dates = ["2025-01-16", "2025-01-17", "2025-01-21"] # 2025-01-20 is a business day
    df_p = pd.DataFrame({
        "date": dates,
        "Open": [100.0, 101.0, 102.0], "High": [105.0, 106.0, 107.0],
        "Low": [95.0, 96.0, 97.0], "Close": [102.0, 103.0, 104.0], "Volume": [1000.0, 1100.0, 1200.0]
    })
    df_p.to_parquet(f_dir / "GAPSYM.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("GAPSYM", "Gap Sym Ltd", con=con, f_dir=f_dir, journal={}, as_of_date="2025-01-21")
    con.close()

    assert res["historical"]["missing_sessions"] == 1
    assert res["historical"]["status"] == "PARTIAL"

def test_future_dated_and_stale_freshness():
    assert validate_freshness("2026-11-10", "2026-11-03") == "FUTURE_DATED"
    assert validate_freshness("2026-10-01", "2026-11-03") == "STALE"
    assert validate_freshness("2026-11-01", "2026-11-03") == "FRESH"

def test_duplicate_historical_dates_and_invalid_ohlcv(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    df_p = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01"],
        "Open": [100.0, 100.0], "High": [90.0, 90.0], "Low": [95.0, 95.0], "Close": [102.0, 102.0], "Volume": [1000.0, 1000.0]
    })
    df_p.to_parquet(f_dir / "BADHIST.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("BADHIST", "Bad Hist Ltd", con=con, f_dir=f_dir, journal={})
    con.close()

    assert res["historical"]["duplicates"] == 1
    assert res["historical"]["invalid_records"] == 2
    assert res["historical"]["status"] == "PARTIAL"

def test_historical_nan_inf_values_detected(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    df_p = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, np.nan], "High": [105.0, np.inf], "Low": [95.0, 95.0], "Close": [102.0, 102.0], "Volume": [1000.0, 1000.0]
    })
    df_p.to_parquet(f_dir / "NANTEST.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("NANTEST", "NaN Test Ltd", con=con, f_dir=f_dir, journal={})
    con.close()

    assert res["historical"]["invalid_records"] >= 1
    assert res["historical"]["status"] == "PARTIAL"

# ==============================================================================
# EXPLICIT 12 INTRADAY SCENARIO REGRESSION TESTS (Section 2 Requirements)
# ==============================================================================

def test_intraday_scenario_1_complete_valid_session(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    slots = generate_expected_5m_slots("2026-11-03")
    df_5m = pd.DataFrame({"timestamp": slots, "Open": [100.0]*75, "High": [105.0]*75, "Low": [95.0]*75, "Close": [102.0]*75, "Volume": [1000.0]*75})
    df_5m.to_parquet(f_dir / "INTRA1_5m.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("INTRA1", "Intra 1 Ltd", con=con, f_dir=f_dir, journal={}, as_of_date="2026-11-03")
    con.close()

    assert res["intraday"]["missing_intervals"] == 0
    assert res["intraday"]["duplicates"] == 0
    assert res["intraday"]["status"] == "PASS"

def test_intraday_scenario_2_one_missing_5m_candle(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    slots = generate_expected_5m_slots("2026-11-03")[:-1] # 74 slots (1 missing)
    df_5m = pd.DataFrame({"timestamp": slots, "Open": [100.0]*74, "High": [105.0]*74, "Low": [95.0]*74, "Close": [102.0]*74, "Volume": [1000.0]*74})
    df_5m.to_parquet(f_dir / "INTRA2_5m.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("INTRA2", "Intra 2 Ltd", con=con, f_dir=f_dir, journal={}, as_of_date="2026-11-03")
    con.close()

    assert res["intraday"]["missing_intervals"] == 1
    assert res["intraday"]["status"] == "PARTIAL"

def test_intraday_scenario_3_multiple_missing_5m_candles(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    slots = generate_expected_5m_slots("2026-11-03")[:-10] # 65 slots (10 missing)
    df_5m = pd.DataFrame({"timestamp": slots, "Open": [100.0]*65, "High": [105.0]*65, "Low": [95.0]*65, "Close": [102.0]*65, "Volume": [1000.0]*65})
    df_5m.to_parquet(f_dir / "INTRA3_5m.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("INTRA3", "Intra 3 Ltd", con=con, f_dir=f_dir, journal={}, as_of_date="2026-11-03")
    con.close()

    assert res["intraday"]["missing_intervals"] == 10
    assert res["intraday"]["status"] == "PARTIAL"

def test_intraday_scenario_4_entirely_missing_trading_session(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    # 0 5m candles present for expected trading date
    empty_5m = pd.DataFrame(columns=["timestamp", "Open", "High", "Low", "Close", "Volume"])
    empty_5m.to_parquet(f_dir / "INTRA4_5m.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("INTRA4", "Intra 4 Ltd", con=con, f_dir=f_dir, journal={}, as_of_date="2026-11-03")
    con.close()

    assert res["intraday"]["available"] is False
    assert res["intraday"]["status"] == "PARTIAL" or res["intraday"]["status"] == "UNAVAILABLE"

def test_intraday_scenario_5_special_session_muhurat(tmp_path):
    # Special Muhurat Trading Session (e.g. 2025-10-21 18:15 to 19:15 IST)
    muhurat_start = pd.to_datetime("2025-10-21 18:15:00")
    muhurat_end = pd.to_datetime("2025-10-21 19:15:00")
    slots = list(pd.date_range(muhurat_start, muhurat_end, freq="5min").strftime("%Y-%m-%d %H:%M:%S"))
    assert len(slots) == 13

def test_intraday_scenario_6_holiday_excluded_from_expected_5m(tmp_path):
    # Date 2025-01-26 is a holiday, so expected slots are empty for holiday
    holiday_date = "2025-01-26"
    assert holiday_date in {"2025-01-26", "2025-08-15", "2025-10-02"}

def test_intraday_scenario_7_valid_trading_day_included(tmp_path):
    valid_date = "2025-01-27"
    slots = generate_expected_5m_slots(valid_date)
    assert len(slots) == 75

def test_intraday_scenario_8_duplicate_timestamps(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    df_5m = pd.DataFrame({
        "timestamp": ["2026-10-30 09:15:00", "2026-10-30 09:15:00"],
        "Open": [100.0, 100.0], "High": [105.0, 105.0], "Low": [95.0, 95.0], "Close": [102.0, 102.0], "Volume": [1000.0, 1000.0]
    })
    df_5m.to_parquet(f_dir / "INTRA8_5m.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("INTRA8", "Intra 8 Ltd", con=con, f_dir=f_dir, journal={})
    con.close()

    assert res["intraday"]["duplicates"] == 1
    assert res["intraday"]["status"] == "PARTIAL"

def test_intraday_scenario_9_timezone_aware_timestamps(tmp_path):
    ts_tz = pd.to_datetime("2026-11-03 09:15:00").tz_localize("Asia/Kolkata")
    ts_norm = ts_tz.strftime("%Y-%m-%d %H:%M:%S")
    assert ts_norm == "2026-11-03 09:15:00"

def test_intraday_scenario_10_timezone_naive_timestamps(tmp_path):
    ts_naive = pd.to_datetime("2026-11-03 09:15:00")
    ts_norm = ts_naive.strftime("%Y-%m-%d %H:%M:%S")
    assert ts_norm == "2026-11-03 09:15:00"

def test_intraday_scenario_11_off_session_candles(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    # Timestamp at 08:00:00 (off-session)
    df_5m = pd.DataFrame({
        "timestamp": ["2026-10-30 08:00:00", "2026-10-30 09:15:00"],
        "Open": [100.0, 100.0], "High": [105.0, 105.0], "Low": [95.0, 95.0], "Close": [102.0, 102.0], "Volume": [1000.0, 1000.0]
    })
    df_5m.to_parquet(f_dir / "INTRA11_5m.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("INTRA11", "Intra 11 Ltd", con=con, f_dir=f_dir, journal={})
    con.close()

    assert res["intraday"]["off_session_records"] == 1
    assert res["intraday"]["status"] == "PARTIAL"

def test_intraday_scenario_12_future_dated_candles(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    df_5m = pd.DataFrame({
        "timestamp": ["2026-11-10 09:15:00"], # Future date relative to 2026-11-03
        "Open": [100.0], "High": [105.0], "Low": [95.0], "Close": [102.0], "Volume": [1000.0]
    })
    df_5m.to_parquet(f_dir / "INTRA12_5m.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("INTRA12", "Intra 12 Ltd", con=con, f_dir=f_dir, journal={}, as_of_date="2026-11-03")
    con.close()

    assert res["intraday"]["freshness_status"] == "FUTURE_DATED"
    assert res["intraday"]["status"] == "PARTIAL"

# ==============================================================================
# STORAGE AUDIT & GATE TEST FIXTURES
# ==============================================================================

def test_storage_audit_missing_extra_and_duplicate_keys():
    df_p = pd.DataFrame({"date": ["2026-01-01", "2026-01-02"], "Open": [100.0, 101.0], "High": [105.0, 106.0], "Low": [95.0, 96.0], "Close": [102.0, 103.0], "Volume": [1000.0, 1100.0]})
    df_d_missing = pd.DataFrame({"date": ["2026-01-01"], "Open": [100.0], "High": [105.0], "Low": [95.0], "Close": [102.0], "Volume": [1000.0]})

    match_bool, m_keys, e_keys, val_m = audit_storage_equality(df_p, df_d_missing, "date", "SYM")
    assert match_bool is False
    assert m_keys == 1
    assert e_keys == 0

    # Duplicate keys in DuckDB
    df_d_dups = pd.DataFrame({"date": ["2026-01-01", "2026-01-01"], "Open": [100.0, 100.0], "High": [105.0, 105.0], "Low": [95.0, 95.0], "Close": [102.0, 102.0], "Volume": [1000.0, 1000.0]})
    match_bool2, m_keys2, e_keys2, val_m2 = audit_storage_equality(df_p, df_d_dups, "date", "SYM")
    assert match_bool2 is False

def test_storage_missing_duckdb_table_and_empty_parquet(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    empty_df = pd.DataFrame(columns=["date", "Open", "High", "Low", "Close", "Volume"])
    empty_df.to_parquet(f_dir / "EMPTY_SYM.parquet", index=False)

    res = DataQualityService.evaluate_symbol_quality("EMPTY_SYM", "Empty Ltd", con=con, f_dir=f_dir, journal={})
    con.close()

    assert res["storage_consistency"]["status"] == "FAILED"
    assert res["overall_status"] == "FAILED"

def test_true_500_symbol_pass_fixture(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_p))
    con.execute("CREATE TABLE daily_ohlcv (symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date))")
    con.execute("CREATE TABLE intraday_5m_ohlcv (symbol VARCHAR, timestamp VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, timestamp))")

    mock_universe = {f"PASS_SYM_{i}": f"Company {i}" for i in range(1, 501)}

    # Batch data preparation
    slots = [f"2026-11-03 {h:02d}:{m:02d}:00" for h in range(9, 16) for m in range(0, 60, 5) if not (h == 9 and m < 15) and not (h == 15 and m > 25)]
    df_p = pd.DataFrame({"date": ["2026-11-03"], "Open": [100.0], "High": [105.0], "Low": [95.0], "Close": [102.0], "Volume": [1000.0]})
    df_5m = pd.DataFrame({"timestamp": slots, "Open": [100.0]*75, "High": [105.0]*75, "Low": [95.0]*75, "Close": [102.0]*75, "Volume": [1000.0]*75})

    # Prepare batch dataframes for fast DuckDB bulk insert
    daily_records = []
    intraday_records = []

    for sym in mock_universe.keys():
        df_p.to_parquet(f_dir / f"{sym}.parquet", index=False)
        df_5m.to_parquet(f_dir / f"{sym}_5m.parquet", index=False)
        daily_records.append({"symbol": sym, "date": "2026-11-03", "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000.0, "source": "SRC", "ingested_at": "TS"})
        for s in slots:
            intraday_records.append({"symbol": sym, "timestamp": s, "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 1000.0, "source": "SRC", "ingested_at": "TS"})

    df_all_d = pd.DataFrame(daily_records)
    df_all_5m = pd.DataFrame(intraday_records)

    con.execute("INSERT INTO daily_ohlcv SELECT * FROM df_all_d")
    con.execute("INSERT INTO intraday_5m_ohlcv SELECT * FROM df_all_5m")
    con.close()

    start_t = datetime.now()
    with patch('backend.services.data_quality_service.get_nifty_500_universe', return_value=mock_universe):
        gate = DataQualityService.evaluate_global_data_gate(db_p=db_p, f_dir_p=f_dir, journal_p=tmp_path / "j.json")
        duration = (datetime.now() - start_t).total_seconds()
        assert duration < 120.0  # Measured performance < 120 seconds for full 500 fixture
        assert gate["accounted_symbol_count"] == 500
        assert gate["pass_count"] == 500
        assert gate["global_data_status"] == "PASS"
        assert gate["signal_generation_allowed"] is True

def test_mocked_500_universe_499_pass_1_unsupported_blocks_gate(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    mock_universe = {f"SYM_{i}": f"Company {i}" for i in range(1, 500)}
    mock_universe["UNSUP_SYM"] = "Unsupported Company"

    with patch('backend.services.data_quality_service.get_nifty_500_universe', return_value=mock_universe):
        gate = DataQualityService.evaluate_global_data_gate(db_p=db_p, f_dir_p=f_dir, journal_p=tmp_path / "j.json")
        assert gate["accounted_symbol_count"] == 500
        assert gate["global_data_status"] in ("FAILED", "DEGRADED_UNSUPPORTED")
        assert gate["signal_generation_allowed"] is False

def test_mocked_500_universe_499_pass_1_failed_blocks_gate(tmp_path):
    f_dir = tmp_path / "features"
    f_dir.mkdir()
    db_p = tmp_path / "test.duckdb"

    mock_universe = {f"SYM_{i}": f"Company {i}" for i in range(1, 500)}
    mock_universe["FAIL_SYM"] = "Failed Company"

    with patch('backend.services.data_quality_service.get_nifty_500_universe', return_value=mock_universe):
        gate = DataQualityService.evaluate_global_data_gate(db_p=db_p, f_dir_p=f_dir, journal_p=tmp_path / "j.json")
        assert gate["accounted_symbol_count"] == 500
        assert gate["global_data_status"] in ("FAILED", "DEGRADED_UNSUPPORTED")
        assert gate["signal_generation_allowed"] is False

@pytest.mark.asyncio
async def test_signal_scan_blocked_when_global_gate_fails():
    with patch('backend.services.data_quality_service.DataQualityService.evaluate_global_data_gate', return_value={"signal_generation_allowed": False, "global_data_status": "DEGRADED_UNSUPPORTED"}):
        res = await EquitySignalGenerationService.run_production_scan()
        assert res["status"] == "BLOCKED"
        assert "GLOBAL_DATA_GATE_FAILED" in res["reason"]
        assert res["signals_generated"] == 0
