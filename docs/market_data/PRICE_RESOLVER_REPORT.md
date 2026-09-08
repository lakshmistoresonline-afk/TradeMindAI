# PRICE RESOLVER AUDIT REPORT

## 1. Hierarchy Configuration
The `PriceResolver` implements the following deterministic sequence:

### **EQUITY**
1. `NSEOpenProvider` (Primary)
2. `AngelOneProvider` (Authenticated)
3. `UpstoxProvider` (Authenticated)
4. `YFinanceProvider` (Fallback)

### **F&O**
1. `NSEOpenProvider` (Primary)
2. `AngelOneProvider` (Authenticated)
3. `DATA_UNAVAILABLE` (Hard Stop)

## 2. Findings
Verified that YFinance is never utilized for derivative pricing, ensuring that underlying spot prices do not contaminate premium fields.

---
**Status**: RESOLVER_CERTIFIED.
