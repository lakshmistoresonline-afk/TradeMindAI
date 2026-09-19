# Signal Improvement Recommendations

## 1. Adaptive Risk Geometry (P1)
**Finding**: 45% of losses were noise-related (EARLY_NOISE_STOP).
**Recommendation**: Implement a Regime-Aware ATR Multiplier.
- **Current**: SWING = 2.0 ATR.
- **Proposed**: 
  - BULLISH: 2.0 ATR (Keep)
  - SIDEWAYS: 1.8 ATR (Lower noise)
  - VOLATILE: 2.5 ATR (Increased buffer)

## 2. Dynamic Exit Strategy (P1)
**Finding**: 15% of losses reversed from near-target levels (NEAR_TARGET_REVERSAL).
**Recommendation**: Implement a "Break-Even Trigger".
- When price reaches **1.5 ATR Favorable Excursion** (75% of a standard SWING risk), move stop loss to **Entry Price + 0.1 ATR**.

## 3. Directional Gating (P2)
**Finding**: LONG signals in BULLISH regime have <50% win rate in current sample.
**Recommendation**: Add Sector Rotation filter.
- Only generate LONG signals if the symbol's sector **RS (Relative Strength)** is in the top 3 sectors of the NIFTY-200 universe.

## 4. Probability Calibration (P2)
**Finding**: Model is 10-12% over-confident in the 70-80% bracket.
**Recommendation**: Re-calibrate Platt Scaling parameters.
- Adjust the `A` and `B` parameters in the `CalibrationService` once N=100 resolved signals is reached.

---
**Status**: Recommendations Derived from Forensic Evidence.
**Next Action**: Implement P1 Shadow Gating for validation.
