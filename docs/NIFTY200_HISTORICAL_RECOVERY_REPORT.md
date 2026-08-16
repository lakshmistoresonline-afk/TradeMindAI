# NIFTY 200 Historical Recovery Report

## 1. Initial State
At the start of this recovery phase, TradeMind AI had successful historical sync for 194/200 NIFTY 200 constituents. 6 symbols were failing due to provider mismatches or recent corporate actions in the August 2026 timeline.

## 2. Stocks Recovered
Through forensic symbol auditing and brute-force provider searching, 5 of the 6 failing symbols were successfully recovered using legitimate ticker mappings.

| Canonical Symbol | Provider Symbol | Status | Reason / Transition |
| :--- | :--- | :--- | :--- |
| **ZOMATO** | `ETERNAL.NS` | RECOVERED | Renamed to Eternal Limited (Aug 2026) |
| **PEL** | `PIRAMALFIN.NS` | RECOVERED | Re-indexed as Piramal Finance (Aug 2026) |
| **TATAMOTORS**| `TMCV.NS` | RECOVERED | Demerged; TMCV is the commercial entity |
| **GMRINFRA** | `GMRAIRPORT.NS`| RECOVERED | Renamed to GMR Airports (Aug 2026) |
| **L&TFH** | `LTF.NS` | RECOVERED | Renamed to L&T Finance Ltd (Aug 2026) |

## 3. Remaining Unavailable Stocks
- **LTIM**: Genuinely unavailable on the approved provider's endpoint for the August 2026 timeline. No legitimate ticker mapping or ISIN search yielded history.

## 4. Probability Calibration (Platt Scaling)
- **Implemented**: A chronological 60/20/20 split was enforced for all training runs.
- **Verification**: Out-of-sample Brier score was calculated and stored in the model registry.
- **Inference**: Signal engine now uses `calibrated_probability` as the primary confidence metric.

## 5. ML Eligibility
| Metric | Result |
| :--- | :--- |
| Eligible Symbols | 199 |
| Excluded Symbols | 1 (LTIM) |
| Valid Short Histories | 3 (GUJGASLTD, TATAMOTORS, PEL) |

## 6. Final Gate Status
**STATUS: CONDITIONALLY CLEARED**

The NIFTY 200 historical dataset is now 99.5% complete (199/200). The single missing symbol (LTIM) is structually unavailable from the primary data source and will be excluded from Step 2 processing to maintain quantitative integrity.

> [!TIP]
> **Step 2: Market Intelligence** is now allowed to proceed for the 199 verified symbols.
