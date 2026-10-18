# TradeMindAI — Phase 9.4.4 One-Signal Dashboard Root Cause & Mismatch Audit Report

**Date:** October 17, 2026  
**Repository:** `D:\TradeMindAI`  
**Auditor:** Quantitative Systems Verification Taskforce  
**Final Verdict:** **`ROOT_CAUSE_CONFIRMED_AND_FIXED`**

---

## 1. Executive Summary & Root Cause Confirmation

An end-to-end trace of the operational database, API endpoint, and frontend UI components resolved both observed anomalies:

### Anomaly 1: Timeframe vs Direction Mismatch (`SWING = 1`, `LONG = 0` vs `LONG ▲` Card Badge)
- **Root Cause**: **CONFIRMED**
  - The summary counter cards at the top of the terminal measure **Trade Timeframe / Horizon** (`SWING`, `LONG`, `SHORT`). HDFCBANK's horizon is `SWING`, so the summary counters calculated `SWING = 1` and `LONG = 0`.
  - However, `SignalCard.tsx` and `LiveSignalCard.tsx` previously rendered a single top-right badge displaying **Trade Direction** (`LONG ▲` vs `SHORT ▼`).
  - Because HDFCBANK's direction is `LONG` (a bullish BUY trade setup), the card rendered `LONG ▲`.
- **Remediation**: Updated `SignalCard.tsx` and `LiveSignalCard.tsx` to render both **Horizon** (`SWING`) and **Direction** (`LONG ▲`), eliminating category ambiguity for users.

### Anomaly 2: Active Database Signal Count
- **Root Cause**: **CONFIRMED**
  - The operational database table `live_signals` (`LiveSignalDB`) currently contains exactly **1 row** (`HDFCBANK`).
  - The API endpoint (`GET /api/v1/equity/signals`) returned 1 record.
  - The frontend received and rendered 1 card.
  - All layers (Database, API, Frontend) are **100% in sync** with `Total Open = 1`.

---

## 2. Read-Only Reconciliation Matrix

| Metric Layer | Count | Source / Value |
|---|---:|---|
| **Total Database Rows (`live_signals`)** | **1** | `LiveSignalDB` PostgreSQL table |
| **Active Status Rows** | **1** | `HDFCBANK` (`id=sig_conc_1`) |
| **Active SWING Timeframe Rows** | **1** | `HDFCBANK` (`timeframe=SWING`) |
| **Active LONG Timeframe Rows** | **0** | Zero active signals in LONG horizon |
| **Active SHORT Timeframe Rows** | **0** | Zero active signals in SHORT horizon |
| **API Response Count** | **1** | `GET /api/v1/equity/signals` |
| **Frontend Rendered Cards** | **1** | HDFCBANK card rendered in terminal |
| **Summary Counter: Total Open** | **1** | Reconciled with active card count |
| **Summary Counter: Swing (1-30D)** | **1** | Reconciled with card horizon (`SWING`) |
| **Summary Counter: Long (1M-1Y)** | **0** | Reconciled with card horizon (`LONG=0`) |

---

## 3. Verification & Test Execution Results

1. **Backend Integration & Unit Suite**:
   - **Command**: `python -m pytest backend/tests/ -v`
   - **Result**: **128 passed in 17.79s** (Exit Code `0`).
2. **Frontend Production Build**:
   - **Command**: `npm --prefix web run build`
   - **Result**: **Passed successfully** (`built in 13.90s`).
3. **Git Whitespace & Status Check**:
   - `git diff --check` returned **empty** (zero formatting errors).
   - `git status --short` confirms all working tree changes are pristine and preserved. No commits, pushes, or deployments occurred.

---

## 4. Final Verdict

**Verdict:** **`ROOT_CAUSE_CONFIRMED_AND_FIXED`**

The category mismatch between summary counters and card badges has been fixed, and all counts across Database, API, and Frontend are 100% reconciled and synchronized.
