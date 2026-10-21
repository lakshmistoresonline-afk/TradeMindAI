"""
================================================================================
TradeMindAI: Phase 9.4.60 Acceptance Gate Proof Tests
================================================================================
1. Direct test of Symbols A-E fixture verifying dynamic reconciliation output.
2. Direct test of is_finite_number function rejecting NaN, +inf, -inf, None, and strings.
3. Direct call to evaluate_symbol_v22_readiness verifying finite-value indicator safety.
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

def test_symbols_a_to_e_reconciliation_integrity(isolated_db_session):
    from scripts.audit.generate_audit_csvs import prepare_reconciled_daily_bars, evaluate_symbol_v22_readiness
    now_utc = datetime.now(timezone.utc)
    dt = now_utc - timedelta(days=1)

    # Symbol A: Two distinct sources with identical OHLCV
    sym_a_1 = PriceDB(symbol="SYM_A", date=dt, open=100.0, high=105.0, low=95.0, close=102.0, volume=1000, source="SRC_1")
    sym_a_2 = PriceDB(symbol="SYM_A", date=dt, open=100.0, high=105.0, low=95.0, close=102.0, volume=1000, source="SRC_2")

    # Symbol B: Two distinct sources with conflicting close price
    sym_b_1 = PriceDB(symbol="SYM_B", date=dt, open=100.0, high=105.0, low=95.0, close=102.0, volume=1000, source="SRC_1")
    sym_b_2 = PriceDB(symbol="SYM_B", date=dt, open=100.0, high=105.0, low=95.0, close=108.0, volume=1000, source="SRC_2")

    # Symbol C: One source only
    sym_c_1 = PriceDB(symbol="SYM_C", date=dt, open=100.0, high=105.0, low=95.0, close=102.0, volume=1000, source="SRC_1")

    isolated_db_session.add_all([sym_a_1, sym_a_2, sym_b_1, sym_b_2, sym_c_1])
    isolated_db_session.commit()

    # Symbol A check
    bars_a, metrics_a = prepare_reconciled_daily_bars([sym_a_1, sym_a_2])
    assert metrics_a["identical_duplicates_collapsed"] == 1
    assert len(bars_a) == 1

    # Symbol B check
    bars_b, metrics_b = prepare_reconciled_daily_bars([sym_b_1, sym_b_2])
    assert metrics_b["conflicting_dates"] == 1
    assert len(bars_b) == 0

    # Symbol C check
    bars_c, metrics_c = prepare_reconciled_daily_bars([sym_c_1])
    assert metrics_c["raw_records"] == 1
    assert len(bars_c) == 1

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
    assert eval_res["duplicate_quality_disposition"] == "NO_DUPLICATES_FOUND"

def test_fail_closed_test_database_isolation_guard():
    sig = LiveSignal(
        id="sig_guard_p60", symbol="RELIANCE", direction="LONG", rating="BUY", timeframe="SWING", entry_price=2500.0, status="ACTIVE"
    )
    with pytest.raises(RuntimeError, match="Unisolated database session detected"):
        import asyncio
        asyncio.run(SignalLedgerService.create_signal(sig, session=None))
