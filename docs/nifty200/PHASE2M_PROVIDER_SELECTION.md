# PHASE 2M: PROVIDER SELECTION REPORT

## 1. Primary Selection: Upstox API
**Classification**: Production Live Data Provider
**Selection Logic**:
- **Autonomy**: High. Analytics Token (1-year) allows for 100% automated shadow monitoring without daily OAuth redirects.
- **F&O Native Intelligence**: Built-in Greeks and OI Change APIs eliminate the need for complex internal calculation engines, reducing systemic risk.
- **Scalability**: Sub-50ms latency using Protobuf-based V3 feeds.

## 2. Secondary Selection: DhanHQ
**Classification**: Forensic Forensic/Audit Data Provider
**Selection Logic**:
- **Lineage Integrity**: The Rolling Options API enables verification of expired derivative contracts, a requirement for TradeMind's "Zero fabrication" mandate for historical auditing.
- **Failover**: Serves as the primary backup for live LTP if the Upstox feed experiences a provider-level outage.

## 3. Discontinued: YFinance
**Reasoning**: Systemic inability to provide reliable, real-time NSE F&O premiums. Continued usage for derivatives poses a "fabricated price" risk to institutional certification.

---
**Implementation Order**:
1. Implement `UpstoxProvider` adapter for live LTP.
2. Implement `DhanProvider` adapter for historical F&O verification.
3. Update `PriceResolver` to utilize the new institutional hierarchy.
