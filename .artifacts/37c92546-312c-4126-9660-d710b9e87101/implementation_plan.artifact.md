# Migration from PostgreSQL to Firebase Firestore

This plan outlines the steps to replace the existing PostgreSQL/SQLAlchemy database layer with Firebase Firestore to avoid local database installations.

## Proposed Changes

### Configuration
#### [MODIFY] [.env](file:///D:/TradeMindAI/backend/.env)
- Remove `DATABASE_URL`.
- Ensure `FIREBASE_PROJECT_ID` is set to `com-webcraft-trademindai-c8f75`.
- (Optional) Add `GOOGLE_APPLICATION_CREDENTIALS` path if not using default auth.

### Core Database Layer
#### [MODIFY] [database.py](file:///D:/TradeMindAI/backend/core/database.py)
- Replace SQLAlchemy setup with `firebase_admin` and `firestore` initialization.
- Update `get_db` to return a Firestore client instance.

### Data Models
#### [MODIFY] [models.py](file:///D:/TradeMindAI/backend/data/models.py)
- Remove `Base` and SQLAlchemy column definitions.
- Implement Pydantic models for `Stock` and `StockPrice` to handle serialization/deserialization for Firestore.

### Data Collection
#### [MODIFY] [collector.py](file:///D:/TradeMindAI/backend/data/collector.py)
- Rewrite `fetch_stock_info` to use Firestore's `document().set()` and `document().get()`.
- Rewrite `fetch_historical_data` to store historical prices as sub-collections or individual documents in a `prices` collection.

### Background Tasks
#### [MODIFY] [tasks.py](file:///D:/TradeMindAI/backend/workers/tasks.py)
- Update `analyze_stock_task` to work with the Firestore client instead of SQLAlchemy `Session`.

## Verification Plan
- Run `analyze_file` on modified files to check for syntax and import errors.
- Manual verification of API endpoints (stocks, analysis) once the backend is running.
- Ensure `celery` worker can still connect to Redis (using Memurai or Cloud Redis).
