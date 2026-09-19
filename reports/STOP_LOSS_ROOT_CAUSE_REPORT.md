# Stop-Loss Root Cause Analysis Report

## 1. Executive Summary
This report analyzes the failure patterns of 20 STOP_LOSS signals from the TradeMind V2.2 Shadow Ledger population (N=49 resolved).

| Metric | Value |
| :--- | :--- |
| Total Resolved Signals | 49 |
| Total STOP_LOSS | 20 |
| STOP_LOSS Rate | 40.8% |
| TARGET_HIT Rate | 59.2% |

---

## 2. Failure Pattern Distribution

| Failure Category | Signals | % of Losses | Evidence |
| :--- | :--- | :--- | :--- |
| **EARLY_NOISE_STOP** | 9 | 45.0% | MAE < 1.2x Stop Distance. Price touched stop and often reversed. |
| **IMMEDIATE_FAILURE** | 5 | 25.0% | MFE < 0.2%. Directional prediction wrong from entry. |
| **NEAR_TARGET_REVERSAL**| 3 | 15.0% | MFE > 70% of Target distance. Signal was "correct" but hit stop later. |
| **LATE_REVERSAL** | 3 | 15.0% | Price moved favorably beyond stop distance but reversed without hitting target. |

---

## 3. Dominant Root Causes

### A. Stop-Loss Geometry (Tight Stops)
45% of losses are classified as **EARLY_NOISE_STOP**. The current SWING stop of **2.0 ATR** appears to be vulnerable to normal intraday volatility in certain sectors. 
- **Finding**: Win rate for stops in (2, 3]% distance was 70%, but dropped to 56% in (3, 5]% range. This suggests that simply widening stops might not help if the entry timing is poor.

### B. Lack of Partial Profit/Trailing logic
15% of losses reached >70% of their target before reversing into a full stop-loss. 
- **Finding**: These signals are "successful" directional predictions that failed to capture value due to rigid exit rules.

### C. Entry Timing Gap
Signals are often generated after significant moves.
- **Finding**: 25% of losses are immediate. These occur when the "breakout" is actually an exhaustion point.

---

## 4. Signal Score & Calibration
- **Calibration Error**: The model exhibits ~10-12% optimism in the 70-80% probability range (Actual WR 63%).
- **Score Inconsistency**: Conviction scores (60, 70] actually outperformed (70, 80] by nearly 10%.

---

## 5. Improvement Recommendations

### P0: Correctness Defects
- None found in infrastructure; current audit verified truth.

### P1: Evidence-Supported Improvements
- **Implement Trailing Stops**: Once MFE > 1.0 ATR, move stop to Entry + 0.1 ATR.
- **Regime-Adaptive ATR**: Increase SWING stop multiplier from 2.0 to 2.25 in "VOLATILE" regimes.
- **Exhaustion Filter**: Block signals if RSI > 75 (Long) or RSI < 25 (Short) at entry to prevent "Buying the Top".

### P2: Data-Driven Calibration
- Re-train Platt Scaling parameters once resolved population reaches N=100.

---
**Verdict**: **PARTIALLY VERIFIED**
The current signal engine is directionally accurate (>59% WR), but risk geometry is too rigid, leading to 60% of losses being "avoidable" (Noise or Late Reversals).
