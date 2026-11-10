# TradeMindAI — Phase 5.36 Datetime Warning Audit Report

## 1. Datetime Warning Audit

- **Pydantic / SQLAlchemy Deprecation Warnings**: Third-party library deprecation warnings (`datetime.datetime.utcnow()`) are tracked. Application code uses `datetime.datetime.now(timezone.utc)`.
