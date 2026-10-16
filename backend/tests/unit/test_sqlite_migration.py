import pytest
from sqlalchemy import create_engine, text
from backend.core.postgres import Base as PostgresBase
from backend.app.main import ensure_sqlite_columns

def test_sqlite_migration_all_present(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file}")
    PostgresBase.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(live_signals)")).fetchall()
        cols = [r[1] for r in res]
        assert "target_price_1" in cols
        assert "target_price_2" in cols
        assert "target_price_3" in cols

    # Run migration twice (Scenario 1 & 5: Idempotency & all present)
    ensure_sqlite_columns(eng=engine)
    ensure_sqlite_columns(eng=engine)

def test_sqlite_migration_all_absent(tmp_path):
    # Scenario 2: All target columns absent
    db_file = tmp_path / "test_absent.db"
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE live_signals (
                id TEXT PRIMARY KEY,
                symbol TEXT
            )
        """))
        conn.commit()

    ensure_sqlite_columns(eng=engine)
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(live_signals)")).fetchall()
        cols = [r[1] for r in res]
        assert "target_price_1" in cols
        assert "target_price_2" in cols
        assert "target_price_3" in cols

def test_sqlite_migration_only_t1_exists(tmp_path):
    # Scenario 3: Only target_price_1 exists
    db_file = tmp_path / "test_t1.db"
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE live_signals (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                target_price_1 FLOAT
            )
        """))
        conn.commit()

    ensure_sqlite_columns(eng=engine)
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(live_signals)")).fetchall()
        cols = [r[1] for r in res]
        assert "target_price_1" in cols
        assert "target_price_2" in cols
        assert "target_price_3" in cols

def test_sqlite_migration_partial_missing(tmp_path):
    # Scenario 4: Only target_price_2 is missing (target_price_1 and 3 exist)
    db_file = tmp_path / "test_partial.db"
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE live_signals (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                target_price_1 FLOAT,
                target_price_3 FLOAT
            )
        """))
        conn.commit()

    ensure_sqlite_columns(eng=engine)
    with engine.connect() as conn:
        res = conn.execute(text("PRAGMA table_info(live_signals)")).fetchall()
        cols = [r[1] for r in res]
        assert "target_price_1" in cols
        assert "target_price_2" in cols
        assert "target_price_3" in cols

def test_sqlite_migration_failure_visible(tmp_path):
    # Scenario 6: Migration failure raises exception and is visible
    class MockEngine:
        url = "sqlite:///mock"
        def connect(self):
            raise RuntimeError("Database connection lost")

    with pytest.raises(RuntimeError) as exc_info:
        ensure_sqlite_columns(eng=MockEngine())
    assert "Database migration failed" in str(exc_info.value)

def test_postgresql_path_does_not_execute_sqlite_sql():
    # Scenario 7: Production PostgreSQL path does not execute SQLite migration
    class MockPostgresEngine:
        url = "postgresql://user:pass@localhost/db"
        def connect(self):
            raise AssertionError("Should not attempt to connect or execute SQLite PRAGMA for PostgreSQL!")

    ensure_sqlite_columns(eng=MockPostgresEngine())
