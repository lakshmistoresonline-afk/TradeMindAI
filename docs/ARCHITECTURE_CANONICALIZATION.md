# TradeMind AI — Canonical Architecture Map

---

## 1. Canonical System Architecture

1. **Database Systems**: SQLite (`backend/trade_mind.db` for market data and signals; `backend/local_operational.db` for operational metadata).
2. **Repository Systems**: `HybridStockRepository`, `DataPlatformRepository`.
3. **Universe Systems**: `Nifty200UniverseService` querying `security_master`.
4. **Signal Engines**: `EquitySignalGenerationService`, `MLService`.
5. **Model Registries**: `backend/ml/registry/` (`.joblib` ExtraTrees/Voting classifiers with `model_registry` table).
6. **Calibration Systems**: `CalibrationService` (Isotonic regression / Platt scaling).
7. **Feature Engines**: `TechnicalAnalysis` (`backend/analysis/technical.py`) and `FeatureCalculationService`.
8. **API Routers**: FastAPI routers under `backend/api/v1/endpoints/` (`equity.py`, `health.py`, `stocks.py`, etc.).
9. **Frontend API Client**: Axios client (`web/src/api/client.ts`).
10. **Signal Ledger & Persistence**: Cloud Firestore mirror & SQLite live signals table.

---

## 2. Canonical Production Pipeline

```
REAL MARKET DATA (Yahoo Finance / yfinance)
   ↓
SECURITY MASTER (`security_master`)
   ↓
NIFTY-200 UNIVERSE (`Nifty200UniverseService`)
   ↓
MARKET DATA INGESTION (`RealMarketDataIngestionService`)
   ↓
TECHNICAL FEATURE ENGINE (`FeatureCalculationService` / `TechnicalAnalysis`)
   ↓
MODEL SELECTION (`ModelRegistryService`)
   ↓
MODEL INFERENCE (`MLService.predict_with_champion`)
   ↓
CALIBRATION (`CalibrationService`)
   ↓
SIGNAL QUALITY GATE (`SignalQualityGate`)
   ↓
RISK GEOMETRY (`RiskEngine`)
   ↓
CROSS-SECTIONAL RANKING
   ↓
SIGNAL LEDGER (`live_signals` / `signals_history`)
   ↓
FASTAPI (`backend/api/v1/endpoints/equity.py`)
   ↓
FRONTEND DASHBOARD (`web/src/pages/EquitySignals.tsx`)
```
