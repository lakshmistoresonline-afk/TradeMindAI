# TradeMind AI: Signal Lifecycle Forensic Audit (Institutional Build 4.5)

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
- **Open Signals (33)**: 30 ACTIVE + 3 WAITING_FOR_ENTRY.
- **Historical Population (50)**: 29 Target + 20 Stop + 1 Timeout.
- **Integrity**: Signal outcomes are immutable in the production ledger.

## 3. Trigger Logic Verification
- **LONG (Pullback)**: Triggered when `Low <= Entry`.
- **SHORT (Retracement)**: Triggered when `High >= Entry`.
- **Sync Status**: 100% of signals correctly synchronized with live price action.

---
**Verdict**: **PASS**
Lifecycle logic is causal, sound, and accurately reflects the frozen V2.2 methodology.
