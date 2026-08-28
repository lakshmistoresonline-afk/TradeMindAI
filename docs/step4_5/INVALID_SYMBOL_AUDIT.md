# Invalid Symbol Audit - Step 4.5.4

The following symbols in the NIFTY 200 universe are currently unavailable for signal generation.

| Symbol | Status | Failure Reason | Local Price Count | Note |
| :--- | :--- | :--- | :--- | :--- |
| **GUJGASLTD** | `DATA_UNAVAILABLE` | `INSUFFICIENT_DATA` | 26 bars | Requires 100+ bars for stable indicator calculation. |
| **LTIM** | `DATA_UNAVAILABLE` | `NOT_FOUND_ON_YAHOO` | 0 bars | Ticker mapping verified as LTIM.NS but Yahoo Finance returns no history for current period. |

## Forensic Analysis
- **GUJGASLTD**: Standard Yahoo API returns very limited depth for this specific symbol (post-2026/07). Data accumulation is pending.
- **LTIM**: LTIMindtree (merged) data depth issues on Yahoo Finance.

## Safety Guard
These symbols are automatically rejected by the `SignalEngine` and `ShadowEngine` with the reason `INVALID_DATA`.

**STATUS**: `MONITORING_DATA_ACCUMULATION`
198/200 symbols are fully operational.
