# TradeMind AI - Browser Access Guide

After running `docker-compose up --build`, use the following URLs to interact with the platform:

## 1. Professional Web Dashboard
- **URL**: [http://localhost:5173](http://localhost:5173)
- **Features**: Real-time NIFTY/BankNIFTY tracking, AI Consensus Feed, and Market Health metrics.

## 2. Interactive API Documentation (Swagger)
- **URL**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Features**: Test all REST APIs directly from the browser. You can trigger AI analysis, fetch stock technicals, and manage user sessions.

## 3. Database & System Health
- **API Health**: [http://localhost:8000/](http://localhost:8000/)
- **PostgreSQL**: Accessible internally via `db:5432` or via an external tool using `localhost:5432` (if port is exposed).
- **Redis**: Accessible via `localhost:6379`.

## 4. Development Notes
- The web frontend uses **Vite + React + Tailwind CSS**.
- The API is built with **FastAPI** and auto-generates documentation.
- All requests from the web frontend to `/api/*` are automatically proxied to the backend container.
