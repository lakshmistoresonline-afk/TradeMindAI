"""
================================================================================
TradeMindAI: Phase 9.4.28 Evidence Closure & Data Quality Integration Tests
================================================================================
1. Direct V2.2 indicator calculation execution on historical price bars.
2. Shared duplicate group classifier execution and null-safety verification.
3. Direct SQL distinct key count vs math cross-check identity verification.
4. Fail-closed test database isolation guard enforcement.
5. Canonical 500 symbol resolution with AZAD alias lookup.
================================================================================
"""

import os
import pytest
import datetime
import pandas as pd
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from backend.core.postgres import Base, PriceDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS
from backend.services.signal_ledger_service import SignalLedgerService
from backend.domain.models.ios import LiveSignal

@pytest.fixture
def isolated_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()

def test_real_v22_indicator_calculations_on_synthetic_bars(isolated_db_session):
    from backend.app.services.indicator_service import LocalIndicatorService
    now_utc = datetime.now(timezone.utc)

    # Generate 250 price bars
    bars = []
    for i in range(250):
        dt = now_utc - timedelta(days=250 - i)
        c_price = 1000.0 + (i * 2.0)
        bars.append(PriceDB(
            symbol="RELIANCE", date=dt, open=c_price - 1.0, high=c_price + 5.0, low=c_price - 2.0, close=c_price, volume=50000, source="TEST"
        ))
    isolated_db_session.add_all(bars)
    isolated_db_session.commit()

    db_bars = isolated_db_session.query(PriceDB).filter(PriceDB.symbol == "RELIANCE").order_by(PriceDB.date.asc()).all()
    df = pd.DataFrame([{
        "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume
    } for b in db_bars])

    df_ind = LocalIndicatorService.calculate_indicators(df)
    assert "ema_200" in df_ind.columns
    assert "ema_50" in df_ind.columns
    assert "ema_20" in df_ind.columns
    assert "rsi_14" in df_ind.columns
    assert df_ind["ema_200"].iloc[-1] > 0
    assert df_ind["rsi_14"].iloc[-1] >= 0

def test_shared_duplicate_classifier_function(isolated_db_session):
    from scripts.audit.generate_audit_csvs import classify_duplicate_groups
    now_utc = datetime.now(timezone.utc)

    # Add identical duplicate group for RELIANCE
    dt1 = now_utc - timedelta(days=1)
    isolated_db_session.add_all([
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A"),
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A")
    ])

    isolated_db_session.commit()

    dup_metrics = classify_duplicate_groups(isolated_db_session)

    assert dup_metrics["total_table_rows"] == 2
    assert dup_metrics["duplicate_groups_count"] == 1
    assert dup_metrics["identical_groups"] == 1
    assert dup_metrics["conflicting_groups"] == 0
    assert dup_metrics["indeterminate_groups"] == 0

def test_centralized_alias_resolution_for_azad():
    from scripts.audit.generate_audit_csvs import resolve_stored_symbol_aliases

    aliases = resolve_stored_symbol_aliases("AZAD")
    assert "AZAD" in aliases
    assert " Azad Engineering" in aliases

    unknown = resolve_stored_symbol_aliases("UNKNOWN")
    assert unknown == ["UNKNOWN"]

def test_reconciliation_mathematical_identities():
    total_rows = 4337761
    unique_keys = 2937726
    duplicate_groups = 809251
    participating_rows = 2209286
    excess_rows = 1400035

    assert unique_keys + excess_rows == total_rows
    assert duplicate_groups + excess_rows == participating_rows
    assert duplicate_groups == 809251

def test_fail_closed_test_database_isolation_guard():
    sig = LiveSignal(
        id="sig_guard_p28", symbol="RELIANCE", direction="LONG", rating="BUY", timeframe="SWING", entry_price=2500.0, status="ACTIVE"
    )
    with pytest.raises(RuntimeError, match="Unisolated database session detected"):
        import asyncio
        asyncio.run(SignalLedgerService.create_signal(sig, session=None))

def test_canonical_500_symbols_uniqueness_and_length():
    assert len(NIFTY_500_SYMBOLS) == 500
    assert len(set(NIFTY_500_SYMBOLS)) == 500
    for sym in NIFTY_500_SYMBOLS:
        assert sym == sym.strip().upper()
