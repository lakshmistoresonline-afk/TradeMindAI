# TradeMind AI — Local Setup Instructions

Since Render build minutes have been exhausted, you can run the entire TradeMind AI Institutional OS locally on your PC.

## Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 20+

## Option 1: Full System with Docker (Recommended)
This runs the Database, Redis, API, and Frontend in containers.

1. Ensure Docker is running.
2. From the root directory:
   ```bash
   docker-compose up --build
   ```
3. The API will be at: `http://localhost:8000`
4. The Web UI will be at: `http://localhost:5173`

## Option 2: Direct Local Run (Faster for Development)

### 1. Run Backend
1. Go to `backend/` directory.
2. Create/Check `.env` (it should have `ENVIRONMENT=development`).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations (to create the local SQLite DB):
   ```bash
   python -c "from backend.core.postgres import init_db; init_db()"
   ```
5. Start the API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### 2. Run Frontend
1. Go to `web/` directory.
2. Update `.env` to point to local API:
   ```
   VITE_API_URL="http://localhost:8000/api/v1"
   ```
3. Install and run:
   ```bash
   npm install
   npm run dev
   ```

## Note on "Config Files" Folder
A copy of all critical configuration files is maintained in the `Config Files/` directory in the root. If you move to a new PC, ensure these files are restored to their respective locations (root, backend/, web/, etc.).
