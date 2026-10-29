# TradeMindAI R4.6.40 — Post-Reset Repository Preservation Gate & Forensic Evidence Reconciliation

## 1. Executive Gate Verdict

**Preservation Gate Verdict**: **`BLOCKED`** (Preservation Hold Active; Phase 1 Blocked)  
**Backup Snapshot Integrity**: **`PASS`** (100% SHA-256 match for 206 core manifest files; 201/201 Parquet stores individually verified for readability)  
**Report Archive Content Verification**: **`PASS (NORMALIZED EQUIVALENCE)`** (772/772 deleted tracked report paths match Git HEAD content **100.0% SHA-256 content-equivalent** upon applying standard CRLF-to-LF normalization against Git HEAD)  
**Report Count Scope Reconciliation**: **`RECONCILED`** (652 tracked root files + 120 tracked subdirectory files = 772 total deleted tracked paths; 652 tracked root files + 92 additional root files = 744 root files; 744 root files + 120 subdirectory files = 864 total archived files)  
**Extra Archive Files Provenance**: **`UNKNOWN — NOT VERIFIED`** (92 additional archive files at `old_reports/` root; origin and creation timeline UNKNOWN — NOT VERIFIED)  
**Live Data Store Reset**: **`PASS`** (DuckDB `daily_ohlcv` table: 0 rows; live Parquet feature store: 0 files)  
**Frontend Source File Presence**: **`PASS (FILES PRESENT)`** (`web/src` component files observed present in working tree; full content preservation not independently verified)  
**Repository Preservation Attribution**: **`UNKNOWN — NOT PROVEN`** (Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence)  
**Environment Config Preservation**: **`NOT VERIFIED`** (`.env` file presence observed; content hashes not compared)  
**Safety Invariants Verification**: **`PASS (RUNTIME SETTINGS CHECK)`** (Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.)

---

## 2. Task 1 — Backup Evidence & Individual Parquet Verification

- **Backup Snapshot Directory**: `backend/data/backup_snapshot_r4640/`
- **SHA-256 Manifest**: `backend/data/backup_snapshot_r4640/SHA256SUMS.txt` (206 expected entries)
- **Hash Verification Outcome**: **206 Matches, 0 Mismatches, 0 Missing**.
- **Per-File Parquet Store Readability**:
  - Total Parquet files in backup: **201 files**
  - Readability Status: **201/201 VALID** (0 read or schema errors)
  - Cumulative Parquet Row Count: **194,766 OHLCV rows** across 201 equities (avg ~969 rows/symbol due to varying row counts)
  - Verified Schema: 47 feature columns (`date`, `Open`, `High`, `Low`, `Close`, `Volume`, `Dividends`, `Stock Splits`, `ema_20`, `sma_20`, etc.)
  - Scope Qualification: Readability and row/column structure verified; deep OHLCV value bounds & full historical coverage not audited (`NOT VERIFIED`).
- **Backed-Up DuckDB Database Readability**:
  - Opened read-only successfully at `backend/data/backup_snapshot_r4640/analytical.duckdb`
  - Tables found: `daily_ohlcv` with **14,730 total rows** across 6 pilot symbols: 4 equities (ABB, LTF, RELIANCE, TCS) with 2,916 rows each, ATGL with 1,968 rows, and LICI with 1,098 rows ($4 \times 2,916 + 1,968 + 1,098 = 14,730$).
- **Backup Directory File Accounting**:
  - Core market data files (DuckDB, Parquet stores, checkpoints): **206 files**
  - Archived old audit reports (`old_reports/`): **864 files** (mapped 772/772 deleted tracked report paths 1-to-1 with 100.0% CRLF-to-LF normalized SHA-256 content match against Git HEAD; 92 additional archive files at `old_reports/` root classified as `UNKNOWN — NOT VERIFIED`)
  - Metadata files: **2 files** (`SHA256SUMS.txt`, `manifest.json`)
  - Total files in backup tree: **1,072 files**

---

## 3. Task 2 — Repository Change Footprint Reconciliation

| Directory / Target Path | Status | Footprint & Attribution Audit |
|---|---|---|
| `backend/data/analytical.duckdb` | **PASS** | Cleared `daily_ohlcv` table (14,730 $\rightarrow$ 0 rows). Schema and tables preserved. |
| `backend/data/features/*.parquet` | **PASS** | 201 Parquet feature store files removed in Category A reset (100% backed up in `backup_snapshot_r4640/features/`). |
| `backend/data/ingestion_checkpoint.json` | **PASS** | Checkpoint reset to `{}` in Category B reset. |
| `backend/data/sync_checkpoint.json` | **PASS** | Checkpoint reset to `{}` in Category B reset. |
| `web/public/signals_history.json` | **PASS** | Removed stale static signal history file in static quarantine bypass fix. |
| `web/package.json` & `web/package-lock.json` | **UNKNOWN — NOT PROVEN** | Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence. |
| `web/src/pages/EquitySignals.tsx` | **UNKNOWN — NOT PROVEN** | Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence. |
| `web/src/utils/nseDateUtils.ts` | **UNKNOWN — NOT PROVEN** | Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence. |
| `.env`, `.env.*` | **NOT VERIFIED** | File presence observed; before/after content hash comparison not performed. |
| `reports/` | **PASS (NORMALIZED EQUIVALENCE)** | 772/772 deleted tracked report paths mapped 1-to-1 to `backup_snapshot_r4640/old_reports/` with 100% CRLF-to-LF normalized SHA-256 content match against Git HEAD. Active reports preserved. |

---

## 4. Task 3 — Report Claims Corrections

1. **Archive Content Terminology**: Described report archive content verification as **“100% SHA-256 content equivalence after CRLF-to-LF normalization against Git HEAD”**, distinguishing it from raw byte-for-byte identity.
2. **Report Count Reconciliation**: Clarified that 652 tracked root files + 120 tracked subdirectory files = 772 total deleted tracked paths; 652 tracked root files + 92 additional root files = 744 root files; 744 root files + 120 subdirectory files = 864 total archived files.
3. **Extra Archive Files Provenance**: Set 92 additional archive files at `old_reports/` root to **`UNKNOWN — NOT VERIFIED`** (`92 additional archive files at old_reports/ root; origin and creation timeline UNKNOWN — NOT VERIFIED`).
4. **Safety-Verification Wording**: Set safety verification wording consistently to: **`Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.`**
5. **Non-Interference Attribution**: Set non-interference statement consistently to: **`NON-INTERFERENCE: NOT INDEPENDENTLY VERIFIABLE — authenticated before-and-after evidence is unavailable.`**
6. **Frontend Chronology & .env**: Set frontend diff chronology consistently to **`UNKNOWN — NOT PROVEN`** (`Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence.`) and `.env` preservation to **`NOT VERIFIED`**.

---

## 5. Test Suite Verification Output

| Verification Tool / Suite | Exit Code | Outcome | Summary Details |
|---|---|---|---|
| `python scripts/audit/verify_backup_integrity.py` | `0` | **PASS** | 206/206 SHA-256 matches; DuckDB backup readably contains 14,730 rows; Parquet backup readably contains 2,916 rows/symbol for 10-year pilot equities. |
| `python scripts/audit/verify_all_backup_parquets.py` | `0` | **PASS** | 201/201 Parquet files read individually with 0 errors; cumulative 194,766 rows across 47 feature columns. |
| `python scripts/audit/reconcile_crlf_archive.py` | `0` | **PASS (NORMALIZED EQUIVALENCE)** | 772/772 deleted tracked report files match Git HEAD content 100.0% SHA-256 content-equivalent upon CRLF-to-LF normalization. |
| `python scripts/audit/inspect_live_databases.py` | `0` | **PASS** | Live DuckDB `daily_ohlcv` table has 0 rows; live Parquet feature store has 0 files; checkpoints reset to `{}`. |
| `captured pytest log output` | `0` | **REPORTED BUT NOT INDEPENDENTLY RECHECKED** | 36 unit tests in `test_operational_api.py` and `test_quarantine_enforcement.py` passed in captured run output; not re-executed in this read-only audit. |

---

## 6. Safety Invariants & Release Decision

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.
- **Overall Gate Verdict**: **`BLOCKED`** (Preservation Hold Active). TejHQ data provider integration (Phase 1) remains blocked until user instruction.
