"""
================================================================================
TradeMindAI Phase 5.25: Signal Ledger Transaction Ownership Test Suite
================================================================================
Dedicated unit test suite proving transaction boundary preservation, caller-owned
session isolation, internal session commit/close semantics, and terminal-state
immutability protection across SignalLedgerService.
================================================================================
"""

import pytest
import datetime
from datetime import timezone
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.postgres import Base, LiveSignalDB, ModelMetadataDB
from backend.core.trading_safety import verify_test_database_isolation
from backend.domain.models.ios import LiveSignal
from backend.services.signal_ledger_service import SignalLedgerService

def asyncio_run_helper(coro):
    import asyncio
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    except Exception:
        return asyncio.run(coro)

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    verify_test_database_isolation(str(engine.url))
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session, TestSession, engine
    session.close()
    engine.dispose()

def test_update_signal_caller_session_no_commit(test_db):
    """1. Verify update_signal() flushes but does NOT commit caller-owned session."""
    session, TestSession, engine = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="INFY", company_name="Infosys Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1500.0, target_price=1620.0, stop_price=1425.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))
    session.commit()

    # Update signal in caller session
    res = asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"confidence": 0.95}, session=session))
    assert res is True
    assert session.is_active is True

    # Calling rollback MUST revert uncommitted caller session changes
    session.rollback()
    reloaded = session.query(LiveSignalDB).filter(LiveSignalDB.id == sig_id).first()
    assert reloaded.confidence == 0.8

def test_update_signal_caller_session_no_close(test_db):
    """2. Verify update_signal() does NOT close caller-owned session."""
    session, _, _ = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="TCS", company_name="TCS Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=3500.0, target_price=3800.0, stop_price=3300.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))
    asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"confidence": 0.9}, session=session))

    # Caller session MUST remain active and open
    assert session.is_active is True

def test_update_signal_caller_session_no_rollback(test_db):
    """3. Verify update_signal() does NOT roll back caller session on error."""
    session, _, _ = test_db
    now_utc = datetime.datetime.now(timezone.utc)

    # Insert pending model metadata in caller session
    meta = ModelMetadataDB(
        name="TEMP_MODEL", symbol="INFY", version="v2.2", horizon="SWING",
        type="VotingClassifier", is_champion=True, status="CHAMPION", last_trained=now_utc
    )
    session.add(meta)
    session.flush()

    # Attempt updating nonexistent signal ID
    res = asyncio_run_helper(SignalLedgerService.update_signal("nonexistent_id", {"status": "ACTIVE"}, session=session))
    assert res is False

    # Pending meta in caller session MUST remain un-rolled-back in session buffer
    pending_meta = session.query(ModelMetadataDB).filter(ModelMetadataDB.name == "TEMP_MODEL").first()
    assert pending_meta is not None

def test_update_signal_caller_rollback_reverts_update(test_db):
    """4. Verify caller session rollback cleanly reverts update_signal() changes."""
    session, TestSession, engine = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="RELIANCE", company_name="Reliance Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=2500.0, target_price=2750.0, stop_price=2380.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))
    session.commit()

    # Update in caller session and execute rollback
    asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"confidence": 0.95}, session=session))
    session.rollback()

    # Verify value reverted
    reloaded = session.query(LiveSignalDB).filter(LiveSignalDB.id == sig_id).first()
    assert reloaded.confidence == 0.8

def test_update_signal_caller_commit_persists_update(test_db):
    """5. Verify caller session commit cleanly persists update_signal() changes to database."""
    session, TestSession, engine = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="HDFCBANK", company_name="HDFC Bank", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1600.0, target_price=1750.0, stop_price=1520.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))
    asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"confidence": 0.99}, session=session))
    session.commit()

    # Read back in separate independent session after caller commit
    indep_session = TestSession()
    try:
        indep_row = indep_session.query(LiveSignalDB).filter(LiveSignalDB.id == sig_id).first()
        assert indep_row is not None
        assert indep_row.confidence == 0.99
    finally:
        indep_session.close()

def test_update_signal_unrelated_pending_work_uncommitted(test_db):
    """6. Verify update_signal() does not commit unrelated pending work in caller session."""
    session, TestSession, engine = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="ICICIBANK", company_name="ICICI Bank", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1000.0, target_price=1120.0, stop_price=940.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))

    # Add unrelated pending work
    meta = ModelMetadataDB(
        name="UNRELATED_META", symbol="ICICIBANK", version="v2.2", horizon="SWING",
        type="VotingClassifier", is_champion=True, status="CHAMPION", last_trained=now_utc
    )
    session.add(meta)

    # Execute update_signal (should NOT commit session)
    asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"confidence": 0.88}, session=session))
    assert session.is_active is True

    # Roll back caller session -> unrelated metadata MUST be cleared
    session.rollback()
    assert session.query(ModelMetadataDB).filter(ModelMetadataDB.name == "UNRELATED_META").first() is None

def test_update_signal_terminal_reopen_fails(test_db):
    """7. Verify terminal signal cannot change status back to ACTIVE."""
    session, _, _ = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="INFY", company_name="Infosys Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1500.0, target_price=1620.0, stop_price=1425.0, status="TARGET_HIT",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))

    # Attempt setting terminal signal status back to ACTIVE
    res = asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"status": "ACTIVE"}, session=session))
    assert res is False

def test_update_signal_terminal_restricted_fields_fail(test_db):
    """8. Verify terminal signal rejects mutations to entry_price, target_price, or model_version."""
    session, _, _ = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="INFY", company_name="Infosys Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1500.0, target_price=1620.0, stop_price=1425.0, status="STOP_LOSS",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))

    # Attempt mutating restricted fields on terminal signal
    res_entry = asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"entry_price": 9999.0}, session=session))
    assert res_entry is False

    res_model = asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"model_version": "v3.0"}, session=session))
    assert res_model is False

def test_update_signal_transition_and_entry_price_mutation_fails(test_db):
    """9. Verify active-to-terminal update combined with entry_price modification is rejected."""
    session, _, _ = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="INFY", company_name="Infosys Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1500.0, target_price=1620.0, stop_price=1425.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))

    # Attempt simultaneous status transition to TARGET_HIT and entry_price modification
    res = asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"status": "TARGET_HIT", "entry_price": 2000.0}, session=session))
    assert res is False

def test_update_signal_valid_terminal_transition_succeeds(test_db):
    """10. Verify valid active-to-terminal transition succeeds."""
    session, _, _ = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="INFY", company_name="Infosys Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1500.0, target_price=1620.0, stop_price=1425.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))

    # Valid status transition to TARGET_HIT
    res = asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"status": "TARGET_HIT"}, session=session))
    assert res is True

def test_update_signal_unknown_field_rejected(test_db):
    """11. Verify update_signal() rejects unknown fields."""
    session, _, _ = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="INFY", company_name="Infosys Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=1500.0, target_price=1620.0, stop_price=1425.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    asyncio_run_helper(SignalLedgerService.create_signal(sig, session=session))

    # Supply invalid unknown field key
    res = asyncio_run_helper(SignalLedgerService.update_signal(sig_id, {"invalid_nonexistent_field": 12345}, session=session))
    assert res is False

def test_create_signal_internal_caller_session_flushes_only(test_db):
    """12. Verify _create_signal_internal returns PENDING_CALLER_COMMIT and flushes without caller commit."""
    session, TestSession, engine = test_db
    now_utc = datetime.datetime.now(timezone.utc)
    sig_id = f"test_sig_{uuid.uuid4().hex[:8]}"

    sig = LiveSignal(
        id=sig_id, symbol="WIPRO", company_name="Wipro Ltd", exchange="NSE",
        asset_type="EQUITY", direction="LONG", rating="BUY", timeframe="SWING",
        entry_price=450.0, target_price=500.0, stop_price=420.0, status="ACTIVE",
        confidence=0.8, created_at=now_utc
    )
    res = asyncio_run_helper(SignalLedgerService._create_signal_internal(sig, session=session))
    assert res["status"] == "PENDING_CALLER_COMMIT"
    assert session.is_active is True

    # Roll back caller session -> pending insert MUST be cleared
    session.rollback()
    assert session.query(LiveSignalDB).filter(LiveSignalDB.id == sig_id).first() is None
