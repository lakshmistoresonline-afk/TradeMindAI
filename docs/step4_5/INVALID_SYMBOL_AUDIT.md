# Invalid Symbol Audit - Step 4.5.2

The following symbols in the NIFTY 200 universe failed to produce valid diagnostics or features during the Step 4.5.1 Shadow Run.

| Symbol | Failure Reason | Local Price Count | Note |
| :--- | :--- | :--- | :--- |
| **GUJGASLTD** | `INSUFFICIENT_DATA` | 23 bars | Symbol recently added to DB; requires 100+ bars for feature stores. |
| **LTIM** | `DATA_UNAVAILABLE` | 0 bars | Missing historical price data in `historical_prices` table. |
| **PEL** | `FEATURE_GEN_ERROR` | 197 bars | Data exists but `get_features_by_range` returned empty (possible range mismatch). |
| **TATAMOTORS** | `FEATURE_GEN_ERROR` | 193 bars | Data exists but failed gate in diagnostic orchestrator. |

## Remediation Strategy
- **LTIM**: Manual data backfill required using `yfinance`.
- **GUJGASLTD**: Automatic accumulation will resolve this over time.
- **PEL / TATAMOTORS**: Investigate `backend/services/feature_store.py` for potential date-alignment edge cases.

**STATUS**: `WARNING`
196/200 symbols are fully operational.
