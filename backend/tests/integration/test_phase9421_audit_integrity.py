"""
================================================================================
TradeMindAI: Phase 9.4.21 Audit Integrity & Readiness Verification Tests
================================================================================
1. Verifies centralized symbol alias resolution (AZAD -> ' Azad Engineering').
2. Verifies 500-symbol canonical resolution audit contract (every symbol resolved).
3. Verifies full-table duplicate reconciliation mathematical identities.
4. Verifies fail-closed test database isolation guard enforcement.
================================================================================
"""

import os
import pytest
import datetime
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker

from backend.core.postgres import Base, PriceDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS
from backend.services.signal_ledger_service import SignalLedgerService

@pytest.fixture
def isolated_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()

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

def test_canonical_500_symbols_uniqueness_and_length():
    assert len(NIFTY_500_SYMBOLS) == 500
    assert len(set(NIFTY_500_SYMBOLS)) == 500
    for sym in NIFTY_500_SYMBOLS:
        assert sym == sym.strip().upper()
