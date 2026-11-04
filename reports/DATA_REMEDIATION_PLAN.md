# Data Remediation Plan

**Date**: 2026-11-03  
**Strategy**: Non-Destructive, Evidence-Based Data Quality Remediation

## Failure Categories & Action Plan

1. **Unlisted Instrument (`BAGMANE`)**:
   - *Status*: Unlisted on Yahoo Finance provider API (`BAGMANE.NS`).
   - *Action*: Documented as `UNSUPPORTED`. Preserved in `reports/phase1_audit/BAGMANE_TRANSITION_RECONCILIATION.json`. No synthetic data fabrication.

2. **Intraday 5m Quote Limitations (`ICICIPRULI`, `BIRET`, `EMBASSY`)**:
   - *Status*: Provider returns `KeyError('tradingPeriods')` or unlisted 5m quote structure.
   - *Action*: Documented as `UNSUPPORTED` for intraday quotes. No synthetic candle fabrication.

3. **IPO Listing Boundaries (Post-2015 Listed Stocks)**:
   - *Status*: Stocks listed after 2015 (e.g. `LICI`, `PAYTM`, `NYKAA`, `SWIGGY`, `HYUNDAI`, `BAJAJHFL`) have valid earliest dates corresponding to their IPO listing dates.
   - *Action*: Map listing boundaries in `POST_2015_LISTING_DATES` to eliminate false missing session flags.

4. **Global Data Quality Gate**:
   - *Status*: Strictly enforces `signal_generation_allowed = False` while any symbol remains degraded.
