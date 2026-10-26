import os
import pytest
from backend.core.postgres import sanitize_db_url, LiveSignalDB
from backend.app.db.database import sanitize_db_url as sanitize_db_url_db

def test_sanitize_db_url_redacts_password():
    url_with_pass = "postgresql://myuser:FakeTopSecretPass999@localhost:5432/mydb?sslmode=require"
    sanitized = sanitize_db_url(url_with_pass)
    assert "FakeTopSecretPass999" not in sanitized
    assert "***" in sanitized
    assert "myuser" in sanitized
    assert "localhost" in sanitized

    sanitized_db = sanitize_db_url_db(url_with_pass)
    assert "FakeTopSecretPass999" not in sanitized_db
    assert "***" in sanitized_db

def test_sanitize_db_url_empty_or_none():
    assert sanitize_db_url(None) == "<EMPTY>"
    assert sanitize_db_url("") == "<EMPTY>"
    assert sanitize_db_url_db(None) == "<EMPTY>"
    assert sanitize_db_url_db("") == "<EMPTY>"

def test_live_signal_db_table_args_preserves_both_constraints():
    table = LiveSignalDB.__table__
    index_names = {idx.name for idx in table.indexes}
    constraint_names = {c.name for c in table.constraints}

    assert 'idx_unique_active_signal' in index_names
    assert '_symbol_strategy_direction_ts_uc' in constraint_names

def test_production_sqlite_rejection_logic(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("POSTGRES_URL", "sqlite:///./prod.db")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    import importlib
    import backend.core.postgres
    with pytest.raises(ValueError, match="CRITICAL SECURITY AUDIT FAILURE: SQLite is strictly prohibited") as excinfo:
        importlib.reload(backend.core.postgres)
    assert "FakeTopSecretPass999" not in str(excinfo.value)

def test_production_missing_url_logic(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    import importlib
    import backend.core.postgres
    with pytest.raises(ValueError, match="CRITICAL SECURITY AUDIT FAILURE: Production environment requires a valid PostgreSQL URL") as excinfo:
        importlib.reload(backend.core.postgres)
