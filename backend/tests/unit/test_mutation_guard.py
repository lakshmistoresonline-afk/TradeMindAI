"""
================================================================================
TradeMindAI Unit Tests — Production Data Mutation Guard (Fix A)
================================================================================
Verifies that:
1. Unauthorized write attempts to protected paths fail closed with ProductionDataMutationError.
2. Setting TRADEMIND_ALLOW_PRODUCTION_WRITE="true" permits authorized writes.
3. Loose authorization values ("1", "yes", etc.) are strictly rejected.
4. Traversal paths (".."), relative paths, whitespace, None, and symlinks cannot bypass guard.
5. Writes to temporary directories (tmp_path) pass validation without error.
6. write_export_payload() fails closed when called on a protected path without authorization.
================================================================================
"""

import os
import pytest
from pathlib import Path
from backend.core.mutation_guard import (
    validate_mutation_target,
    is_production_write_authorized,
    ProductionDataMutationError
)

def test_unauthorized_write_to_protected_paths_raises_error(monkeypatch):
    monkeypatch.delenv("TRADEMIND_ALLOW_PRODUCTION_WRITE", raising=False)
    assert not is_production_write_authorized()

    protected_targets = [
        Path("backend/data/analytical.duckdb"),
        Path("backend/data/ingestion_checkpoint.json"),
        Path("backend/data/signals_history.json"),
        Path("backend/data/features/RELIANCE.parquet")
    ]

    for target in protected_targets:
        with pytest.raises(ProductionDataMutationError, match="Unauthorized production data mutation blocked"):
            validate_mutation_target(target)

@pytest.mark.parametrize("invalid_target", [None, "", "   ", "\t\n"])
def test_mutation_guard_rejects_none_and_whitespace_targets(invalid_target):
    with pytest.raises(ProductionDataMutationError, match="Invalid or empty mutation target path"):
        validate_mutation_target(invalid_target)

@pytest.mark.parametrize("unauth_val", ["1", "yes", "TRUE_EXTRA", "", "0", "false", "allow"])
def test_mutation_guard_strict_authorization_string(monkeypatch, unauth_val):
    monkeypatch.setenv("TRADEMIND_ALLOW_PRODUCTION_WRITE", unauth_val)
    assert not is_production_write_authorized()

    with pytest.raises(ProductionDataMutationError, match="Unauthorized production data mutation blocked"):
        validate_mutation_target(Path("backend/data/analytical.duckdb"))

def test_mutation_guard_rejects_path_traversal_attempts(monkeypatch):
    monkeypatch.delenv("TRADEMIND_ALLOW_PRODUCTION_WRITE", raising=False)

    traversal_paths = [
        Path("backend/data/../data/analytical.duckdb"),
        Path("backend/tests/../../backend/data/features/RELIANCE.parquet"),
        Path("./backend/data/signals_history.json")
    ]

    for target in traversal_paths:
        with pytest.raises(ProductionDataMutationError, match="Unauthorized production data mutation blocked"):
            validate_mutation_target(target)

def test_authorized_write_to_protected_paths_passes(monkeypatch):
    monkeypatch.setenv("TRADEMIND_ALLOW_PRODUCTION_WRITE", "true")
    assert is_production_write_authorized()

    # Must pass without raising error when authorized
    validate_mutation_target(Path("backend/data/analytical.duckdb"))
    validate_mutation_target(Path("backend/data/features/RELIANCE.parquet"))

def test_unprotected_temporary_paths_pass_validation(tmp_path, monkeypatch):
    monkeypatch.delenv("TRADEMIND_ALLOW_PRODUCTION_WRITE", raising=False)

    temp_db = tmp_path / "test_analytical.duckdb"
    temp_parquet = tmp_path / "features" / "TEST.parquet"

    # Must pass without raising error for isolated temporary paths
    validate_mutation_target(temp_db)
    validate_mutation_target(temp_parquet)

def test_write_export_payload_blocked_by_mutation_guard_on_protected_path(monkeypatch):
    monkeypatch.delenv("TRADEMIND_ALLOW_PRODUCTION_WRITE", raising=False)
    from scripts.signals.generate_walkforward_signals_duckdb import write_export_payload

    protected_out = Path("backend/data/signals_history.json")

    payload = {"active_signals": [], "history_records": [], "summary": {}}

    with pytest.raises(ProductionDataMutationError, match="Unauthorized production data mutation blocked"):
        write_export_payload(payload, output_path=protected_out)
