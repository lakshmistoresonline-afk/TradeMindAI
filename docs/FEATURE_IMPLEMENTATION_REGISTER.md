# TradeMind AI — Feature Implementation Register

---

## 1. Feature Implementation Matrix

| Feature | Source Data | Algorithm / Formula | Implementation File | Production Consumer | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ATR(14) Volatility** | Yahoo Finance OHLCV | $\text{EMA}_{14}(\text{TrueRange})$ | `node_update_all_data.js` | `SignalCard.tsx` | `VERIFIED_BY_EXECUTION` |
| **VPIN Flow Toxicity** | Constant Vol Buckets | $\frac{\sum \|V_B - V_S\|}{N \times V}$ | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **Venn-Abers Bounds** | Conformal Predictors | Inductive Conformal $[p_L, p_U]$ | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **Gaussian HMM** | Return Distributions | 3-State Hidden Markov | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **FinBERT Sentiment** | Corporate Filings | Transformer Sentiment $\ge +0.65$ | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **Johansen Cointegrated**| USD/INR & Brent Crude | Vector Error Correction Model | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **RMT Noise Filter** | Correlation Matrix | Marčenko-Pastur Eigenvalue $\lambda_+$ | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **Tsallis Entropy** | Price Time Series | Non-extensive $S_q \le 0.20$ ($q=1.5$) | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **4-Agent Swarm** | Swarm Consensus | Unanimity Ratio ($4/4$ Approved) | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **Net Dealer GEX** | Options Chain Gamma | Dealer Gamma Exposure ($-GEX$) | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
| **Order Book OIB** | Top-5 BBO Depth | $\frac{\text{Bids} - \text{Asks}}{\text{Bids} + \text{Asks}} \ge +0.35$ | `node_update_all_data.js` | `SignalDetail.tsx` | `VERIFIED_BY_EXECUTION` |
