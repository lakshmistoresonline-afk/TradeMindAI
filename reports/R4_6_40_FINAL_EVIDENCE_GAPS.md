# TradeMindAI R4.6.40 — Final Evidence Gaps & Archive Provenance Report

## 1. Executive Summary & Verdict Matrix

**Overall Preservation Gate Verdict**: **`BLOCKED`** (Preservation Hold Active; Phase 1 TejHQ Integration Blocked)  
**Backup Snapshot Integrity**: **`PASS`** (206/206 core market files matched SHA-256 manifest; 201/201 Parquet feature files readably verified)  
**Report Archive Content Verification**: **`PASS (NORMALIZED EQUIVALENCE)`** (772/772 deleted tracked report paths match Git HEAD content **100.0% SHA-256 content-equivalent** upon applying standard CRLF-to-LF normalization against Git HEAD)  
**Report File Count Reconciliation**: **`RECONCILED`** (652 tracked root files + 120 tracked subdirectory files = 772 total deleted tracked paths; 652 tracked root files + 92 additional root files = 744 root files; 744 root files + 120 subdirectory files = 864 total archived files)  
**Extra Archive Files Provenance**: **`UNKNOWN — NOT VERIFIED`** (92 additional archive files at `old_reports/` root; origin and creation timeline UNKNOWN — NOT VERIFIED)  
**Frontend Git Diff Chronology Attribution**: **`UNKNOWN — NOT PROVEN`** (Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence)  
**Environment Config Preservation**: **`NOT VERIFIED`** (`.env` file presence observed; before/after byte hash comparison not performed)  
**Safety Invariants Verification**: **`PASS (RUNTIME SETTINGS CHECK)`** (Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.)

---

## 2. Categorized Forensic Evidence Matrix

| Area / Target Claim | Verification Method | Observed Evidence / Outcome | Verdict | Remaining Limitation |
|---|---|---|---|---|
| **Core Backup SHA-256 Manifest** | Recomputed SHA-256 digests (`verify_backup_integrity.py`) | 206/206 manifest files matched SHA-256 digests. Zero mismatches, zero missing. | **PASS** | Core manifest covers 206 market data files; report archives tracked separately. |
| **Individual Parquet Store Readability** | Per-file Parquet inspection (`verify_all_backup_parquets.py`) | All 201 backed-up `.parquet` files read individually with 0 schema errors (cumulative 194,766 rows). | **PASS** | Basic row/column structure readably verified; deep OHLCV price bounds & historical coverage not audited. |
| **Full Parquet Data Quality & Coverage** | Readability inspection only | Sample `ABB.parquet` read with 2,916 rows and 47 feature columns; full backup store contains 194,766 cumulative rows across 201 symbols (avg ~969 rows/symbol due to varying row counts). | **NOT VERIFIED** | Value bounds, duplicate timestamps, and full 10-year market date coverage not audited. |
| **DuckDB Backup Readability & Row Count** | Read-only connection (`verify_backup_integrity.py`) | `analytical.duckdb` opened read-only; contains `daily_ohlcv` table with 14,730 total rows across 6 pilot symbols: ABB (2,916), LTF (2,916), RELIANCE (2,916), TCS (2,916), ATGL (1,968), LICI (1,098), yielding 4 x 2,916 + 1,968 + 1,098 = 14,730. | **PASS** | `daily_ohlcv` row count verified; other potential analytical database objects not audited. |
| **Report Archive Path Reconciliation** | Path matching (`reconcile_report_archive.py`) | 772/772 deleted tracked report files mapped 1-to-1 to relative paths in `old_reports/`. | **PASS (PATHS)** | All 772 deleted tracked report relative paths exist in `old_reports/`. |
| **Report Archive Content Verification** | SHA-256 against Git HEAD with CRLF-to-LF normalization (`reconcile_crlf_archive.py`) | **772 / 772 deleted tracked report files** match Git HEAD content **100.0% SHA-256 content-equivalent** when applying `\r\n` $\rightarrow$ `\n` line ending normalization (1 raw byte match without normalization). | **PASS (NORMALIZED EQUIVALENCE)** | Establishes 100% content equivalence to Git HEAD after CRLF-to-LF normalization, distinct from raw byte-for-byte identity on disk. |
| **Unmanifested Archive Files Provenance** | Directory tree walk (`reconcile_crlf_archive.py`) | 864 total files in `old_reports/` directory tree (772 matched tracked reports + 92 extra files at `old_reports/` root). | **UNKNOWN — NOT VERIFIED** | 92 additional archive files at `old_reports/` root; origin and creation timeline UNKNOWN — NOT VERIFIED. |
| **Live DuckDB Market Data Reset** | Read-only connection (`inspect_live_databases.py`) | `daily_ohlcv` table contains **0 rows**. Table schema and 9 column definitions 100% preserved. | **PASS** | Schema preserved; row count zero. |
| **Live Parquet Feature Store Reset** | Directory listing (`inspect_live_databases.py`) | `backend/data/features/` contains **0 `.parquet` files**. Directory structure preserved. | **PASS** | Live feature store clear and ready for Phase 1. |
| **Frontend Source File Presence (`web/src`)** | File tree inspection | Frontend component files present in working tree. | **PASS (FILES PRESENT)** | Component source files observed present; full content preservation not independently verified. |
| **Frontend Git Diff Chronology Attribution** | Path-scoped `git status` & `git diff --stat` | Diffs in `web/package.json`, `EquitySignals.tsx`, `nseDateUtils.ts` exist in working tree. | **UNKNOWN — NOT PROVEN** | Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence. |
| **Environment Config Preservation** | File presence check | `.env` and `.env.*` configuration files present in working tree. | **NOT VERIFIED** | File presence observed; before/after content hash comparison not performed to avoid exposing secrets. |
| **Operational Health & Quarantine Enforcement** | Captured test log inspection | 36 unit tests passed in captured output of `test_operational_api.py` & `test_quarantine_enforcement.py`. | **REPORTED BUT NOT INDEPENDENTLY RECHECKED** | Operational API health endpoints and universal quarantine enforcement (`503 Service Unavailable`) reported passing in captured run output; not re-executed in this read-only audit. |

---

## 3. Reconciled Report & Backup Metric Accounting

### A. Report & Archive Arithmetic
1. **652 Tracked Root Files**: Deleted tracked report files located directly under `reports/` root.
2. **120 Tracked Subdirectory Files**: Deleted tracked report files located inside `reports/SET_*/` subdirectories.
3. **772 Total Deleted Tracked Paths**: $652\text{ tracked root} + 120\text{ tracked sub} = 772\text{ deleted tracked paths in Git index}$.
4. **92 Additional Root Files**: Extra files located directly at `old_reports/` root (`origin and creation timeline UNKNOWN — NOT VERIFIED`).
5. **744 Total Root Files**: $652\text{ tracked root} + 92\text{ additional root} = 744\text{ total root files handled by }clean\_old\_reports.py$.
6. **864 Total Archived Files**: $744\text{ root files} + 120\text{ subdirectory files} = 864\text{ total archived files in }old\_reports/$.
7. **884 Total Filesystem Nodes**: $864\text{ archived files} + 20\text{ subdirectories} = 884\text{ total filesystem nodes in }old\_reports/$.

### B. Backup Parquet vs. DuckDB Metric Reconciliation
1. **DuckDB Backup Row Breakdown**: Contains exactly 14,730 total rows across 6 pilot symbols: 4 equities (ABB, LTF, RELIANCE, TCS) with 2,916 rows each, ATGL with 1,968 rows, and LICI with 1,098 rows ($4 \times 2,916 + 1,968 + 1,098 = 14,730$ total rows).
2. **Cumulative Backup Parquet Row Count (`194,766 rows`)**: Represents the total sum of rows across all 201 Parquet feature store files in backup (including stocks with varying row counts). Parquet store readability establishes file structure and row counts, NOT full historical completeness or data correctness.

---

## 4. Path-Scoped Git Working-Tree Audit

```text
## main...origin/main
 M .github/workflows/deploy-backend.yml
 M .github/workflows/deploy-frontend.yml
 M .gitignore
 M backend/app/services/indicator_service.py
 M backend/app/services/signal_engine.py
 M backend/core/release_gate.py
 M backend/data/analytical.duckdb
 D backend/data/features/*.parquet (201 files deleted in approved reset)
 M scripts/ci_release_gate.py
 M scripts/export_history_json.py
 M scripts/export_performance_json.py
 M web/package-lock.json
 M web/package.json
 D web/public/signals_history.json (deleted in static quarantine bypass fix)
 M web/src/pages/EquitySignals.tsx
 M web/src/utils/nseDateUtils.ts
?? backend/data/backup_snapshot_r4640/ (pre-reset backup snapshot)
?? backend/data/ingestion_checkpoint.json
?? backend/data/signals_history.json
?? reports/CLEAN_RESET_REPORT.md
?? reports/POST_RESET_FORENSIC_VERIFICATION.md
?? reports/POST_RESET_REPOSITORY_PRESERVATION_GATE.md
?? reports/R4_6_40_FINAL_EVIDENCE_GAPS.md
```

- **Attribution Status**: Working-tree changes are present; their chronology relative to Phase 0 cannot be established from the available evidence (`UNKNOWN — NOT PROVEN`). Diffs in `backend/data/features/*.parquet` are attributed directly to the approved Phase 0 data cleanup.

---

## 5. Safety Invariants & Release Decision

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- **Runtime settings verification**: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.
- **Non-Interference Attribution**: NON-INTERFERENCE: NOT INDEPENDENTLY VERIFIABLE — authenticated before-and-after evidence is unavailable.
- **Overall Gate Verdict**: **`BLOCKED`** (Preservation Hold Active). TejHQ data provider integration (Phase 1) remains blocked until explicit user authorization.
