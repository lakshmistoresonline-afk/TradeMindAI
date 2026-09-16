# TradeMind AI: Repository Forensic Audit (Quant Validation 1.0)

## Executive Summary
This document provides a comprehensive audit of the quantitative components within the TradeMind AI platform, following the product freeze of Strategy V2.2. The audit covers signal generation, risk management, outcome resolution, P&L calculation, and advanced validation services.

## 1. Core Quantitative Components

### 1.1 Signal Engine (`backend/services/signal_engine.py`)
- **Version**: Strategy V2.2 (Frozen)
- **Primary Function**: Master Signal Generation Node.
- **Key Logic**:
    - **Time-Awareness**: Fully implemented for historical replay and live shadow monitoring.
    - **No-Trade Engine**: Implements strict gates for rejection:
        - Drawdown (Max 15%)
        - Data Freshness (Max 120h)
        - Liquidity (Min 10M Avg Volume)
        - Trend Alignment (EMA 200)
        - Momentum (SMA 20 vs ATR)
        - Probability (Calibrated > 0.52)
        - Expected Value (EV > 0)
    - **Provenance**: Generates unique `provenance_id` and hashes for decision traceability.

### 1.2 Risk Engine (`backend/services/risk_engine.py`)
- **Primary Function**: Calculates trade parameters (Stop Loss, Target, Position Sizing).
- **Key Logic**:
    - **ATR-Based Geometry**: Stop Multipliers (Short: 1.5x, Swing: 2.0x, Long: 3.0x).
    - **Risk/Reward**: Target Ratios (Short: 2.0, Swing: 2.5, Long: 3.0).
    - **Position Sizing**: Fixed Fractional (2% risk per trade, max 10% notional exposure).

### 1.3 Outcome Engine (`backend/services/outcome_engine.py`)
- **Primary Function**: Lifecycle management and terminal outcome verification.
- **Key Logic**:
    - **Immutability**: Terminal states (`TARGET_HIT`, `STOP_LOSS`, `EXPIRED`) are irreversible and immutable once verified.
    - **Chronological Evaluation**: High/Low/Open prices processed in sequence; Gaps handled; `STOP_LOSS` priority in same-candle collisions.
    - **Horizon Enforcement**: INTRADAY (1d), SHORT_TERM (7d), SWING (30d), POSITIONAL (365d).

### 1.4 P&L Engine (`backend/services/pnl_engine.py`)
- **Primary Function**: Standardized profit/loss calculation.
- **Key Logic**:
    - **Friction Model**: Default 0.20% round-trip friction (brokerage, STT, slippage).
    - **Calculation**: Supports both percentage-based and absolute currency P&L.

### 1.5 Research Metrics Service (`backend/services/research_metrics_service.py`)
- **Primary Function**: Aggregate performance statistics.
- **Key Metrics**: Win Rate, Profit Factor, Expectancy, Net P&L, Brier Score.
- **Segmentation**: Capable of slicing performance by Sector, Regime, and Direction.

## 2. Validation & Quality Services

### 2.1 Quantitative Validation Service (`backend/services/quant_validation_service.py`)
- **Features**:
    - **Probability Metrics**: Brier Score, Log Loss, ROC-AUC.
    - **Reliability Curve**: Predicted vs. Actual probability calibration.
    - **EV Correlation**: Pearson and Spearman rank correlation between Predicted EV and Realized P&L.
    - **Sensitivity Analysis**: Outlier impact assessment.
    - **Drift Detection**: Kolmogorov-Smirnov test for distribution shifts.

### 2.2 Walk-Forward Service (`backend/services/walk_forward_service.py`)
- **Mechanism**: Chronological train/test window splitting without random shuffling to prevent look-ahead bias.

### 2.3 Freeze Verification Service (`backend/services/freeze_verification_service.py`)
- **Mechanism**: SHA256 integrity checks against `docs/V22_FREEZE_MANIFEST.json`.

## 3. Authoritative Data Layer

### 3.1 PostgreSQL Schema (`backend/core/postgres.py`)
- **Tables**:
    - `live_signals`: Authoritative ledger for live/shadow signals.
    - `shadow_signals`: Authoritative ledger for historical/replay signals.
    - `predictions`: Model inference history.
    - `shadow_provenance`: Forensic lineage data.
- **Guards**: `before_insert` hooks to prevent TEST data leakage into PRODUCTION/SHADOW environments.

## 4. Reconciliation Layer
- **Scripts**: `scripts/debug/reconcile_active_vs_history.py`, `scripts/debug/reconcile_signal_ids.py`.
- **Function**: Ensures consistency between active caches, historical logs, and database records.

---
**Audit Date**: 2026-09-16
**Auditor**: TradeMind AI Quant Validator
**Status**: COMPLETE
