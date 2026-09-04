# TRADEMIND AI: INTELLIGENCE API REPORT

## 1. Overview
The Intelligence API (RC-7C) provides high-fidelity, multi-dimensional context for the NIFTY 200 universe. It exposes the output of the newly implemented Advanced Intelligence Engines.

## 2. Active Endpoints

| Endpoint | Method | Purpose | Source |
| :--- | :--- | :--- | :--- |
| `/shadow/intelligence/market` | GET | Current Market Regime & Institutional Bias | `RegimeDB` + `InstitutionalMetricDB` |
| `/shadow/intelligence/sectors` | GET | Real-time Sector Rotation & Rankings | `SectorMetricDB` |
| `/shadow/intelligence/stock/{sym}`| GET | Structured Stock Profile & Trend Score | `StockIntelligenceDB` |
| `/shadow/signals/{id}/explanation` | GET | Forensic AI Synthesis (Why this signal?) | `IntelligenceSynthesisDB` |

## 3. Data Flow
1. **Background Job**: Intelligence engines compute snapshots (Regime, Sectors, Stocks) and persist them to Neon.
2. **Signal Trigger**: `SignalEngine` snapshots current context into `IntelligenceSynthesisDB`.
3. **Frontend**: React components poll or retrieve on-demand context for deep visualization.

## 4. Integrity Standards
- **Zero Fabrication**: All API returns are mapped to actual database records or `UNAVAILABLE`.
- **Temporal Isolation**: API respects the `data_timestamp` of signals, ensuring no look-ahead in explanations.
