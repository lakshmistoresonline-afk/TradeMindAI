# Phase 1 Changelog — Market Data Ingestion & Storage Recovery

## Changes Implemented

### 1. Storage & Dual-Store Ingestion Safety (`scripts/ingest_historical_nifty500.py`)
- Added `verify_ohlcv_value_equality()` enforcing element-wise price/volume numeric equality ($10^{-4}$ tolerance), date uniqueness, row count match, and non-finite checks (`NaN`/`Inf`).
- Implemented temporary backup copy preservation (`.tmp_backup_{symbol}_{tx_id}.parquet`) to guarantee 100% byte-for-byte dataset restoration on pre-commit replacement failure.
- Separated pre-commit failures (rolled back with backup restored) from post-commit failures (`FAILED_POST_COMMIT`).
- Added strict test failpoint guard `_check_test_failpoint(fp_name)` requiring `TRADEMIND_TEST_MODE == "true"` and `VALID_FAILPOINTS` allowlist matching.

### 2. Mutation Guard Hardening (`backend/core/mutation_guard.py`)
- Enforced strict authorization string matching (`auth == "true"`).
- Resolved target paths against `REPO_ROOT` to prevent path traversal attempts.
- Rejected `None`, empty string (`""`), and whitespace targets (`"   "`).

### 3. Unit & Subprocess Crash Test Harness (`backend/tests/unit/test_ingestion_transaction_safety.py`)
- Implemented genuine 3-process recovery test harness (`Process A Crash -> Process B OS Recovery -> Process C OS Verification & Idempotency`).
- Parameterized test suite across all 9 crash failpoint boundaries (`POST_STAGING`, `POST_INTENT_JOURNAL`, `PRE_DUCKDB_COMMIT`, `POST_DUCKDB_COMMIT`, `POST_COMMITTED_JOURNAL`, `POST_PARQUET_PROMOTION`, `POST_PROMOTED_JOURNAL`, `POST_CHECKPOINT_SAVE`, `DURING_RECOVERY`).
- Added named unit tests for orphan staging preservation and adversarial metadata/file corruption handling.
