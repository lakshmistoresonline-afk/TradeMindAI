# TradeMind AI — Signal Architecture V3

---

## 1. Pipeline Overview

The Signal Architecture V3 enforces end-to-end reproducibility, point-in-time safety, and zero real trading execution paths.

```text
Live Price Ingestion (NSE)
  ↓
Feature Engineering (8 Families)
  ↓
HMM Regime & Breadth Classification
  ↓
Selective Meta-Labeling ML Ensemble
  ↓
Signal Quality Gate Audit
  ↓
Firestore Publication & Signal Detail View
```
