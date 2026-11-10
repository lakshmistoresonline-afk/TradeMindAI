"""
================================================================================
TradeMindAI Phase 4.3.3 / 4.3.4: Quality Gate & Signal Pipeline Test Suite
================================================================================
Tests effective runtime safety invariants, strict fail-closed quality gate,
registered vs unregistered model metadata, time-safety, V2.2/V2.3 isolation,
and end-to-end signal pipeline persistence with database isolation.
================================================================================
"""

import pytest
import datetime
from datetime import timezone
import hashlib
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.domain.models.data_platform import ModelMetadata
from backend.services.signal_quality_service import SignalQualityService
from backend.services.security_master_service import SecurityMasterService
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_eligibility import is_eligible_buy
from backend.core.config import settings
from backend.core.trading_safety import trading_safety, Operation, TradingSafetyViolation, is_signals_only_architecture
from backend.domain.models.ios import LiveSignal
from backend.core.postgres import Base, LiveSignalDB

def test_effective_signals_only_safety_invariant():
    """Verify that effective runtime signals-only architecture invariant evaluates True."""
    assert is_signals_only_architecture() is True
    assert getattr(settings, "REAL_TRADING", True) is False
    assert getattr(settings, "LIVE_EXECUTION_ENABLED", True) is False
    assert getattr(settings, "BROKER_ORDER_EXECUTION_ENABLED", True) is False
    assert getattr(settings, "QUARANTINE_ACTIVE", False) is True

def test_trading_safety_prohibits_order_execution():
    """Verify that TradingSafetyPolicy prohibits execute_order, raising TradingSafetyViolation."""
    with pytest.raises(TradingSafetyViolation):
        trading_safety.authorize(Operation.EXECUTE_ORDER)
    with pytest.raises(TradingSafetyViolation):
        trading_safety.execute_order()

def test_quality_gate_strict_fail_closed_unregistered_model():
    """Verify that unregistered model metadata (model=None) unconditionally fails closed."""
    assert SignalQualityService.should_publish("SWING", None, 0.82) is False
    assert SignalQualityService.should_publish("LONG", None, 0.85) is False
    assert SignalQualityService.should_publish("SHORT", None, 0.75) is False

def test_quality_gate_registered_model_success():
    """Verify that a registered champion model with valid metrics passes the quality gate."""
    valid_model = ModelMetadata(
        name="RELIANCE_SWING_v2.2.joblib",
        symbol="RELIANCE",
        version="v2.2",
        horizon="SWING",
        type="VotingClassifier",
        accuracy=0.65,
        precision=0.60,
        recall=0.60,
        f1_score=0.60,
        roc_auc=0.65,
        brier_score=0.15,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 50, "positives_test": 20}
    )
    assert SignalQualityService.should_publish("SWING", valid_model, 0.82) is True

def test_quality_gate_insufficient_sample_size_rejected():
    """Verify that models with test_size < 20 are rejected."""
    small_model = ModelMetadata(
        name="RELIANCE_SWING_v2.2.joblib",
        symbol="RELIANCE",
        version="v2.2",
        horizon="SWING",
        type="VotingClassifier",
        accuracy=0.65,
        precision=0.60,
        recall=0.60,
        f1_score=0.60,
        roc_auc=0.65,
        brier_score=0.15,
        is_champion=True,
        status="CHAMPION",
        last_trained=datetime.datetime.now(timezone.utc),
        hyperparameters={"test_size": 10, "positives_test": 2}
    )
    assert SignalQualityService.should_publish("SWING", small_model, 0.82) is False

def test_end_to_end_controlled_signal_persistence_and_readback():
    """
    Case B — End-to-End Signal Pipeline Proof with Isolated In-Memory Database:
    Constructs a valid LiveSignal object, validates BUY eligibility, persists to an isolated test database,
    and performs independent database read-back verification without touching operational database.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"
    now_utc = datetime.datetime.now(timezone.utc)

    test_signal = LiveSignal(
        id=sig_id,
        symbol="RELIANCE",
        company_name="Reliance Industries Limited",
        exchange="NSE",
        asset_type="EQUITY",
        direction="LONG",
        rating="BUY",
        timeframe="SWING",
        entry_price=2500.0,
        target_price=2650.0,
        stop_price=2420.0,
        confidence=0.82,
        calibrated_probability=0.82,
        expected_value=125.0,
        status="WAITING_FOR_ENTRY",
        model_version="v2.2",
        quality_class="PRIMARY",
        created_at=now_utc
    )

    # 1. Verify BUY eligibility predicate
    assert is_eligible_buy(test_signal) is True

    # 2. Persist signal to isolated test database using SignalLedgerService
    try:
        res = asyncio_run_helper(SignalLedgerService._create_signal_internal(test_signal, session=session))
        assert res["status"] in ("PERSISTED", "DUPLICATE_PREVENTED")

        # 3. Independent Database Read-Back Query
        readback_db = session.query(LiveSignalDB).filter(LiveSignalDB.id == sig_id).first()
        assert readback_db is not None
        assert readback_db.symbol == "RELIANCE"
        assert readback_db.direction == "LONG"
        assert readback_db.rating == "BUY"
        assert readback_db.entry_price == 2500.0
    finally:
        session.close()

def test_frozen_v22_files_byte_integrity_baseline_head():
    """Verify SHA-256 hashes of frozen V2.2 strategy files against baseline commit HEAD."""
    frozen_files = {
        "backend/services/signal_engine.py": "3FCF2BAC4C56EF6101CA2F8DC76AD3CFE7FEDDFC342CE63C50C100F950859891",
        "backend/services/outcome_engine.py": "EDEEACBDC3F675838D4FEA38065D1735B56AD3964456FC1FA85918872F356B25",
        "backend/services/risk_engine.py": "63082C5338363B68ADFBE0ADA98D0B1B07CB1492CB067B4E093651050BF769FF",
        "backend/core/risk.py": "826AC9EC177F30788B1A09DAC609045EF0B968CCE1DFF80FCBEAD30A3218A3F4",
        "backend/core/config.py": "927AAA5C1917EEC6DE98337D616F55DF391062F63FEB3AB8E382D574959A07ED"
    }

    for rel_path, expected_hash in frozen_files.items():
        abs_path = os.path.join(os.getcwd(), rel_path.replace("/", os.sep))
        assert os.path.exists(abs_path), f"Frozen file missing: {abs_path}"

        with open(abs_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest().upper()

        assert actual_hash == expected_hash, f"FROZEN FILE INTEGRITY VIOLATION: {rel_path} hash changed!"

def asyncio_run_helper(coro):
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception:
        return asyncio.run(coro)
