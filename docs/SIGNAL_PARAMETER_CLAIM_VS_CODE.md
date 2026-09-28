# TradeMind AI — Signal Parameter Claim vs. Code Reconciliation

---

## 1. Parameter Reconciliation Matrix

This matrix reconciles every parameter in TradeMindAI between documented claims and actual codebase implementations.

| Parameter Family | Claimed Parameter | Actual Code Property | Source / Formula | Classification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Risk Geometry** | ATR(14) Volatility Scaling | `atr_14_value` | 14-period EMA of True Range | `IMPLEMENTED` | Active |
| **Risk Geometry** | Target 1 (Conservative) | `target_price_1` | $\text{Entry} + 1.5 \times \text{ATR}$ | `IMPLEMENTED` | Active |
| **Risk Geometry** | Target 2 (Main Base) | `target_price_2` | $\text{Entry} + 2.8 \times \text{ATR}$ | `IMPLEMENTED` | Active |
| **Risk Geometry** | Target 3 (Extended) | `target_price_3` | $\text{Entry} + 4.2 \times \text{ATR}$ | `IMPLEMENTED` | Active |
| **Risk Geometry** | Invalidation Level (Stop) | `stop_loss_price` | $\text{Entry} - 2.0 \times \text{ATR}$ | `IMPLEMENTED` | Active |
| **Derivatives** | Put-Call Ratio ($PCR$) | `options_pcr_oi` | Put OI / Call OI | `IMPLEMENTED` | Active |
| **Derivatives** | Net Dealer Gamma ($GEX$) | `net_dealer_gex` | Options Gamma Exposure | `IMPLEMENTED` | Active |
| **Microstructure** | Order Book Imbalance | `order_book_imbalance` | Top 5 BBO Depth Ratio | `IMPLEMENTED` | Active |
| **Microstructure** | VPIN Flow Toxicity | `vpin_flow_toxicity` | Constant-Volume Bucket Toxicity | `IMPLEMENTED` | Active |
| **Machine Learning**| SHAP Feature Attribution | `shap_drivers` | Game-theoretic feature weights | `IMPLEMENTED` | Active |
| **Machine Learning**| Venn-Abers Calibration | `venn_abers_lower_prob` | Multiprobability lower bound | `IMPLEMENTED` | Active |
| **Regime** | Gaussian HMM State | `hmm_regime_state` | 3-State Hidden Markov Model | `IMPLEMENTED` | Active |
| **Macro** | FinBERT Filings Sentiment | `finbert_nlp_sentiment` | Transformer-based NLP score | `IMPLEMENTED` | Active |
| **Macro** | Johansen Cointegration | `intermarket_cointegration_score` | USD/INR & Brent Cointegration | `IMPLEMENTED` | Active |
| **AI Swarm** | Swarm Consensus Score | `agent_swarm_consensus_score` | 4-Agent Unanimity Ratio | `IMPLEMENTED` | Active |
| **Telemetry** | 3-Source Price Consensus | `feed_consensus_score` | Real-time price median consensus | `IMPLEMENTED` | Active |

---

## 2. Code Reconciliation Guarantee

- No feature is claimed as active unless explicitly calculated or represented in the canonical payload.
- Unavailable data is represented with explicit missingness semantics rather than fake values.
