# PHASE 6: DATABASE CONFIGURATION (PROD-READY)

## 1. Environment Classification
TradeMind AI now strictly distinguishes between development and production environments to prevent data cross-contamination and ensure PC independence.

| Environment | Database | Logic Gate |
| :--- | :--- | :--- |
| **Development** | Local SQLite | `ENVIRONMENT=development` |
| **Production** | Hosted PostgreSQL (Neon) | `ENVIRONMENT=production` |
| **Testing** | Local SQLite (Temp) | `ENVIRONMENT=test` |

## 2. Configuration Precedence
The system resolves the database connection string using the following priority:

1. **POSTGRES_URL** (Environment Variable): Authoritative production string.
2. **DATABASE_URL** (Environment Variable): Fallback/Compatibility.
3. **Local SQLite File**: Default for development ONLY.

## 3. Production Safety (Fail-Closed)
To prevent accidental dependency on the local PC, the `ShadowService` implements a mandatory check:
- If `ENVIRONMENT == "production"` and the driver is `sqlite`, the engine will **FAIL CLOSED** with a `PRODUCTION_SHADOW_SQLITE_FORBIDDEN` error.

## 4. Authoritative Source of Truth
The **Hosted PostgreSQL** instance is the single authoritative source for:
- `shadow_signals`: Signal lifecycle and resolved outcomes.
- `shadow_events`: Immutable evaluation audit trail.
- `model_registry`: Champion model metadata.

## 5. PC Independence
Once deployed to Railway, the Shadow engine reads/writes exclusively to PostgreSQL. Shutting down the local PC will have **zero impact** on signal generation or outcome resolution.
