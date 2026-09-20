# V2.3 Entry Timing Instrumentation

## 1. Instrumentation Gaps (Historical)
- Resolved Population: 49 signals.
- Usable Timing Data: 0.0%.

## 2. V2.3 Active Instrumentation
The following fields are now mandatory for every signal candidate:
- `candidate_timestamp`: Internal generation start.
- `published_at`: Atomic record creation time.
- `price_at_signal`: Price seen by the agent.
- `price_at_publish`: Price recorded in the ledger.

**Next Audit Step**: Calculate "Signal-to-Publish" latency and price slippage once N=50 forward signals accumulate.
