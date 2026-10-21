"""
================================================================================
TradeMindAI: Phase 9.4.42 V2.2 Readiness Contract & Production Path Proof Tests
================================================================================
1. Direct call to prepare_reconciled_daily_bars verifying duplicate collapsing.
2. Direct call to evaluate_symbol_v22_readiness verifying lookback requirement.
3. Verification that conflicting duplicate bars block readiness with BLOCKED_DUPLICATE_CONFLICT.
4. Fail-closed test database isolation guard enforcement.
================================================================================
"""

import os
import math
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

def test_prepare_reconciled_daily_bars_direct_call():
    from scripts.audit.generate_audit_csvs import prepare_reconciled_daily_bars
    now_utc = datetime.now(timezone.utc)

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
    assert metrics["conflicting_dates"] == 0
    assert len(reconciled_bars) == 2

def test_conflicting_duplicate_bars_block_readiness(isolated_db_session):
    from scripts.audit.generate_audit_csvs import evaluate_symbol_v22_readiness
    now_utc = datetime.now(timezone.utc)

    bars = []
    for i in range(200):
        dt = now_utc - timedelta(days=200 - i)
        c_price = 1000.0 + (i * 2.0)
        bars.append(PriceDB(
            symbol="CONFLICT_SYM", date=dt, open=c_price - 1.0, high=c_price + 5.0, low=c_price - 2.0, close=c_price, volume=50000, source="SRC_A"
        ))
        if i == 10:
            bars.append(PriceDB(
                symbol="CONFLICT_SYM", date=dt, open=c_price - 1.0, high=c_price + 5.0, low=c_price - 2.0, close=c_price + 10.0, volume=50000, source="SRC_B"
            ))

    isolated_db_session.add_all(bars)
    isolated_db_session.commit()

    eval_res = evaluate_symbol_v22_readiness(isolated_db_session, "CONFLICT_SYM")

    assert eval_res["symbol"] == "CONFLICT_SYM"
    assert eval_res["v22_readiness"] == "BLOCKED_DUPLICATE_CONFLICT"
    assert eval_res["calc_status"] == "BLOCKED_DUPLICATE_CONFLICT"

def test_evaluate_symbol_v22_readiness_valid_history(isolated_db_session):
    from scripts.audit.generate_audit_csvs import evaluate_symbol_v22_readiness
    now_utc = datetime.now(timezone.utc)

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

def test_centralized_alias_resolution_for_azad():
    from scripts.audit.generate_audit_csvs import resolve_stored_symbol_aliases

    aliases = resolve_stored_symbol_aliases("AZAD")
    assert "AZAD" in aliases
    assert " Azad Engineering" in aliases

def test_fail_closed_test_database_isolation_guard():
    sig = LiveSignal(
        id="sig_guard_p42", symbol="RELIANCE", direction="LONG", rating="BUY", timeframe="SWING", entry_price=2500.0, status="ACTIVE"
    )
    with pytest.raises(RuntimeError, match="Unisolated database session detected"):
        import asyncio
        asyncio.run(SignalLedgerService.create_signal(sig, session=None))
