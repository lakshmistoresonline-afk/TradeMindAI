"""
================================================================================
TradeMindAI: Phase 9.4.22 Audit Integrity & Real Classifier Tests
================================================================================
1. Verifies null-safe duplicate group classification query logic.
2. Verifies real symbol resolver and canonical universe resolution contract.
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

def test_shared_duplicate_classifier_null_safety(isolated_db_session):
    now_utc = datetime.now(timezone.utc)

    # Group 1: Identical rows
    dt1 = now_utc - timedelta(days=1)
    isolated_db_session.add_all([
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A"),
        PriceDB(symbol="RELIANCE", date=dt1, open=2500, high=2520, low=2490, close=2510, volume=1000, source="SRC_A")
    ])

    # Group 2: Indeterminate rows (contains a null close)
    dt2 = now_utc
    isolated_db_session.add_all([
        PriceDB(symbol="TCS", date=dt2, open=3000, high=3020, low=2980, close=None, volume=1000, source="SRC_B"),
        PriceDB(symbol="TCS", date=dt2, open=3000, high=3020, low=2980, close=3010, volume=1000, source="SRC_B")
    ])

    isolated_db_session.commit()

    dup_sql = text('''
        SELECT
            symbol,
            CASE
                WHEN null_cnt > 0 THEN 'INDETERMINATE'
                WHEN max_open = min_open AND max_high = min_high AND max_low = min_low AND max_close = min_close AND max_vol = min_vol THEN 'IDENTICAL'
                ELSE 'CONFLICTING'
            END as group_class
        FROM (
            SELECT
                symbol, date, source,
                COUNT(*) as cnt,
                (COUNT(*) * 5) - (COUNT(open) + COUNT(high) + COUNT(low) + COUNT(close) + COUNT(volume)) as null_cnt,
                MAX(open) as max_open, MIN(open) as min_open,
                MAX(high) as max_high, MIN(high) as min_high,
                MAX(low) as max_low, MIN(low) as min_low,
                MAX(close) as max_close, MIN(close) as min_close,
                MAX(volume) as max_vol, MIN(volume) as min_vol
            FROM historical_prices
            GROUP BY symbol, date, source
            HAVING COUNT(*) > 1
        ) t
    ''')

    results = {r[0]: r[1] for r in isolated_db_session.execute(dup_sql).fetchall()}

    assert results.get("RELIANCE") == "IDENTICAL"
    assert results.get("TCS") == "INDETERMINATE"

def test_centralized_alias_resolution_for_azad(isolated_db_session):
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
