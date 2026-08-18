# SBIN Signal Lifecycle Audit

## 1. Summary
- **Total SBIN Evaluations:** 4
- **Total SBIN Signals:** 1 (Transactional)
- **Status:** **RECONCILED**

## 2. Signal Details
| ID | Created Timestamp | Status | Strategy | Model |
| :--- | :--- | :--- | :--- | :--- |
| sig_SBIN_202608180715 | 2026-08-18 07:15:56 | ACTIVE | v2.2 | 202608180606 |

## 3. Lifecycle Events (EVALUATION)
The following events triggered a "TRADE_SIGNAL" decision in the evaluation engine:
- **Event 161:** 2026-08-18 07:54:25
- **Event 361:** 2026-08-18 07:55:53
- **Event 561:** 2026-08-18 09:02:13
- **Event 761:** 2026-08-18 09:03:30

## 4. Reconciliation Conclusion
Only **one** active signal exists because the `ShadowService` correctly implements an **Idempotency Gate**. 

> [!NOTE]
> The system checks for existing `ACTIVE` signals for the same symbol before creating a new record in `shadow_signals`. This prevents duplicate exposure to the same trade idea across multiple evaluation cycles.

No historical signals have been lost or deleted. The discrepancy between "Total Trade Signals" (Evaluations) and "Active Signals" (Transactional) is a reporting taxonomy artifact, not a data integrity failure.
