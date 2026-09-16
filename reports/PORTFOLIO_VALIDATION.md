# TradeMind AI: Portfolio Validation Report

## 1. Simulation Baseline
Verified the theoretical performance of a fixed-fractional portfolio using Strategy V2.2 signals:

| Parameter | Value | Status |
| :--- | :--- | :--- |
| **Baseline Capital** | ₹1,000,000 | **VERIFIED** |
| **Risk per Trade** | 2.0% (₹20,000) | **VERIFIED** |
| **Allocation Model** | ATR-Based Position Sizing | **VERIFIED** |
| **Max Concurrent Pos** | No Limit (Audit Discovery) | **RISK_DETECTED** |

## 2. Portfolio-Level Performance
- **Cumulative Net Return**: +126.9% (Theoretical)
- **Max Portfolio Drawdown**: -19.3%
- **Exposure Peak**: 150% (Leveraged on 2026-08-24 due to clustering)
- **Signal Independence**: Low (Correlation > 0.70 during clusters)

## 3. Findings
- **Leverage Risk**: Without a cap on concurrent positions, the portfolio simulation utilized >100% of capital during high-crowding sessions (e.g., Aug 24). This overstates potential real-world returns.
- **Diversification**: Performance is currently symbol-agnostic but sector-concentrated due to missing sector gates.

## 4. Recommendation
- Implement a `max_concurrent_positions = 5` gate in `RiskEngine`.
- Implement a `max_sector_exposure = 20%` gate.

---
**Verdict**: **PASS WITH LIMITATIONS**
Theoretical portfolio performance is exceptionally high but relies on unconstrained capital allocation during clustered sessions.
