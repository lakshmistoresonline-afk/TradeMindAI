# TradeMind AI - Execution Guide

This guide provides step-by-step instructions to get the TradeMind AI platform up and running.

## Prerequisites

- **Python 3.10+**: For the backend service.
- **Docker & Docker Compose**: For containerized deployment (Database, Redis, Workers).
- **Android Studio (Ladybug or newer)**: For Android app development.
- **Ollama**: For running local LLMs (Llama 3).
- **PostgreSQL**: (Optional if not using Docker).

---

## 1. Backend Setup (Local Development)

If you want to run the backend without Docker for development:

1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    ```bash
    cp .env.example .env
    # Edit .env with your database and API keys
    ```

5.  **Run the FastAPI server**:
    ```bash
    uvicorn app.main:app --reload
    ```

---

## 2. Docker Deployment (Recommended)

To spin up the entire backend stack (API, DB, Redis, Celery Worker):

1.  **Run Docker Compose**:
    ```bash
    docker-compose up --build
    ```

---

## 3. AI Model Setup (Ollama)

The platform uses local LLMs for agentic analysis.

1.  **Install Ollama** from [ollama.com](https://ollama.com).
2.  **Pull the Llama 3 model**:
    ```bash
    ollama pull llama3
    ```
3.  Ensure Ollama is running at `http://localhost:11434` (default).

---

## 4. Android App Setup

1.  **Open the project** in Android Studio.
2.  **Sync Gradle**: Ensure all dependencies (Hilt, Retrofit, Compose) are downloaded.
3.  **Local API Access**: 
    - The app is configured to connect to `http://10.0.2.2:8000` (Android Emulator's alias for host localhost).
    - If running on a physical device, update `baseUrl` in `NetworkModule.kt` to your machine's local IP.
4.  **Build and Run**: Select your device/emulator and click "Run".

---

## 5. Web App Setup (Future/Manual)

*Note: The web project was initialized but requires Node.js/NPM on your host machine.*

1.  **Navigate to web directory**: `cd web`
2.  **Install dependencies**: `npm install`
3.  **Run development server**: `npm run dev`

---

## Troubleshooting

- **Database Connection**: Ensure the `DATABASE_URL` in `.env` matches your Docker or local Postgres credentials.
- **Hilt Errors**: If you encounter Hilt compilation errors, run `Build > Clean Project` followed by `Rebuild Project`.
- **Market Data**: The app uses `yfinance` which relies on public Yahoo Finance APIs; ensure you have an active internet connection.
