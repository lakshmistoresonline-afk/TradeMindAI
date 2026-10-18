"""
================================================================================
TradeMindAI: Phase 9.4.3 Global Uniqueness & Timestamp Creation Proof Tests
================================================================================
Exercises real SignalLedgerService methods against an isolated database to prove:
1. Signal creation timestamps (created_at) are generated dynamically in UTC.
2. Global one-active-signal-per-stock invariant is enforced across different
   timeframes/horizons (SWING, SHORT, LONG) for the same normalized stock symbol.
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

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.mark.asyncio
async def test_global_one_active_signal_per_stock_across_horizons(db_session):
    # Create first active signal for RELIANCE with SWING horizon
    swing_signal = LiveSignal(
        id="sig_u_swing_001",
        symbol="RELIANCE",
        direction="LONG",
        rating="STRONG_BUY",
        timeframe="SWING",
        entry_price=2500.0,
        target_price=2700.0,
        stop_price=2375.0,
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )

    persisted_swing = await SignalLedgerService.create_signal(swing_signal, session=db_session)
    assert persisted_swing is not None
    assert persisted_swing.id == "sig_u_swing_001"

    # Attempt to create second active signal for RELIANCE with LONG horizon
    long_signal = LiveSignal(
        id="sig_u_long_002",
        symbol="RELIANCE",
        direction="LONG",
        rating="BUY",
        timeframe="LONG",
        entry_price=2520.0,
        target_price=2800.0,
        stop_price=2400.0,
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )

    # Global uniqueness invariant: rejects/returns existing active signal and blocks second active signal creation
    persisted_long = await SignalLedgerService.create_signal(long_signal, session=db_session)
    assert persisted_long is not None
    assert persisted_long.id == "sig_u_swing_001" # Returned existing active signal ID

    # Verify that ONLY ONE active row exists for RELIANCE in the database
    active_rows = db_session.query(LiveSignalDB).filter(
        LiveSignalDB.symbol == "RELIANCE",
        LiveSignalDB.status == "ACTIVE"
    ).all()

    assert len(active_rows) == 1
    assert active_rows[0].id == "sig_u_swing_001"

@pytest.mark.asyncio
async def test_creation_timestamp_generated_dynamically_in_utc(db_session):
    start_time = datetime.now(timezone.utc) - timedelta(seconds=2)

    signal = LiveSignal(
        id="sig_u_ts_001",
        symbol="TCS",
        direction="LONG",
        rating="STRONG_BUY",
        timeframe="SHORT",
        entry_price=3500.0,
        status="ACTIVE"
    )

    await SignalLedgerService.create_signal(signal, session=db_session)

    reloaded = db_session.query(LiveSignalDB).filter(LiveSignalDB.id == "sig_u_ts_001").first()
    assert reloaded is not None
    assert reloaded.created_at is not None
    end_time = datetime.now(timezone.utc) + timedelta(seconds=2)

    # Verify timestamp was generated dynamically at creation time
    created_dt = reloaded.created_at
    if created_dt.tzinfo is None:
        created_dt = created_dt.replace(tzinfo=timezone.utc)

    assert start_time <= created_dt <= end_time
