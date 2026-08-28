# DATABASE MIGRATION GUIDE (RC-4)

## 📋 Strategy
The migration follows an **Online Shadow Write** pattern to ensure zero downtime.

### Phase 1: Preparation
1. Initialize the PostgreSQL schema:
   ```bash
   .\backend\venv\Scripts\python -c "from backend.core.postgres import init_db; init_db()"
   ```
2. Ensure local storage for Parquet files exists.

### Phase 2: Execution
1. Run the migration script to copy legacy data from Firestore to the Hybrid Tier:
   ```bash
   .\backend\venv\Scripts\python scripts/migrate_to_hybrid.py
   ```
2. Verify row counts between Firestore collections and Postgres tables.

### Phase 3: Switching
1. Update `Container.py` to use `HybridRepository` implementations.
2. Deploy the updated backend.
3. Monitor `system_logs` for any persistence errors.

## 🔄 Rollback Plan
If inconsistencies are detected:
1. Revert `Container.py` to use the original `FirestoreRepository` classes.
2. Deployment will automatically reconnect to the legacy NoSQL data.
3. No data is deleted from Firestore during migration.
