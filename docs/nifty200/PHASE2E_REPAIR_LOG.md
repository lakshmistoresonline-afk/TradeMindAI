# TRADEMIND AI: PHASE 2E REPAIR LOG

## 1. Price Contamination Fix
- **Defect**: Equity spot prices were leaking into derivative current price fields for F&O signals.
- **Root Cause**: `ShadowService` was incorrectly mapping prices from `StockDB` using symbol alone, ignoring `asset_class`.
- **Fix**: Re-implemented `update_active_signal_prices` to use the `PriceResolver`, which enforces strict instrument-level separation.
- **Affected Records**: `master_fut_RELIANCE_122636`, `master_opt_SBIN_860_122636`, etc.

## 2. Model/Ledger Parity Fix
- **Defect**: `PriceResolver` failing for shadow signals due to missing `price_adjustment_factor` attribute.
- **Fix**: Upgraded Neon schema to include `price_adjustment_factor` in `shadow_signals` table and updated domain mapping.

## 3. Linkage Recovery
- **Defect**: Missing `prediction_id` for active signals.
- **Rectification**: All pre-ledger signals explicitly marked `UNAVAILABLE_PRE_LEDGER_2.0` to eliminate FALSE-PASS ambiguity.

## 4. Risk/Reward Normalization
- **Defect**: `risk_amount_abs` and `reward_amount_abs` were NULL for active signals.
- **Fix**: Recomputed from entry/target/stop for all 1,259 signals in the authoritative ledger.

---
**Strategy V2.2 was NOT modified.**
