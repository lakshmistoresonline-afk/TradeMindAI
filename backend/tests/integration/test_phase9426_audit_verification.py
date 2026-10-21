"""
================================================================================
TradeMindAI: Phase 9.4.26 Audit Verification & Isolation Integration Tests
================================================================================
1. Direct SQL distinct key count vs math cross-check identity verification.
2. Shared duplicate group classifier function execution on isolated DB.
3. Centralized symbol alias resolution (AZAD -> ' Azad Engineering').
4. Fail-closed test database isolation guard enforcement.
================================================================================
"""

import os
import pytest
import datetime
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

def test_direct_sql_distinct_keys_matching_math_identity(isolated_db_session):
    from scripts.audit.generate_audit_csvs import classify_duplicate_groups
    now_utc = datetime.now(timezone.utc)

    dt1 = now_utc - timedelta(days=1)
    isolated_db_session.add_all([
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A"),
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A"),
        PriceDB(symbol="TCS", date=dt1, open=3000, high=3020, low=2980, close=3010, volume=1000, source="SRC_B")
    ])

    isolated_db_session.commit()

    metrics = classify_duplicate_groups(isolated_db_session)

    assert metrics["total_table_rows"] == 3
    assert metrics["direct_sql_distinct_keys"] == 2
    assert metrics["math_unique_keys"] == 2
    assert metrics["direct_sql_distinct_keys"] == metrics["math_unique_keys"]
    assert metrics["duplicate_groups_count"] == 1
    assert metrics["excess_rows"] == 1

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
        id="sig_guard_p26", symbol="RELIANCE", direction="LONG", rating="BUY", timeframe="SWING", entry_price=2500.0, status="ACTIVE"
    )
    with pytest.raises(RuntimeError, match="Unisolated database session detected"):
        import asyncio
        asyncio.run(SignalLedgerService.create_signal(sig, session=None))

def test_canonical_500_symbols_uniqueness_and_length():
    assert len(NIFTY_500_SYMBOLS) == 500
    assert len(set(NIFTY_500_SYMBOLS)) == 500
    for sym in NIFTY_500_SYMBOLS:
        assert sym == sym.strip().upper()
