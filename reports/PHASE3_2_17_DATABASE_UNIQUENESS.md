# Phase 3.2.17 Database Uniqueness Report

**Date**: 2026-11-03  
**Target File**: [backend/core/postgres.py](file:///D:/TradeMindAI/backend/core/postgres.py)  
**Status**: **100% IMPLEMENTED & VERIFIED**

## Database-Level Uniqueness Constraint Implementation

- **Partial Unique Index**:
  ```python
  Index(
      'idx_unique_active_signal', 'symbol',
      unique=True,
      sqlite_where=(Column('status') == 'ACTIVE'),
      postgresql_where=(Column('status') == 'ACTIVE')
  )
  ```
- **Scope**: Enforces global active BUY signal uniqueness across all timeframes/strategies at the database level for both SQLite (test) and PostgreSQL/Neon (production).
- **IntegrityError Race Recovery**: Atomic rollback on `IntegrityError` in `create_signal()` recovers existing active record cleanly.
