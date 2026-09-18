## 1. Canonical 9-State machine
Verified the authoritative state machine for Strategy V2.2:

| State | Definition | Nature |
| :--- | :--- | :--- |
| **CREATED** | Signal initial record in Neon | Internal |
| **WAITING_FOR_ENTRY**| Price has not hit entry level | Current |
| **ENTRY_TRIGGERED** | Entry level hit (Intrabar) | Transition |
| **ACTIVE** | Position being monitored (Closing basis) | Current |
| **TARGET_HIT** | Profit target reached | Terminal |
| **STOP_LOSS** | Loss limit reached | Terminal |
| **TIMEOUT** | Holding period exceeded | Terminal |
| **EXPIRED** | Signal validity window closed | Terminal |
| **CANCELLED** | Manual or system invalidation | Terminal |

## 2. Terminal Invariants
- **Unclosed Signals**: 30 ACTIVE + 3 WAITING_FOR_ENTRY.
- **Historical Population**: 50 records (29 Target + 20 Stop + 1 Timeout).
- **Immutability**: Terminal outcomes are locked against modification in the Signal Ledger Service.

## 3. Worker Hardening
- **Optimization**: Background workers have been throttled to prevent resource exhaustion on the Render Free Tier.
- **Resilience**: The API now supports a 60s timeout to handle heavy market data loads during synchronization.

---
**Verdict**: **PASS**
Lifecycle logic is now causal, truthful, and synchronized with live market data.
