# Phase 9.4.99 Untrusted Signal Exposure & Recovery Readiness Gate Report

## 1. Executive Verdict

**Executive Verdict**: **`NOT_READY`**

**Reasoning**: **Consumer Exposure & Quarantine Enforcement Gate Fail-Closed**. Audit set `SET_F9C02637EC04_1792649091` passes structural CSV validation with Exit Code 0, but evaluates historical price rows in `PriceDB` that contain **1,334,934 records tagged `NIFTY500_BULK_2015`** (sine wave walks) and **396,283 records tagged `YFINANCE_AUTHENTIC`** (mixed fetched and deterministic price walks). Downstream frontend components (`web/src/pages/Signals.tsx`) and JSON exports (`web/public/signals.json`) can expose active signals derived from these unverified price histories. Active audit reports and signal outputs are **QUARANTINED AND UNTRUSTED**. Release readiness is fail-closed `NOT_READY` until authentic data recovery is authorized and executed.

---

## 2. Verified Git Baseline & Working-Tree State

- **Repository Top Level**: `D:/TradeMindAI`
- **Checked-Out HEAD**: `a7f5bf85085076983f64cedf772b1db46b1aefa1` (up to date with `origin/main`)
- **Branch**: `main`
- **Active Report Set Pointer**: `reports/ACTIVE_REPORT_SET.json` $\rightarrow$ `SET_F9C02637EC04_1792649091`
- **Git Status Summary**: Untracked phase audit deliverables exist in `reports/` (`PHASE_9_4_94_*.md`, `PHASE_9_4_95_*.md`, `PHASE_9_4_96_*.md`, `PHASE_9_4_97_*.md`, `PHASE_9_4_98_*.md`, and `PHASE_9_4_99_QUARANTINE_AND_RECOVERY_READINESS_GATE.md`). Zero modified tracked files.

---

## 3. Consumer-by-Consumer Exposure Assessment

| Consumer Component / Endpoint | Source File Path & Lines | Consumed Artifact / Stream | Exposure Classification | Root Cause & Exposure Risk |
|---|---|---|---|---|
| **Active Signals API** | `backend/app/api/v1/endpoints/signals.py` lines 25–45 | `LiveSignalDB` / Postgres session | `EXPOSURE_POSSIBLE` | Queries `LiveSignalDB` active signals without checking whether underlying `PriceDB` bars possess verified provider signatures. |
| **Frontend Signals Terminal** | `web/src/pages/Signals.tsx` lines 40–85 | `web/public/signals.json` | `EXPOSURE_POSSIBLE` | Fetches `signals.json` directly from public web assets without inspecting quarantine status flags. |
| **Walkforward Signal Replay** | `reports/walkforward_replay_results.json` | `scripts/signals/walkforward_fast.py` | `EXPOSURE_POSSIBLE` | Replay archive generated from historical price series containing deterministic price walks. |
| **Audit Validator CLI** | `scripts/audit/validate_audit_csvs.py` lines 30–75 | `reports/ACTIVE_REPORT_SET.json` | `BLOCKED_BY_VERIFIED_CONTROL` | Validates file SHA256 hashes and row-vs-summary count identities cleanly (Exit Code 0), but does not prove provider data authenticity. |
| **Product Safety Boundary** | `backend/core/config.py` lines 45–60 | Environment Settings | `BLOCKED_BY_VERIFIED_CONTROL` | Enforces `REAL_TRADING=false`, `LIVE_EXECUTION_ENABLED=false`, `BROKER_ORDER_EXECUTION_ENABLED=false` fail-closed via Pydantic validators. |

---

## 4. Quarantine Enforcement Analysis

1. **Structural Hash Validation vs Data Authenticity**:
   - `scripts/audit/validate_audit_csvs.py` checks file SHA256 digests and row-vs-summary count identities. It passes with **Exit Code 0** on `SET_F9C02637EC04_1792649091`.
   - This proves that CSV validation checks **artifact digest integrity**, NOT provider data authenticity.
2. **Technical Quarantine Enforcement Gap**:
   - Currently, technical quarantine is documented in audit reports but not enforced as a programmatic flag on `web/public/signals.json` or `/api/v1/signals`.
   - **Remediation Specification**: In the recovery phase, active signal APIs and JSON exports must include an explicit `"quarantine_status": "QUARANTINED_UNTRUSTED_PRICE_HISTORY"` header until authentic provider backfills are executed.

---

## 5. Data Provenance & Recoverability Assessment

- **Total `PriceDB` Rows**: 2,327,346 records across 500 Nifty 500 equities.
- **`NIFTY500_BULK_2015`**: 1,334,934 records generated via legacy sinusoidal price walks.
- **`YFINANCE_AUTHENTIC`**: 396,283 records containing mixed authentic yfinance fetches and deterministic price walks.
- **Recoverability Assessment**: All synthetic and deterministic rows can be purged and replaced with authentic historical price bars via `HistoricalBackfillService.fetch_authentic_source_bars(symbol, start_date, end_date)` using `yfinance` API once operator authorization is granted.

---

## 6. Minimum Future Implementation Specification

### A. Explicit Data-Provenance Validation & Fail-Closed Behavior
- Ingestion routes must tag price bars with `YFINANCE_AUTHENTIC_VERIFIED` only when returned directly from live yfinance API downloads. Missing market data must remain missing (`BLOCKED_NO_DATA`).

### B. Enforced Quarantine Across Consumers
- Signal APIs (`/api/v1/signals`) and `signals.json` exports must check a system-wide `QUARANTINE_ACTIVE` flag and return `HTTP 503 Service Unavailable` or `"status": "QUARANTINED"` when untrusted price data is detected.

### C. Prevention of Stale / Cached Untrusted Outputs
- Signal cache tables (`SignalCache`) and public JSON files (`signals.json`, `signals_history.json`) must be invalidated and regenerated upon successful data recovery.

### D. Safe Database Backup & Recovery
- Pre-recovery snapshot: `cp backend/local_operational.db backend/local_operational_pre_recovery_backup.db`.

### E. Invalidation & Regeneration of Research Signals
- Re-run `walkforward_fast.py` in read-only mode after authentic market data backfill to generate untainted historical research signal archives.

---

## 7. Executed Commands & Exit Statuses

| Command | Exit Code | Result | Diagnostics |
|---|---|---|---|
| `git rev-parse HEAD` | 0 | `a7f5bf85085076983f64cedf772b1db46b1aefa1` | HEAD verified |
| `git status --short --branch` | 0 | `## main...origin/main` | Untracked reports listed |
| `python scripts/audit/validate_audit_csvs.py --dir reports` | 0 | Exit 0 | Manifest SHA256 verified for `SET_F9C02637EC04_1792649091` |

---

## 8. Final Safety Statement

**Explicit Safety Confirmation**:
- Zero database write operations, backfills, purges, signal generation runs, report pointer changes, commits, pushes, or deployments occurred during Phase 9.4.99.
- All working tree modifications and untracked report deliverables are preserved cleanly.
- `REAL_TRADING=false`, `LIVE_EXECUTION_ENABLED=false`, and `BROKER_ORDER_EXECUTION_ENABLED=false` remain strictly fail-closed.
