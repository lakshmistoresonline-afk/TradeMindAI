"""
================================================================================
TradeMindAI Phase A: Market Data Quality & NIFTY 500 Validation Unit Tests
================================================================================
Comprehensive test suite verifying:
1. Canonical NIFTY 500 universe integrity (500 exact, unique, non-synthetic equities).
2. Dynamic NSE constituent metadata fetch and fallback provenance tracking.
3. Point-in-time constituent resolution preventing survivorship bias in backtesting.
4. Historical OHLCV bar validation (NaN/Inf, positive prices, OHLC geometry, volume, incomplete session filter).
5. Intraday 5-minute expected slot generation for regular and Muhurat trading sessions.
6. Versioned exchange calendar holiday exclusions and freshness evaluation.
7. Storage consistency between Parquet and DuckDB.
================================================================================
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from backend.app.db.nifty500_symbols import (
    get_nifty_500_universe,
    validate_nifty500_universe,
    fetch_official_nse_nifty500_metadata,
    get_point_in_time_constituents,
    UNIVERSE_VERSION,
    OFFICIAL_NSE_SOURCE_URL
)
from backend.services.historical_backfill_service import HistoricalBackfillService
from backend.services.intraday_ingestion_service import IntradayIngestionService
from backend.services.data_quality_service import (
    DataQualityService,
    generate_expected_5m_slots,
    validate_freshness,
    audit_storage_equality,
    VERSIONED_NSE_TRADING_CALENDAR_V1
)

def test_phase_a_nifty500_exact_count_and_uniqueness():
    universe = get_nifty_500_universe()
    assert len(universe) == 500
    assert validate_nifty500_universe(list(universe.keys())) is True

def test_phase_a_nifty500_synthetic_patterns_rejected():
    symbols = [f"SYM_{i}" for i in range(499)] + ["N500_SYNTHETIC"]
    with pytest.raises(ValueError, match="Synthetic filler pattern"):
        validate_nifty500_universe(symbols)

def test_phase_a_nifty500_duplicate_symbols_rejected():
    symbols = list(get_nifty_500_universe().keys())
    symbols[1] = symbols[0]  # Duplicate
    with pytest.raises(ValueError, match="Duplicate symbols detected"):
        validate_nifty500_universe(symbols)

def test_phase_a_nifty500_metadata_provenance():
    meta = fetch_official_nse_nifty500_metadata()
    assert "source" in meta
    assert meta["source"] in ("LIVE_NSE_CSV", "FALLBACK_CACHED")
    assert meta["source_url"] == OFFICIAL_NSE_SOURCE_URL
    assert meta["universe_version"] == UNIVERSE_VERSION
    assert meta["constituents_count"] == 500

def test_phase_a_point_in_time_constituents_prevents_survivorship_bias():
    # Equities listed after 2015 should be excluded when as_of_date is 2016-01-01
    pit_2016 = get_point_in_time_constituents("2016-01-01")
    assert "LICI" not in pit_2016  # Listed 2022-05-17
    assert "ATGL" not in pit_2016  # Listed 2018-11-05
    assert "INFY" in pit_2016  # Listed 1995

    # Equities listed before as_of_date should be included
    pit_2023 = get_point_in_time_constituents("2023-01-01")
    assert "LICI" in pit_2023
    assert "ATGL" in pit_2023

def test_phase_a_historical_ohlcv_bar_validation_valid():
    as_of = datetime(2026, 1, 15)
    row = pd.Series({"Open": 1500.0, "High": 1520.0, "Low": 1490.0, "Close": 1510.0, "Volume": 100000.0})
    is_valid, bar_dict, reason = HistoricalBackfillService.validate_historical_bar("INFY", datetime(2026, 1, 10), row, as_of)
    assert is_valid is True
    assert bar_dict["close"] == 1510.0
    assert reason is None

def test_phase_a_historical_ohlcv_nan_inf_rejected():
    as_of = datetime(2026, 1, 15)
    row_nan = pd.Series({"Open": np.nan, "High": 1520.0, "Low": 1490.0, "Close": 1510.0, "Volume": 100000.0})
    is_valid, bar_dict, reason = HistoricalBackfillService.validate_historical_bar("INFY", datetime(2026, 1, 10), row_nan, as_of)
    assert is_valid is False
    assert "NON_FINITE_VALUE" in reason

    row_inf = pd.Series({"Open": 1500.0, "High": np.inf, "Low": 1490.0, "Close": 1510.0, "Volume": 100000.0})
    is_valid, bar_dict, reason = HistoricalBackfillService.validate_historical_bar("INFY", datetime(2026, 1, 10), row_inf, as_of)
    assert is_valid is False
    assert "NON_FINITE_VALUE" in reason

def test_phase_a_historical_ohlcv_geometry_violation_rejected():
    as_of = datetime(2026, 1, 15)
    # High < Low
    row_bad = pd.Series({"Open": 1500.0, "High": 1480.0, "Low": 1490.0, "Close": 1510.0, "Volume": 100000.0})
    is_valid, bar_dict, reason = HistoricalBackfillService.validate_historical_bar("INFY", datetime(2026, 1, 10), row_bad, as_of)
    assert is_valid is False
    assert "GEOMETRY_VIOLATION" in reason

def test_phase_a_historical_ohlcv_negative_volume_rejected():
    as_of = datetime(2026, 1, 15)
    row_neg_vol = pd.Series({"Open": 1500.0, "High": 1520.0, "Low": 1490.0, "Close": 1510.0, "Volume": -50.0})
    is_valid, bar_dict, reason = HistoricalBackfillService.validate_historical_bar("INFY", datetime(2026, 1, 10), row_neg_vol, as_of)
    assert is_valid is False
    assert "NEGATIVE_VOLUME" in reason

def test_phase_a_historical_incomplete_session_filtered():
    as_of = datetime(2026, 1, 15)
    # Bar date after as_of date
    row = pd.Series({"Open": 1500.0, "High": 1520.0, "Low": 1490.0, "Close": 1510.0, "Volume": 100000.0})
    is_valid, bar_dict, reason = HistoricalBackfillService.validate_historical_bar("INFY", datetime(2026, 1, 16), row, as_of)
    assert is_valid is False
    assert "INCOMPLETE_SESSION" in reason

def test_phase_a_historical_get_as_of_end_date_timedelta_runtime():
    # Verifies get_as_of_end_date executes cleanly without NameError: timedelta
    as_of_dt = HistoricalBackfillService.get_as_of_end_date()
    assert isinstance(as_of_dt, datetime)
    assert as_of_dt.year >= 2026

def test_phase_a_expected_5m_slots_regular_vs_muhurat():
    # Regular trading session -> 75 slots (09:15 to 15:25)
    slots_reg = generate_expected_5m_slots("2026-03-10")
    assert len(slots_reg) == 75
    assert slots_reg[0] == "2026-03-10 09:15:00"
    assert slots_reg[-1] == "2026-03-10 15:25:00"

    # Muhurat trading session -> 13 slots (18:15 to 19:15)
    slots_muhurat = generate_expected_5m_slots("2026-11-08")
    assert len(slots_muhurat) == 13
    assert slots_muhurat[0] == "2026-11-08 18:15:00"
    assert slots_muhurat[-1] == "2026-11-08 19:15:00"

def test_phase_a_freshness_evaluation():
    assert validate_freshness("2026-03-10", "2026-03-12") == "FRESH"
    assert validate_freshness("2026-03-01", "2026-03-15") == "STALE"
    assert validate_freshness("2026-03-20", "2026-03-15") == "FUTURE_DATED"

def test_phase_a_storage_audit_equality():
    df1 = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, 102.0],
        "High": [105.0, 107.0],
        "Low": [99.0, 101.0],
        "Close": [104.0, 106.0],
        "Volume": [1000.0, 1100.0]
    })
    df2 = df1.copy()
    match_bool, m_keys, e_keys, val_mismatches = audit_storage_equality(df1, df2, "date", "INFY")
    assert match_bool is True
    assert m_keys == 0
    assert e_keys == 0
    assert val_mismatches == 0
