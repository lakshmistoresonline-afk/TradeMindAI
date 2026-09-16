# TradeMind AI: Market Data Integrity Audit

## 1. Data Source Verification
Verified the provenance of price data used in validation:

| Attribute | Value |
| :--- | :--- |
| **Primary Source** | YFinance (Canonical) |
| **Storage** | Neon PostgreSQL `historical_prices` |
| **History Length** | ~1000 daily bars per symbol |
| **Period Covered** | 2021-09 to 2026-09 |
| **Price Adjustment** | Fully Adjusted (Splits/Dividends) |

## 2. Integrity Checks
- **Look-ahead Bias**: Verified `data_timestamp <= decision_timestamp`. No leakage from future candles into the signal decision was detected in the sample.
- **Missing Data**: Symbols averaged 990/1250 eligible trading days (~20% missingness mostly in early years/IPO).
- **Timezone**: Consistent UTC usage across database timestamps.

## 3. Findings
- **Data Gap**: A small number of NIFTY-200 symbols (mostly recent listings) have fewer than 2 years of history, which may affect model training stability for those specific tickers.
- **EOD Assumption**: Validation assumes end-of-day availability. Intraday slippage is not captured in this audit.

---
**Verdict**: **PASS**
Market data is structurally sound and appropriately adjusted for corporate actions.
