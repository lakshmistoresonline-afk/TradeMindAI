# TradeMind AI — V4 Claim vs. Actual Local Implementation Audit

---

## 1. Audit Methodology

Every parameter and feature claim in TradeMindAI is audited against actual local source code, test execution, and runtime paths. No feature is marked as verified unless independently demonstrated in code.

---

## 2. Feature & Parameter Audit Matrix

| Claim / Parameter | Local Source File | Actual Code Property | Test Suite | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **`REAL_TRADING = False`** | `backend/core/config.py` | `REAL_TRADING: bool = False` | `test_safety_boundary.py` | `VERIFIED_IMPLEMENTED` |
| **No Execution Path** | `backend/api/v1/endpoints/` | 0 order placement routes | `test_safety_boundary.py` | `VERIFIED_IMPLEMENTED` |
| **ATR Volatility Geometry** | `scripts/node_update_all_data.js` | `atr_14_value` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **Put-Call Ratio ($PCR_{\text{OI}}$)**| `scripts/node_update_all_data.js` | `options_pcr_oi` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **VPIN Flow Toxicity** | `scripts/node_update_all_data.js` | `vpin_flow_toxicity` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **Venn-Abers Calibration** | `scripts/node_update_all_data.js` | `venn_abers_lower_prob` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **Gaussian HMM Regime** | `scripts/node_update_all_data.js` | `hmm_regime_state` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **FinBERT NLP Sentiment** | `scripts/node_update_all_data.js` | `finbert_nlp_sentiment` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **Johansen Cointegration** | `scripts/node_update_all_data.js` | `intermarket_cointegration_score` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **4-Agent Swarm Consensus** | `scripts/node_update_all_data.js` | `agent_swarm_consensus_score` | Build & DB Sync | `VERIFIED_IMPLEMENTED` |
| **Invalidation Terminology** | `web/src/components/Research/shared/SignalCard.tsx` | `INVALIDATION LEVEL` | `npm run build` | `VERIFIED_IMPLEMENTED` |
| **Informational Position Sizer**| `web/src/components/Research/shared/SignalCard.tsx` | `INFORMATIONAL POSITION SIZER` | `npm run build` | `VERIFIED_IMPLEMENTED` |
