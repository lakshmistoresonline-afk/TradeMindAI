import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine, text
from backend.scripts.migrate_postgres_active_signal_index import run_postgres_preflight, execute_postgres_migration

@pytest.fixture
def test_migration_sqlite_engine():
    """
    Creates an isolated SQLite test database engine with live_signals table schema.
    """
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    with eng.connect() as conn:
        conn.execute(text("""
            CREATE TABLE live_signals (
                id VARCHAR PRIMARY KEY,
                symbol VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                timeframe VARCHAR
            )
        """))
        conn.commit()
    return eng

def test_sqlite_engine_unconditionally_rejected(test_migration_sqlite_engine):
    preflight = run_postgres_preflight(test_migration_sqlite_engine)
    assert preflight["preflight_status"] == "BLOCKED_DATABASE_DIALECT"
    assert "Non-PostgreSQL dialect detected" in preflight["reason"]

def test_mock_postgres_engine_ready_to_migrate():
    mock_eng = MagicMock()
    mock_eng.name = "postgresql"
    mock_eng.url = "postgresql://user:pass@localhost:5432/trademind"

    mock_conn = MagicMock()
    mock_eng.connect.return_value.__enter__.return_value = mock_conn

    res_tbl = MagicMock()
    res_tbl.fetchall.return_value = [("live_signals",)]

    res_cols = MagicMock()
    res_cols.fetchall.return_value = [("symbol",), ("status",)]

    res_dups = MagicMock()
    res_dups.fetchall.return_value = []

    res_idx = MagicMock()
    res_idx.fetchone.return_value = None

    mock_conn.execute.side_effect = [res_tbl, res_cols, res_dups, res_idx]

    preflight = run_postgres_preflight(mock_eng)
    assert preflight["table_exists"] is True
    assert preflight["duplicate_active_symbols_found"] == 0
    assert preflight["preflight_status"] == "READY_TO_MIGRATE"

def test_mock_postgres_preflight_blocks_when_duplicates_exist():
    mock_eng = MagicMock()
    mock_eng.name = "postgresql"
    mock_eng.url = "postgresql://user:pass@localhost:5432/trademind"

    mock_conn = MagicMock()
    mock_eng.connect.return_value.__enter__.return_value = mock_conn

    res_tbl = MagicMock()
    res_tbl.fetchall.return_value = [("live_signals",)]

    res_cols = MagicMock()
    res_cols.fetchall.return_value = [("symbol",), ("status",)]

    dup_row = MagicMock()
    dup_row._mapping = {"symbol": "RELIANCE", "cnt": 2}
    res_dups = MagicMock()
    res_dups.fetchall.return_value = [dup_row]

    mock_conn.execute.side_effect = [res_tbl, res_cols, res_dups]

    preflight = run_postgres_preflight(mock_eng)
    assert preflight["table_exists"] is True
    assert preflight["duplicate_active_symbols_found"] == 1
    assert preflight["preflight_status"] == "BLOCKED_DUPLICATE_ACTIVE_SYMBOLS"
    assert "EXISTING_DUPLICATE_ACTIVE_SIGNALS_FOUND" in preflight["reason"]

def test_mock_postgres_explicit_migration_creates_index():
    mock_eng = MagicMock()
    mock_eng.name = "postgresql"
    mock_eng.url = "postgresql://user:pass@localhost:5432/trademind"

    mock_conn = MagicMock()
    mock_eng.connect.return_value.__enter__.return_value = mock_conn

    # Preflight 1 setup (READY_TO_MIGRATE)
    res_tbl1 = MagicMock()
    res_tbl1.fetchall.return_value = [("live_signals",)]
    res_cols1 = MagicMock()
    res_cols1.fetchall.return_value = [("symbol",), ("status",)]
    res_dups1 = MagicMock()
    res_dups1.fetchall.return_value = []
    res_idx1 = MagicMock()
    res_idx1.fetchone.return_value = None

    # DDL Execute
    res_ddl = MagicMock()

    # Preflight 2 setup (ALREADY_MIGRATED)
    res_tbl2 = MagicMock()
    res_tbl2.fetchall.return_value = [("live_signals",)]
    res_cols2 = MagicMock()
    res_cols2.fetchall.return_value = [("symbol",), ("status",)]
    res_dups2 = MagicMock()
    res_dups2.fetchall.return_value = []
    res_idx2 = MagicMock()
    idx_row = ("idx_unique_active_signal", "CREATE UNIQUE INDEX idx_unique_active_signal ON live_signals (symbol) WHERE status = 'ACTIVE'")
    res_idx2.fetchone.return_value = idx_row

    mock_conn.execute.side_effect = [
        res_tbl1, res_cols1, res_dups1, res_idx1,
        res_ddl,
        res_tbl2, res_cols2, res_dups2, res_idx2
    ]

    res = execute_postgres_migration(mock_eng)
    assert res["migration_status"] == "SUCCESS"
    assert res["preflight"]["index_exists"] is True
    assert res["preflight"]["preflight_status"] == "ALREADY_MIGRATED"
