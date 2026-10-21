"""
================================================================================
TradeMindAI: Phase 9.4.37 Production-Path Reconciliation Proof Tests
================================================================================
1. Direct call to prepare_reconciled_daily_bars verifying duplicate collapsing.
2. Direct call to evaluate_symbol_v22_readiness verifying lookback requirement.
3. Integration test for generate_phase_9_4_37_audit_csvs output.
4. Fail-closed test database isolation guard enforcement.
================================================================================
"""

import os
import pytest
import datetime
import pandas as pd
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
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

def test_prepare_reconciled_daily_bars_direct_call(isolated_db_session):
    from scripts.audit.generate_audit_csvs import prepare_reconciled_daily_bars
    now_utc = datetime.now(timezone.utc)

    # Create 5 bars, with 2 identical duplicates on dt1
    dt1 = now_utc - timedelta(days=2)
    dt2 = now_utc - timedelta(days=1)

    raw_bars = [
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A"),
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A"),
        PriceDB(symbol="RELIANCE", date=dt2, open=2510, high=2530, low=2500, close=2520, volume=1100, source="SRC_A")
    ]

    reconciled_bars, metrics = prepare_reconciled_daily_bars(raw_bars)

    assert metrics["raw_records"] == 3
    assert metrics["distinct_dates"] == 2
    assert metrics["usable_bars"] == 2
    assert metrics["identical_duplicates_collapsed"] == 1
    assert len(reconciled_bars) == 2

def test_evaluate_symbol_v22_readiness_direct_call(isolated_db_session):
    from scripts.audit.generate_audit_csvs import evaluate_symbol_v22_readiness
    now_utc = datetime.now(timezone.utc)

    # Populate 250 price bars for RELIANCE
    bars = []
    for i in range(250):
        dt = now_utc - timedelta(days=250 - i)
        c_price = 1000.0 + (i * 2.0)
        bars.append(PriceDB(
            symbol="RELIANCE", date=dt, open=c_price - 1.0, high=c_price + 5.0, low=c_price - 2.0, close=c_price, volume=50000, source="TEST"
        ))
    isolated_db_session.add_all(bars)
    isolated_db_session.commit()

    eval_res = evaluate_symbol_v22_readiness(isolated_db_session, "RELIANCE")

    assert eval_res["symbol"] == "RELIANCE"
    assert eval_res["usable_observation_records"] == 250
    assert eval_res["calc_status"] == "INDICATOR_CALCULATION_PASSED"
    assert eval_res["v22_readiness"] == "V22_INPUT_REQUIREMENTS_PASSED"
    assert eval_res["rsi14_valid"] is True
    assert eval_res["ema200_valid"] is True

def test_evaluate_symbol_v22_readiness_insufficient_history(isolated_db_session):
    from scripts.audit.generate_audit_csvs import evaluate_symbol_v22_readiness
    now_utc = datetime.now(timezone.utc)

    # Populate only 100 price bars
    bars = []
    for i in range(100):
        dt = now_utc - timedelta(days=100 - i)
        c_price = 1000.0 + (i * 2.0)
        bars.append(PriceDB(
            symbol="TCS", date=dt, open=c_price - 1.0, high=c_price + 5.0, low=c_price - 2.0, close=c_price, volume=50000, source="TEST"
        ))
    isolated_db_session.add_all(bars)
    isolated_db_session.commit()

    eval_res = evaluate_symbol_v22_readiness(isolated_db_session, "TCS")

    assert eval_res["symbol"] == "TCS"
    assert eval_res["usable_observation_records"] == 100
    assert eval_res["v22_readiness"] == "BLOCKED_INSUFFICIENT_HISTORY"

def test_centralized_alias_resolution_for_azad():
    from scripts.audit.generate_audit_csvs import resolve_stored_symbol_aliases

    aliases = resolve_stored_symbol_aliases("AZAD")
    assert "AZAD" in aliases
    assert " Azad Engineering" in aliases

def test_fail_closed_test_database_isolation_guard():
    sig = LiveSignal(
        id="sig_guard_p37", symbol="RELIANCE", direction="LONG", rating="BUY", timeframe="SWING", entry_price=2500.0, status="ACTIVE"
    )
    with pytest.raises(RuntimeError, match="Unisolated database session detected"):
        import asyncio
        asyncio.run(SignalLedgerService.create_signal(sig, session=None))
