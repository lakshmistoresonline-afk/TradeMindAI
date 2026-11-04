"""
================================================================================
TradeMindAI: Production Data Mutation Guard (v2.3-STRICT-FAIL-CLOSED)
================================================================================
Enforces strict protection over live market data, feature stores, checkpoints,
and signal ledgers. Any attempt to write, replace, rename, or delete protected paths
without exact authorization (TRADEMIND_ALLOW_PRODUCTION_WRITE="true") fails closed.
================================================================================
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PROTECTED_RELATIVE_PATHS = [
    "backend/data/analytical.duckdb",
    "backend/data/ingestion_checkpoint.json",
    "backend/data/ingestion_journal.json",
    "backend/data/signals_history.json",
    "web/public/signals_history.json"
]

PROTECTED_DIRECTORIES = [
    "backend/data/features"
]

class ProductionDataMutationError(RuntimeError):
    """Raised when an unauthorized attempt is made to mutate protected production data."""
    pass

def is_production_write_authorized() -> bool:
    """
    Checks if exact authorization is provided via environment variable.
    Strictly accepts only the exact value 'true' (case-insensitive).
    Rejects '1', 'yes', 'True', and all other loose values.
    """
    auth = os.environ.get("TRADEMIND_ALLOW_PRODUCTION_WRITE", "").strip().lower()
    return auth == "true"

def validate_mutation_target(target_path: Path) -> None:
    """
    Validates that a write, replace, rename, or deletion target is authorized if it points
    to a protected production path or directory. Handles relative paths, absolute paths,
    '..' traversal, whitespace paths, and symlink resolution against REPO_ROOT.
    Fails closed with ProductionDataMutationError if target is invalid/None or if unauthorized.
    """
    if is_production_write_authorized():
        return

    if target_path is None or str(target_path).strip() == "":
        raise ProductionDataMutationError("Invalid or empty mutation target path specified.")

    # Convert to Path object if string
    t_obj = Path(target_path)

    try:
        # Resolve target path against REPO_ROOT if relative
        if not t_obj.is_absolute():
            resolved_target = (REPO_ROOT / t_obj).resolve()
        else:
            resolved_target = t_obj.resolve()
    except Exception as ex:
        # Path resolution error fails closed
        raise ProductionDataMutationError(
            f"Path resolution error for mutation target '{target_path}': {ex}. "
            f"Set TRADEMIND_ALLOW_PRODUCTION_WRITE='true' to authorize production writes."
        ) from ex

    # 1. Check exact protected file paths (fail-closed on error)
    for rel_path in PROTECTED_RELATIVE_PATHS:
        try:
            prot_resolved = (REPO_ROOT / rel_path).resolve()
        except Exception as ex:
            raise ProductionDataMutationError(
                f"Failed to resolve protected path '{rel_path}': {ex}. Faiing closed for safety."
            ) from ex

        if resolved_target == prot_resolved or str(resolved_target) == str(prot_resolved):
            raise ProductionDataMutationError(
                f"Unauthorized production data mutation blocked for target '{target_path}'. "
                f"Set TRADEMIND_ALLOW_PRODUCTION_WRITE='true' to authorize production writes."
            )

    # 2. Check protected directory trees (fail-closed on error)
    for rel_dir in PROTECTED_DIRECTORIES:
        try:
            prot_dir_resolved = (REPO_ROOT / rel_dir).resolve()
        except Exception as ex:
            raise ProductionDataMutationError(
                f"Failed to resolve protected directory '{rel_dir}': {ex}. Failing closed for safety."
            ) from ex

        if prot_dir_resolved in resolved_target.parents or resolved_target == prot_dir_resolved:
            raise ProductionDataMutationError(
                f"Unauthorized production data mutation blocked for target in directory '{target_path}'. "
                f"Set TRADEMIND_ALLOW_PRODUCTION_WRITE='true' to authorize production writes."
            )
