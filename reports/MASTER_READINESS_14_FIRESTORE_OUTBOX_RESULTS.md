# TradeMindAI — Master Readiness 14: Firestore Outbox Results Report

## 1. Firestore Outbox & Secondary Mirror Architecture

- **Post-Commit Mirroring**: For caller-owned sessions, secondary Firestore mirroring is deferred (`mirror_status: "DEFERRED_UNTIL_CALLER_COMMIT"`) and executed post-commit via `mirror_signal_after_commit()`.
- **Rollback Protection**: Transaction rollbacks clear Postgres DB entries and leave 0 orphan Firestore documents.
