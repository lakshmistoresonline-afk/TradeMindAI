# TradeMind AI — Signal Count Reconciliation

**Date:** 2026-09-13
**Objective:** Resolve discrepancy between reported signal counts (234 vs 237).

## 1. Discrepancy Analysis
- **Forensic Audit (Earlier):** Reported 234 signals.
- **Neon/Postgres Authority (Current):** 237 signals.
- **Discrepancy:** +3 signals.

## 2. Root Cause
The discrepancy originated from a race condition between the background production scan and the generation of forensic reports. 3 additional signals for the LONG horizon were persisted to the ledger during the final verification loop of the previous session.

## 3. Authoritative Distribution (As of 2026-09-13 10:45 IST)

| Horizon | Direction | Count | Status |
| :--- | :--- | :--- | :--- |
| **SHORT** | LONG | 5 | WAITING_FOR_ENTRY |
| **SHORT** | SHORT | 90 | WAITING_FOR_ENTRY |
| **SWING** | LONG | 11 | WAITING_FOR_ENTRY |
| **SWING** | SHORT | 82 | WAITING_FOR_ENTRY |
| **LONG** | LONG | 10 | WAITING_FOR_ENTRY |
| **LONG** | SHORT | 39 | WAITING_FOR_ENTRY |
| **Total** | | **237** | |

## 4. Reconciliation Action
- The count of **237** is now the unique authoritative system truth.
- All subsequent performance metrics and UI displays must align with this ledger.
- The `live_signals` table in Neon/Postgres remains the master record.

---
**Verdict:** DISCREPANCY RESOLVED.
