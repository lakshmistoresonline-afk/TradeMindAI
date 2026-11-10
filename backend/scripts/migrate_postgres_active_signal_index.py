"""
================================================================================
TradeMindAI: Dedicated PostgreSQL Active Signal Uniqueness Migration & Preflight CLI
================================================================================
Provides preflight inspection and explicitly authorized migration execution for the
authoritative PostgreSQL partial unique index `idx_unique_active_signal`.
Exclusively targets PostgreSQL dialect. Performs ZERO DDL or data mutation in default preflight mode.
================================================================================
"""

import sys
import os
import json
import argparse
import logging
from urllib.parse import urlparse, urlunparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import text
from backend.core.postgres import postgres_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PostgresMigrationCLI")

def sanitize_engine_url(url: str) -> str:
    """
    Sanitizes database connection URL string to redact passwords and sensitive credentials.
    """
    if not url:
        return "<EMPTY>"
    try:
        parsed = urlparse(url)
        if parsed.password:
            user = parsed.username or ""
            host = parsed.hostname or ""
            port = f":{parsed.port}" if parsed.port else ""
            netloc = f"{user}:***@{host}{port}"
            parsed = parsed._replace(netloc=netloc)
        return urlunparse(parsed)
    except Exception:
        return "<REDACTED_URL>"

def run_postgres_preflight(engine=None) -> dict:
    """
    Executes a 100% read-only preflight check against PostgreSQL catalog and live_signals table.
    Unconditionally enforces PostgreSQL dialect check. Redacts connection credentials.
    """
    target_engine = engine or postgres_engine
    result = {
        "engine": sanitize_engine_url(str(target_engine.url)),
        "engine_dialect": target_engine.name,
        "table_exists": False,
        "duplicate_active_symbols_found": 0,
        "duplicate_active_records": [],
        "index_exists": False,
        "index_definition_valid": False,
        "preflight_status": "BLOCKED_PREFLIGHT_DEFAULT",
        "reason": None
    }

    if target_engine.name != "postgresql":
        result["preflight_status"] = "BLOCKED_DATABASE_DIALECT"
        result["reason"] = f"Non-PostgreSQL dialect detected ({target_engine.name}). PostgreSQL migration CLI requires a valid PostgreSQL database engine."
        return result

    try:
        with target_engine.connect() as conn:
            # 1. Verify live_signals table existence in catalog
            tbl_check = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name='live_signals'")).fetchall()
            if not tbl_check:
                result["preflight_status"] = "BLOCKED_TABLE_MISSING"
                result["reason"] = "TABLE_LIVE_SIGNALS_NOT_FOUND"
                return result

            result["table_exists"] = True

            # 2. Inspect required columns in catalog
            col_check = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='live_signals'")).fetchall()
            existing_cols = [r[0] for r in col_check]

            if "symbol" not in existing_cols or "status" not in existing_cols:
                result["preflight_status"] = "BLOCKED_REQUIRED_COLUMN_MISSING"
                result["reason"] = "REQUIRED_COLUMNS_SYMBOL_OR_STATUS_MISSING"
                return result

            # 3. Inspect active-signal duplicates by symbol
            dups = conn.execute(text(
                "SELECT symbol, COUNT(*) as cnt FROM live_signals WHERE status = 'ACTIVE' GROUP BY symbol HAVING COUNT(*) > 1"
            )).fetchall()

            if dups:
                result["duplicate_active_symbols_found"] = len(dups)
                result["duplicate_active_records"] = [dict(row._mapping) for row in dups]
                result["preflight_status"] = "BLOCKED_DUPLICATE_ACTIVE_SYMBOLS"
                result["reason"] = f"EXISTING_DUPLICATE_ACTIVE_SIGNALS_FOUND: {len(dups)} symbols conflict"
                return result

            # 4. Inspect database catalog for exact index definition
            idx_info = conn.execute(text(
                "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'live_signals' AND indexname = 'idx_unique_active_signal'"
            )).fetchone()

            if idx_info:
                result["index_exists"] = True
                idx_def = str(idx_info[1] or "").lower()
                if "unique" in idx_def and "(symbol)" in idx_def and "status = 'active'" in idx_def:
                    result["index_definition_valid"] = True
                    result["preflight_status"] = "ALREADY_MIGRATED"
                    return result
                else:
                    result["index_definition_valid"] = False
                    result["preflight_status"] = "BLOCKED_INVALID_EXISTING_INDEX"
                    result["reason"] = f"INVALID_INDEX_DEFINITION_DETECTED: {idx_info[1]}"
                    return result

            result["preflight_status"] = "READY_TO_MIGRATE"
            return result
    except Exception as e:
        result["preflight_status"] = "PREFLIGHT_ERROR"
        result["reason"] = f"PREFLIGHT_EXCEPTION: {e}"
        return result

def execute_postgres_migration(engine=None) -> dict:
    """
    Executes explicit PostgreSQL DDL after preflight validation succeeds.
    Creates `idx_unique_active_signal` partial unique index on `live_signals(symbol) WHERE status = 'ACTIVE'`.
    Unconditionally rejects non-PostgreSQL dialects.
    """
    target_engine = engine or postgres_engine

    if target_engine.name != "postgresql":
        return {
            "migration_status": "BLOCKED",
            "error": f"Non-PostgreSQL dialect detected ({target_engine.name}). Migration execution requires a valid PostgreSQL database engine."
        }

    preflight = run_postgres_preflight(target_engine)

    if preflight["preflight_status"] == "ALREADY_MIGRATED":
        return {
            "migration_status": "SUCCESS",
            "preflight": preflight,
            "message": "Database is already migrated."
        }

    if preflight["preflight_status"] != "READY_TO_MIGRATE":
        return {
            "migration_status": "BLOCKED",
            "preflight": preflight,
            "error": preflight.get("reason")
        }

    try:
        with target_engine.connect() as conn:
            logger.info("[Migration] Executing explicit DDL on %s...", target_engine.name)
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_signal ON live_signals (symbol) WHERE status = 'ACTIVE'"))
            conn.commit()
            logger.info("[Migration] DDL committed. Verifying catalog...")

        post_check = run_postgres_preflight(target_engine)
        if post_check.get("preflight_status") == "ALREADY_MIGRATED" and post_check.get("index_definition_valid") is True:
            return {
                "migration_status": "SUCCESS",
                "preflight": post_check
            }
        else:
            return {
                "migration_status": "FAILED_VERIFICATION",
                "preflight": post_check,
                "error": "Index creation DDL executed but post-migration catalog verification failed or index definition is invalid."
            }
    except Exception as ex:
        return {
            "migration_status": "EXECUTION_EXCEPTION",
            "error": str(ex)
        }

def main():
    parser = argparse.ArgumentParser(description="TradeMindAI PostgreSQL Active Signal Index Migration CLI")
    parser.add_argument("--execute", action="store_true", help="Execute DDL migration after preflight check")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    args = parser.parse_args()

    if args.execute:
        logger.info("=== [MIGRATION CLI] Mode: EXPLICIT MIGRATION EXECUTION ===")
        res = execute_postgres_migration()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Migration Result: status='{res['migration_status']}'")
        if res.get("migration_status") != "SUCCESS":
            sys.exit(1)
    else:
        logger.info("=== [MIGRATION CLI] Mode: PREFLIGHT CHECK ONLY (No DDL Executed) ===")
        res = run_postgres_preflight()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Preflight Result: status='{res['preflight_status']}', table='{res['table_exists']}', dups='{res['duplicate_active_symbols_found']}', index='{res['index_exists']}'")
        if res.get("preflight_status") not in ("READY_TO_MIGRATE", "ALREADY_MIGRATED"):
            sys.exit(1)

if __name__ == "__main__":
    main()
