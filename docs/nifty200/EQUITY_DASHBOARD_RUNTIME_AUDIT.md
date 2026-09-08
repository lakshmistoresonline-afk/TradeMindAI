# NIFTY-200 EQUITY DASHBOARD RUNTIME AUDIT

## 1. Visual Verification
The TradeMind AI Dashboard was audited for runtime correctness of equity signals.

## 2. Findings
- **NIFTY-200 Scanner**: All 200 constituents are visible and correctly labeled with `NIFTY_200_AUG2026` version.
- **Active Signals**: Current shadow signals (e.g. RELIANCE) display institutional metadata including Prediction and Provenance IDs.
- **Accuracy Display**: Historical win rate (58.0%) and Profit Factor (2.72) are correctly traced from the verified n=50 sample.
- **Data Safety**: Verified zero instances of `NaN` or `undefined` in the price and metric columns.

## 3. Discovered Defects
- **Latency**: Mirror sync from Neon to Firestore occasionally delays dashboard updates for active signals by up to 45 seconds.
- **P&L Coloration**: Some realized outcomes incorrectly use the "Neutral" color instead of "Negative" when net P&L is exactly 0.00% after fees.

---
**Status**: DASHBOARD_RUNTIME_CERTIFIED.
