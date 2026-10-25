"""
================================================================================
TradeMindAI: Unit Test Suite for Market Data Pipeline & Provider Normalization
================================================================================
Verifies that HistoricalBackfillService normalizes yfinance responses, validates
OHLCV geometry, filters malformed/non-finite values, and executes end-to-end
Strategy V2.2 indicator calculations deterministically using mocks and temporary DB.
================================================================================
"""

import pytest
import datetime
import pandas as pd
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.postgres import Base, StockDB, PriceDB
from backend.services.historical_backfill_service import HistoricalBackfillService
from backend.app.services.indicator_service import LocalIndicatorService
from backend.services.signal_engine import SignalEngine
from backend.services.signal_eligibility import is_eligible_buy

def test_mocked_yfinance_normalization_and_geometry_validation():
    """Verify offline deterministic normalization and OHLCV geometry filtering using mocked yfinance response."""
    dates = pd.date_range("2023-01-01", periods=6, freq="B")
    mock_df = pd.DataFrame({
        "open": [100.0, 102.0, 101.0, -10.0, 105.0, 106.0],  # row 3 invalid negative open
        "high": [105.0, 106.0, 100.0, 105.0, 108.0, 109.0],  # row 2 invalid high < low (100 < 104)
        "low": [98.0, 101.0, 104.0, 100.0, 104.0, 105.0],
        "close": [103.0, 104.0, 102.0, 101.0, 107.0, 108.0],
        "volume": [1000, 1200, 1100, 500, 1500, 1600]
    }, index=dates)

    with patch("yfinance.download", return_value=mock_df):
        bars = HistoricalBackfillService.fetch_authentic_source_bars(
            "MOCK_SYM", datetime.datetime(2023, 1, 1), datetime.datetime(2023, 1, 10)
        )

    # 4 valid rows out of 6 (row 2 invalid high < low, row 3 invalid negative open filtered)
    assert len(bars) == 4
    for b in bars:
        assert b["symbol"] == "MOCK_SYM"
        assert b["source"] == "YFINANCE_AUTHENTIC"
        assert b["open"] > 0
        assert b["high"] >= b["low"]
        assert b["close"] > 0
        assert b["volume"] >= 0

def test_mocked_yfinance_empty_response_fails_closed():
    """Verify that an empty or missing provider response returns an empty list without fabricating bars."""
    empty_df = pd.DataFrame()
    with patch("yfinance.download", return_value=empty_df):
        bars = HistoricalBackfillService.fetch_authentic_source_bars(
            "MOCK_EMPTY", datetime.datetime(2023, 1, 1), datetime.datetime(2023, 2, 1)
        )
    assert bars == [], "Expected empty list for empty yfinance response"

def test_mocked_200_bar_lookback_indicator_calculation():
    """Verify that 200+ deterministic bars calculate Strategy V2.2 indicators (EMA200, EMA50, EMA20, SMA20, RSI14, MACD, Bollinger Bands)."""
    dates = pd.date_range("2023-01-01", periods=250, freq="B")
    prices = [200.0 + (i * 0.5) for i in range(250)]
    mock_df = pd.DataFrame({
        "open": [p - 1.0 for p in prices],
        "high": [p + 2.0 for p in prices],
        "low": [p - 2.0 for p in prices],
        "close": prices,
        "volume": [500000 + (i * 100) for i in range(250)]
    }, index=dates)

    with patch("yfinance.download", return_value=mock_df):
        bars = HistoricalBackfillService.fetch_authentic_source_bars(
            "TCS", datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)
        )

    assert len(bars) == 250
    df = pd.DataFrame(bars)
    df.set_index("date", inplace=True)
    df.sort_index(inplace=True)

    metrics = LocalIndicatorService.get_latest_metrics(df)

    assert metrics["close"] == prices[-1]
    assert "rsi_14" in metrics and metrics["rsi_14"] is not None
    assert "ema_20" in metrics and metrics["ema_20"] is not None
    assert "ema_50" in metrics and metrics["ema_50"] is not None
    assert "ema_200" in metrics and metrics["ema_200"] is not None
    assert "macd" in metrics and metrics["macd"] is not None
    assert "bb_upper" in metrics and metrics["bb_upper"] is not None
    assert "atr_14" in metrics and metrics["atr_14"] is not None

def test_pipeline_temporary_db_persistence_and_read_symmetry():
    """Verify read/write database symmetry: persist normalized bars to temporary SQLite DB and query back for signal calculation."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    dates = pd.date_range("2023-01-01", periods=210, freq="B")
    prices = [1000.0 + (i * 1.0) for i in range(210)]
    mock_df = pd.DataFrame({
        "open": [p - 2.0 for p in prices],
        "high": [p + 5.0 for p in prices],
        "low": [p - 3.0 for p in prices],
        "close": prices,
        "volume": [100000 for _ in range(210)]
    }, index=dates)

    with patch("yfinance.download", return_value=mock_df):
        bars = HistoricalBackfillService.fetch_authentic_source_bars(
            "INFY", datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)
        )

    with TestSession() as session:
        db_objs = [PriceDB(
            symbol=b["symbol"], date=b["date"], open=b["open"], high=b["high"],
            low=b["low"], close=b["close"], volume=b["volume"], source=b["source"]
        ) for b in bars]
        session.bulk_save_objects(db_objs)
        session.commit()

        # Read back from temporary database
        persisted_bars = session.query(PriceDB).filter(PriceDB.symbol == "INFY").order_by(PriceDB.date.asc()).all()
        assert len(persisted_bars) == 210

        read_data = [{
            "date": p.date, "open": p.open, "high": p.high, "low": p.low, "close": p.close, "volume": p.volume
        } for p in persisted_bars]

        df = pd.DataFrame(read_data)
        df.set_index("date", inplace=True)
        metrics = LocalIndicatorService.get_latest_metrics(df)

        assert metrics["ema_200"] is not None
        assert metrics["close"] == prices[-1]

@pytest.mark.skip(reason="Live network connectivity smoke test disabled by default in unit suite")
def test_live_yfinance_provider_smoke_test():
    """Separate live network smoke test for yfinance API connectivity."""
    start_dt = datetime.datetime(2023, 1, 1)
    end_dt = datetime.datetime(2023, 6, 1)

    bars = HistoricalBackfillService.fetch_authentic_source_bars("RELIANCE", start_dt, end_dt)

    assert len(bars) > 0, "Expected non-empty authentic price bars for RELIANCE"
    assert bars[0]["symbol"] == "RELIANCE"
    assert bars[0]["source"] == "YFINANCE_AUTHENTIC"
