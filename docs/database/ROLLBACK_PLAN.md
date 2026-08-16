# DATABASE ROLLBACK PLAN (RC-4)

## 🚨 Scenario: Data Corruption or API Failure
In the event of a catastrophic failure during the hybrid transition:

### 1. Identify
- Check `system_logs` for `POSTGRES_CONNECTION_ERROR`.
- Verify if dashboard widgets show `NaN` or `N/A`.

### 2. Isolate
- Immediately stop the background ETL scheduler to prevent further inconsistent writes.

### 3. Revert
1. **Repository Switch**: Update `backend/core/container.py`
   ```python
   # REVERTED
   from backend.infrastructure.repositories.firestore_repository import FirestoreStockRepository
   self._repository = FirestoreStockRepository(db_client)
   ```
2. **Redeploy**: Push the hotfix to production.

### 4. Verify
- Confirm terminal loads correctly using original Firestore sub-collections.
- Since Firestore was never deleted, the system will return to the T-0 state immediately.
