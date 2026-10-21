"""
================================================================================
TradeMindAI: Phase 9.4.43 Correctness-First Audit Remediation Tests
================================================================================
1. Direct test of is_finite_number function rejecting NaN, +inf, -inf, None, and strings.
2. Direct call to evaluate_symbol_v22_readiness verifying finite-value indicator safety.
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

def test_is_finite_number_validation():
    from scripts.audit.generate_audit_csvs import is_finite_number

    assert is_finite_number(100.5) is True
    assert is_finite_number(0) is True
    assert is_finite_number(-25.3) is True
    assert is_finite_number("123.45") is True

    assert is_finite_number(float("nan")) is False
    assert is_finite_number(float("inf")) is False
    assert is_finite_number(float("-inf")) is False
    assert is_finite_number(None) is False
    assert is_finite_number("invalid_string") is False

def test_evaluate_symbol_v22_readiness_finite_validation(isolated_db_session):
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
    assert eval_res["rsi14_valid"] is True
    assert eval_res["ema200_valid"] is True

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

def test_centralized_alias_resolution_for_azad():
    from scripts.audit.generate_audit_csvs import resolve_stored_symbol_aliases

    aliases = resolve_stored_symbol_aliases("AZAD")
    assert "AZAD" in aliases
    assert " Azad Engineering" in aliases

def test_fail_closed_test_database_isolation_guard():
    sig = LiveSignal(
        id="sig_guard_p43", symbol="RELIANCE", direction="LONG", rating="BUY", timeframe="SWING", entry_price=2500.0, status="ACTIVE"
    )
    with pytest.raises(RuntimeError, match="Unisolated database session detected"):
        import asyncio
        asyncio.run(SignalLedgerService.create_signal(sig, session=None))
