# Multi-Horizon Signal Report
**Date:** 2026-09-13
**Total Signals Scanned:** 234

## Signal Distribution by Horizon
The system categorizes signals into three distinct time horizons to accommodate different trading strategies.

### 1. SHORT Horizon
- **Status:** Active
- **Performance:** AUC 0.45 - 0.65
- **Observation:** Characterized by mixed results. Highly sensitive to intra-day market noise.

### 2. SWING Horizon
- **Status:** Active
- **Performance:** AUC 0.60 - 0.85
- **Observation:** The most consistent performer in the current build. Suitable for 2-5 day positions.

### 3. LONG Horizon
- **Status:** Active (Filtered)
- **Performance:** AUC 0.85+
- **Observation:** Exceptional accuracy when signals are generated. However, signal frequency is lower due to strict data sufficiency requirements and class imbalance management.

## Current Signal Count Summary
- **Total Valid Signals:** 234
- **High Confidence Signals (SWING/LONG):** 65% of total volume.
- **Experimental Signals (SHORT):** 35% of total volume.
