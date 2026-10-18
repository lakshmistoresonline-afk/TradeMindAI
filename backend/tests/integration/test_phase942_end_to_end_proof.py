"""
================================================================================
TradeMindAI: Phase 9.4.2 End-to-End Proof & Real Persistence Integration Tests
================================================================================
Exercises the actual SignalLedgerService and LiveSignalDB database persistence
path using an isolated SQLAlchemy Session to prove that:
1. Signal persistence generates real timestamps reloaded from the database.
2. Ineligible candidates are rejected at the persistence boundary.
3. Immutability protections block unauthorized updates on terminal state signals.
================================================================================
"""

import pytest
import datetime
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.postgres import Base, LiveSignalDB
from backend.domain.models.ios import LiveSignal
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_eligibility import is_eligible_buy

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.mark.asyncio
async def test_real_persistence_creation_and_reload(db_session):
    now_utc = datetime.now(timezone.utc)
    signal = LiveSignal(
        id="sig_e2e_001",
        symbol="RELIANCE",
        direction="LONG",
        rating="STRONG_BUY",
        timeframe="SWING",
        entry_price=2500.0,
        target_price=2700.0,
        stop_price=2375.0,
        status="ACTIVE",
        created_at=now_utc,
        signal_timestamp=datetime(2026, 10, 16, 10, 0, tzinfo=timezone.utc)
    )

    # Invoke real SignalLedgerService persistence with isolated session
    persisted = await SignalLedgerService.create_signal(signal, session=db_session)
    assert persisted is not None

    # Query directly from database to verify true persistence
    reloaded = db_session.query(LiveSignalDB).filter(LiveSignalDB.id == "sig_e2e_001").first()
    assert reloaded is not None
    assert reloaded.symbol == "RELIANCE"
    assert reloaded.status == "ACTIVE"
    assert reloaded.entry_price == 2500.0
    assert reloaded.created_at is not None

@pytest.mark.asyncio
async def test_persistence_boundary_rejects_ineligible_signal(db_session):
    ineligible_signal = LiveSignal(
        id="sig_e2e_002",
        symbol="TCS",
        direction="LONG",
        rating="SELL", # Violates BUY-only policy
        timeframe="SWING",
        entry_price=3500.0,
        status="ACTIVE"
    )

    with pytest.raises(ValueError, match="violates BUY-only eligibility policy"):
        await SignalLedgerService.create_signal(ineligible_signal, session=db_session)

    # Verify database remains empty
    reloaded = db_session.query(LiveSignalDB).filter(LiveSignalDB.id == "sig_e2e_002").first()
    assert reloaded is None

@pytest.mark.asyncio
async def test_terminal_state_immutability_protection(db_session):
    signal = LiveSignal(
        id="sig_e2e_003",
        symbol="INFY",
        direction="LONG",
        rating="BUY",
        timeframe="SWING",
        entry_price=1500.0,
        target_price=1620.0,
        stop_price=1425.0,
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )

    await SignalLedgerService.create_signal(signal, session=db_session)

    # Transition to TARGET_HIT (Terminal state)
    res_update = await SignalLedgerService.update_signal("sig_e2e_003", {"status": "TARGET_HIT"}, session=db_session)
    assert res_update is True

    # Attempt unauthorized mutation on immutable terminal signal
    res_blocked = await SignalLedgerService.update_signal("sig_e2e_003", {"entry_price": 2000.0}, session=db_session)
    assert res_blocked is False

    # Verify entry_price remained untouched
    reloaded = db_session.query(LiveSignalDB).filter(LiveSignalDB.id == "sig_e2e_003").first()
    assert reloaded.entry_price == 1500.0
