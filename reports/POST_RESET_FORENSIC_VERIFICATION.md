# TradeMindAI R4.6.40 — Post-Reset Forensic Verification Report

## 1. Executive Summary & Verification Matrix

**Post-Reset Forensic Gate Verdict**: **`BLOCKED`** (Preservation Hold Active; Phase 1 Blocked)  
**Backup Snapshot Integrity**: **`PASS`** (206/206 core market files matched SHA-256 manifest; 201/201 Parquet stores individually verified for readability)  
**Live Database & Feature Store Reset**: **`PASS`** (DuckDB `daily_ohlcv` table: 0 rows; Parquet feature store: 0 files)  
**Report Archive Reconciliation**: **`PASS (NORMALIZED EQUIVALENCE)`** (772/772 deleted tracked report paths match Git HEAD content **100.0% SHA-256 content-equivalent** upon applying standard CRLF-to-LF normalization against Git HEAD)  
**Report Count Scope Reconciliation**: **`RECONCILED`** (652 tracked root files + 120 tracked subdirectory files = 772 total deleted tracked paths; 652 tracked root files + 92 additional root files = 744 root files; 744 root files + 120 subdirectory files = 864 total archived files)  
**Extra Archive Files Provenance**: **`UNKNOWN — NOT VERIFIED`** (92 additional archive files at `old_reports/` root; origin and creation timeline UNKNOWN — NOT VERIFIED)  
**Frontend Source File Presence**: **`PASS (FILES PRESENT)`** (`web/src` component files observed present in working tree; full content preservation not independently verified)  
**Frontend Git Diff Chronology Attribution**: **`UNKNOWN — NOT PROVEN`** (Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence)  
**Environment Config Preservation**: **`NOT VERIFIED`** (`.env` file presence observed; before/after content hash comparison not performed)  
**Safety Invariants Verification**: **`PASS (RUNTIME SETTINGS CHECK)`** (Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.)

---

## 2. Task 1 — Backup Snapshot & Hash Verification

- **Snapshot Directory**: `backend/data/backup_snapshot_r4640/`
- **SHA-256 Manifest File**: `backend/data/backup_snapshot_r4640/SHA256SUMS.txt`
- **Hash Verification Results**:
  - Total Manifest Entries: **206 core market data files**
  - SHA-256 Digest Matches: **206 files** (100% SHA-256 match)
  - SHA-256 Mismatches: **0 files**
  - Missing Files: **0 files**
- **Unmanifested Archive Files**: **864 files / 20 directories** under `backend/data/backup_snapshot_r4640/old_reports/`. Mapped 772/772 deleted tracked report paths 1-to-1 against `old_reports/`. Content comparison against Git HEAD showed **772/772 SHA-256 content-equivalent matches** (100.0%) when applying CRLF-to-LF line ending normalization (1 raw byte match without normalization). Provenance for 92 additional archive files at `old_reports/` root classified as **`UNKNOWN — NOT VERIFIED`**.
- **Backed-Up DuckDB Database Readability**:
  - `backend/data/backup_snapshot_r4640/analytical.duckdb`: Opened read-only successfully. Contains table `daily_ohlcv` with **14,730 total rows** across 6 pilot symbols: 4 equities (ABB, LTF, RELIANCE, TCS) with 2,916 rows each, ATGL with 1,968 rows, and LICI with 1,098 rows ($4 \times 2,916 + 1,968 + 1,098 = 14,730$).
- **Backed-Up Parquet Readability**:
  - `backend/data/backup_snapshot_r4640/features/`: All **201 Parquet files** inspected individually via `verify_all_backup_parquets.py`. 201/201 files read successfully with 0 schema errors, containing **194,766 cumulative OHLCV rows** across 47 feature columns (avg ~969 rows/symbol due to varying row counts). (Note: Readability verified; full historical data quality audit not performed).

---

## 3. Task 2 & Task 3 — Live Database & Artifact Audit

| Target Data Asset | Pre-Reset Metric | Live Post-Reset Metric | Health & Schema Status |
|---|---|---|---|
| **Live DuckDB (`backend/data/analytical.duckdb`)** | 14,730 rows | **0 rows** in `daily_ohlcv` | **PASS** (Table schema & 9 columns 100% preserved) |
| **Live Parquet Store (`backend/data/features/`)** | 201 `.parquet` files | **0 `.parquet` files** | **PASS** (Directory structure preserved) |
| **Ingestion Checkpoint (`ingestion_checkpoint.json`)** | 1.1 KB stale data | **`{}`** (0 items) | **PASS** |
| **Sync Checkpoint (`sync_checkpoint.json`)** | 5.7 KB stale data | **`{}`** (0 items) | **PASS** |
| **Ingestion Journal (`ingestion_journal.json`)** | Stale journal | **Absent** | **PASS** |
| **Backend Signals History (`signals_history.json`)** | 75.6 MB | 75.6 MB | **PRESERVED** (Private backend dataset) |
| **Reports Directory (`reports/`)** | 744 old markdown/CSV files | **Archived to backup snapshot** | `reports/` clean, containing active reset and forensic verification reports |

---

## 4. Task 4 — Frontend & Configuration Preservation

- **Git Status Audit**: Verified `git status --short -- web/package.json web/src/pages/EquitySignals.tsx web/src/utils/nseDateUtils.ts`. Chronology classified consistently as: `UNKNOWN — NOT PROVEN. Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence.`
- **Environment & Secrets Audit**: `.env` and `.env.*` configuration files present in working tree; before/after content hash comparison classified as **`NOT VERIFIED`**.
- **Static Public Asset Containment**: Stale public asset `web/public/signals_history.json` removed; verified 0 static JSON signal assets served in public frontend build.

---

## 5. Test Suite Verification Output

| Verification Tool / Suite | Exit Code | Outcome | Summary Evidence |
|---|---|---|---|
| `python scripts/audit/verify_backup_integrity.py` | `0` | **PASS** | 206/206 SHA-256 matches; DuckDB backup readably contains 14,730 rows; Parquet backup readably contains 2,916 rows/symbol for 10-year pilot equities. |
| `python scripts/audit/verify_all_backup_parquets.py` | `0` | **PASS** | 201/201 Parquet files read individually with 0 errors; cumulative 194,766 rows across 47 feature columns. |
| `python scripts/audit/reconcile_crlf_archive.py` | `0` | **PASS (NORMALIZED EQUIVALENCE)** | 772/772 deleted tracked report files match Git HEAD content 100.0% SHA-256 content-equivalent upon CRLF-to-LF normalization. |
| `python scripts/audit/inspect_live_databases.py` | `0` | **PASS** | Live DuckDB `daily_ohlcv` table has 0 rows; live Parquet feature store has 0 files; checkpoints reset to `{}`. |
| `captured pytest log output` | `0` | **REPORTED BUT NOT INDEPENDENTLY RECHECKED** | 36 unit tests in `test_operational_api.py` and `test_quarantine_enforcement.py` passed in captured run output; not re-executed in this read-only audit. |

---

## 6. Safety Invariants Confirmation

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.
- Non-interference attribution: `NON-INTERFERENCE: NOT INDEPENDENTLY VERIFIABLE — authenticated before-and-after evidence is unavailable.`
- **Gate Status**: **`BLOCKED`** (Preservation Hold Active). Phase 1 TejHQ data provider integration remains blocked.
