# INSTRUMENT IDENTITY & TOKEN MAPPING REPORT

## 1. Mapping Strategy
Deterministic identity is established using the following fields:
- **EQUITY**: Symbol + ISIN.
- **F&O**: Underlying + Expiry + Strike + OptionType.

## 2. Token Authority
While some providers use numeric tokens, the **Open Market Data Fabric** uses the official NSE trading symbols and contract identifiers as the primary keys for resolution. This ensures compatibility across multiple public sources.

---
**Status**: RESOLVED.
