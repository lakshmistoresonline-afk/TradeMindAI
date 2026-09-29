# TradeMind AI — Advanced Feature Forensics (Step 19 & 48)

---

## 1. Advanced Feature Forensics & Audit Table

| Feature Name | Real Algorithm | Real Data Source | Production Consumer | Test Coverage | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VPIN Flow Toxicity** | Constant Volume Bucket Toxicity | Order Flow Tape | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Venn-Abers Bounds** | Inductive Conformal $[p_L, p_U]$ | ML Model Outputs | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Gaussian HMM** | 3-State Hidden Markov Model | NIFTY Returns | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **FinBERT NLP** | Transformer Sentiment Score | Corporate Filings | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Johansen Cointegration**| Vector Error Correction Model | USD/INR & Brent | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Random Matrix Theory** | Marčenko-Pastur Threshold | Return Covariance | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Tsallis Entropy** | Non-extensive $S_q$ ($q=1.5$) | Price Time Series | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **4-Agent Swarm** | Unanimity Ratio ($4/4$ Approved) | Multi-Agent Swarm | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Net Dealer GEX** | Dealer Gamma Exposure ($-GEX$) | Options Chain | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Options PCR** | Put OI / Call OI Ratio ($1.15$) | Options Chain | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Order Book OIB** | Top-5 BBO Depth Ratio | Level-2 Order Book | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
| **Intraday CVD** | Cumulative Delta Pressure | Aggressor Volume | `SignalDetail.tsx` | `test_production_contract.py` | `VERIFIED_BY_CODE_INSPECTION` |
