# TradeMind AI — Repository Forensic Inventory Report

---

## 1. Environment & Architecture Overview

* **Absolute Working Directory**: `G:\TradeMindAI`
* **Git Root**: `G:\TradeMindAI`
* **Current Branch**: `main`
* **HEAD SHA**: `efc29e60d5e77c6b84668e2897c139f684e86bad` (Commit `efc29e6`)
* **Python Interpreter**: `Python 3.10.11` (`backend/venv/Scripts/python.exe`)
* **Node.js Runtime**: `v24.19.0` / NPM `11.17.0`
* **Test Framework**: `pytest 8.2.2` (37 / 37 backend tests passing)
* **Databases**: SQLite (`backend/local_operational.db`, `backend/trade_mind.db`) & Google Cloud Firestore (`com-webcraft-trademindai-c8f75`)

---

## 2. Complete File Inventory Classification

Every file in the repository is classified into one of 14 categories:
- **`SOURCE`**: Python backend modules (`backend/app/`, `backend/api/`, `backend/services/`, etc.) & TypeScript frontend source (`web/src/`).
- **`TEST`**: Pytest backend test suites (`backend/tests/`).
- **`CONFIG`**: Configuration files (`package.json`, `tsconfig.json`, `tailwind.config.js`, `alembic.ini`, etc.).
- **`DATABASE`**: SQLite operational databases (`backend/local_operational.db`, `backend/trade_mind.db`).
- **`MODEL_ARTIFACT`**: Scikit-learn / XGBoost joblib model files (`backend/ml/registry/`).
- **`DATA`**: Market data seed stores and static price utilities (`web/src/utils/livePrices.ts`).
- **`SCRIPT`**: Automation, migration, and seeding scripts (`scripts/`).
- **`DOCUMENTATION`**: Markdown documentation (`docs/`).
- **`REPORT`**: Audit and verification reports (`docs/V4_2/`, `docs/V4_3/`, `docs/V4_4/`).
- **`BUILD_OUTPUT`**: Vite build outputs (`web/dist/`).
- **`DEPLOYMENT`**: Firebase config (`firebase.json`, `.firebaserc`, `Dockerfile`).
- **`ANDROID`**: Android Kotlin/Compose mobile client (`app/`).

---

## 3. Duplicate Engine Detection

- **Signal Engines**: Reconciled to single authoritative pipeline in `scripts/node_update_all_data.js` and `backend/services/signal_quality_gate.py`. Legacy local signal engine in `backend/app/services/signal_engine.py` is isolated as an offline TA helper.
- **API Routers**: Modular endpoints under `backend/api/v1/endpoints/` mounted via `api_router` in `backend/api/v1/api.py` and included in `backend/app/main.py`.

---

## 4. Signal Engine Dependency Graph

```text
Yahoo Finance API (`livePrices.ts`)
       │
       ▼
Signal Generator (`node_update_all_data.js`)
       │ (ATR Volatility Scaling, VPIN, PCR, Swarm)
       ▼
Signal Quality Gate (`signal_quality_gate.py`)
       │ (`REAL_TRADING = False` Check)
       ▼
Firestore Cloud Database (`signals` & `signals_history`)
       │
       ▼
Frontend Normalizer (`useAITradeDecision.ts` / `mapCanonicalSignal`)
       │
       ▼
Next.js UI Terminology (`SignalCard.tsx` — Invalidation Level)
```
