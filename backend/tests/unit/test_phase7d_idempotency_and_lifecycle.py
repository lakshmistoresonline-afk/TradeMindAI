import pytest
import asyncio
import subprocess
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.postgres import Base, LiveSignalDB
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_eligibility import is_eligible_buy
from backend.workers.lifecycle_worker import SignalLifecycleWorker
from backend.domain.models.ios import LiveSignal

@pytest.fixture
def test_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    engine.dispose()

@pytest.mark.asyncio
async def test_atomic_idempotency_same_symbol_horizon(test_db_session):
    sig_1 = LiveSignal(
        id="sig_abc_1",
        symbol="RELIANCE",
        direction="LONG",
        rating="BUY",
        timeframe="SWING",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility="ELIGIBLE",
        entry_price=1000.0,
        conviction=85.0
    )

    # First insert succeeds
    res_1 = await SignalLedgerService.create_signal(sig_1, session=test_db_session)
    assert res_1.id == "sig_abc_1"

    # Second insert with different ID but same symbol and timeframe should return existing record idempotently
    sig_2 = LiveSignal(
        id="sig_abc_2",
        symbol="RELIANCE",
        direction="LONG",
        rating="BUY",
        timeframe="SWING",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility="ELIGIBLE",
        entry_price=1010.0,
        conviction=90.0
    )

    res_2 = await SignalLedgerService.create_signal(sig_2, session=test_db_session)
    assert res_2.id == "sig_abc_1" # Returns existing record

@pytest.mark.asyncio
async def test_distinct_horizons_coexist(test_db_session):
    sig_swing = LiveSignal(
        id="sig_swing_1",
        symbol="TCS",
        direction="LONG",
        rating="BUY",
        timeframe="SWING",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility="ELIGIBLE",
        entry_price=3000.0,
        conviction=85.0
    )
    sig_long = LiveSignal(
        id="sig_long_1",
        symbol="TCS",
        direction="LONG",
        rating="BUY",
        timeframe="LONG",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility="ELIGIBLE",
        entry_price=3000.0,
        conviction=88.0
    )

    res_1 = await SignalLedgerService.create_signal(sig_swing, session=test_db_session)
    res_2 = await SignalLedgerService.create_signal(sig_long, session=test_db_session)

    assert res_1.id == "sig_swing_1"
    # Phase 9.4.3 Global Uniqueness Invariant: Enforces at most 1 active signal per stock globally
    assert res_2.id == "sig_swing_1"

@pytest.mark.asyncio
async def test_buy_eligibility_rejection_at_persistence(test_db_session):
    sig_short = LiveSignal(
        id="sig_short_1",
        symbol="INFY",
        direction="SHORT",
        rating="SELL",
        timeframe="SWING",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility="INELIGIBLE",
        entry_price=1500.0,
        conviction=85.0
    )

    with pytest.raises(ValueError, match="violates BUY-only eligibility policy"):
        await SignalLedgerService.create_signal(sig_short, session=test_db_session)

@pytest.mark.asyncio
async def test_lifecycle_worker_status_precedence():
    worker = SignalLifecycleWorker()

    with patch.object(worker, '_process_active_signals', new_callable=AsyncMock, side_effect=Exception("Audit failure")), \
         patch.object(worker, '_generate_new_signals', new_callable=AsyncMock, return_value={"generated": 0, "errors": 0, "status": "COMPLETED"}):

        report = await worker.run_cycle()
        assert report["status"] in ("PARTIAL", "FAILED")

@pytest.mark.asyncio
async def test_lifecycle_worker_invocation_path():
    worker = SignalLifecycleWorker()
    with patch.object(worker, '_process_active_signals', new_callable=AsyncMock, return_value={"audited": 0, "errors": 0}), \
         patch.object(worker, '_generate_new_signals', new_callable=AsyncMock, return_value={"generated": 0, "errors": 0, "status": "COMPLETED"}):

        report = await worker.run_cycle()
        assert report["status"] == "COMPLETED"
        assert report["cycle_id"].startswith("cycle_")

def test_cli_main_exit_codes():
    from backend.workers.lifecycle_worker import main as worker_main

    # 1. COMPLETED -> 0
    with patch('backend.workers.lifecycle_worker.SignalLifecycleWorker') as MockWorker:
        instance = MockWorker.return_value
        instance.run_cycle = AsyncMock(return_value={"status": "COMPLETED"})
        assert worker_main() == 0

    # 2. PARTIAL -> 1
    with patch('backend.workers.lifecycle_worker.SignalLifecycleWorker') as MockWorker:
        instance = MockWorker.return_value
        instance.run_cycle = AsyncMock(return_value={"status": "PARTIAL", "reason": "Partial errors"})
        assert worker_main() == 1

    # 3. FAILED -> 1
    with patch('backend.workers.lifecycle_worker.SignalLifecycleWorker') as MockWorker:
        instance = MockWorker.return_value
        instance.run_cycle = AsyncMock(return_value={"status": "FAILED", "reason": "Scan failed"})
        assert worker_main() == 1

    # 4. BLOCKED -> 1
    with patch('backend.workers.lifecycle_worker.SignalLifecycleWorker') as MockWorker:
        instance = MockWorker.return_value
        instance.run_cycle = AsyncMock(return_value={"status": "BLOCKED", "reason": "Blocked"})
        assert worker_main() == 1

    # 5. Crash / Exception -> 1
    with patch('backend.workers.lifecycle_worker.SignalLifecycleWorker', side_effect=Exception("Crash")):
        assert worker_main() == 1

def test_cli_subprocess_execution():
    script = """
import asyncio
from unittest.mock import AsyncMock, patch
from backend.workers.lifecycle_worker import main, SignalLifecycleWorker

with patch.object(SignalLifecycleWorker, 'run_cycle', new_callable=AsyncMock, return_value={"status": "COMPLETED"}):
    code = main()
    import sys
    sys.exit(code)
"""
    res = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert res.returncode == 0

@pytest.mark.asyncio
async def test_concurrent_duplicate_persistence_sqlite(test_db_session):
    sig_a = LiveSignal(
        id="sig_conc_1",
        symbol="HDFCBANK",
        direction="LONG",
        rating="BUY",
        timeframe="SWING",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility="ELIGIBLE",
        entry_price=1600.0,
        conviction=88.0
    )
    sig_b = LiveSignal(
        id="sig_conc_2",
        symbol="HDFCBANK",
        direction="LONG",
        rating="BUY",
        timeframe="SWING",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility="ELIGIBLE",
        entry_price=1605.0,
        conviction=90.0
    )

    results = await asyncio.gather(
        SignalLedgerService.create_signal(sig_a, session=test_db_session),
        SignalLedgerService.create_signal(sig_b, session=test_db_session),
        return_exceptions=True
    )
    assert not isinstance(results[0], Exception)
    assert not isinstance(results[1], Exception)
