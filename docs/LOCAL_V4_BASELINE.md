# TradeMind AI — Local System V4 Baseline Report

---

## 1. Local Project Identification

* **Working Directory**: `G:\TradeMindAI`
* **Git Top-Level**: `G:\TradeMindAI`
* **Git Branch**: `main`
* **Git Commit HEAD**: `051a77657a974f2f41b67ea9250a252ce32bc84b`
* **Remote Repository**: `https://github.com/lakshmistoresonline-afk/TradeMindAI`
* **Working Tree Status**: 1 uncommitted local modification (`web/src/utils/livePrices.ts` preserved)

---

## 2. Environment & Runtime Stack

* **Operating System**: Windows 10/11 Enterprise (x64)
* **Python Interpreter**: `Python 3.10.11` (Installed at `C:\Users\ADMIN\AppData\Local\Programs\Python\Python310\python.exe`)
* **Virtual Environment**: `G:\TradeMindAI\backend\venv` (Verified linked & operational)
* **Pytest Runner**: `pytest 8.2.2` (Verified 3/3 safety boundary tests passing)
* **Node.js Runtime**: `v24.19.0`
* **NPM Package Manager**: `11.17.0`
* **Frontend Framework**: Next.js / React 18 / Vite 5 / TypeScript 5 / Material UI (MUI) 5
* **Backend Framework**: Python FastAPI 0.111 / Pydantic 2.7 / SQLAlchemy 2.0 / Alembic 1.13
* **Cloud Database**: Google Cloud Firestore (`com-webcraft-trademindai-c8f75`)
* **Local Database**: SQLite (`G:\TradeMindAI\backend\local_operational.db`)
* **Deployment Target**: Firebase Hosting (`https://com-webcraft-trademindai-c8f75.web.app`)

---

## 3. Local Uncommitted Changes Audit

* **`web/src/utils/livePrices.ts`**: Contains real-time Yahoo Finance price quotes fetched from live NSE market feeds (`LT`, `TCS`, `RELIANCE`, `INFY`, etc.). Preserved in workspace.
