# Phase 9.4.92 Test Evidence & Incident Diagnostics

## 1. Focused Acceptance Gate Test Results

```
Command: python -m pytest backend/tests/integration/test_phase9472_acceptance_gate.py -v
Exit Code: 0
Duration: 2.94s
Passed: 5 / 5

backend/tests/integration/test_phase9472_acceptance_gate.py::test_full_acceptance_gate_pipeline_and_adversarial_tampering PASSED
backend/tests/integration/test_phase9472_acceptance_gate.py::test_staging_publication_failure_preserves_previous_set PASSED
backend/tests/integration/test_phase9472_acceptance_gate.py::test_concurrent_publication_safety PASSED
backend/tests/integration/test_phase9472_acceptance_gate.py::test_empty_symbol_universe_handling PASSED
backend/tests/integration/test_phase9472_acceptance_gate.py::test_missing_dependency_isolation_guard PASSED
```

## 2. Read-Only Forensic Database Query Log

```
Command: python -c "from backend.core.postgres import SessionLocal, PriceDB, StockDB; ..."
Exit Code: 0
Output:
=== PriceDB Read-Only Forensic Summary ===
Total StockDB records: 500
Total PriceDB records: 2327346

Record counts by Source label:
  - Source: 'BACKFILL_2015_CANONICAL'           -> Count: 200489
  - Source: 'NIFTY500_BULK_2015'                -> Count: 1334934
  - Source: 'YFINANCE_AUTHENTIC'                -> Count: 396283
  - Source: 'YFinance_10Y_Canonical'            -> Count: 395640
```

## 3. Quarantined Active Report Set Validation Output

```
Command: python scripts/audit/validate_audit_csvs.py --dir reports
Exit Code: 0
Quarantined Set ID: SET_69D4DB80F18E_1792647538 (v2.2-ISO)
Quarantine Status: UNTRUSTED & QUARANTINED (False Readiness Certification)

[+] Loaded report manifest: SET_69D4DB80F18E_1792647538 (v2.2-ISO)
[+] Manifest SHA256 integrity verified across all 5 report files.
[SUCCESS] Independent Audit Acceptance Validator verified all CSV invariants cleanly across 500 evaluated symbols!
          Verified Ready        : 500
          Insufficient History  : 0
          Duplicate Conflicts   : 0
          Unverified Provenance : 0
          Invalid OHLCV         : 0
          No Data               : 0
```

## 4. Backend Full Suite Execution Results

```
Command: python -m pytest backend/tests/ -v
Exit Code: 0
Duration: 234.24s
Collected: 428
Passed: 428 / 428
Failed: 0
Skipped: 0
```

## 5. Frontend Production Build Execution Results

```
Command: npm --prefix web run build
Exit Code: 0
Duration: 12.72s
Output: web/dist/index.html created successfully
Chunk Warning: Minified index JS chunk >500kB (1,226 kB / gzip: 335 kB)
```
