# ISSUE: NIFTY200_HISTORICAL_LIVE_SIGNAL_SYNC_DISCREPANCY

## 1. Description
A discrepancy exists between the number of live signals in the authoritative Neon (Postgres) database and the Firestore mirror.

- **Neon (Postgres) Count**: 1232
- **Firestore Count**: 1089
- **Delta**: 143 records

## 2. Impact
Non-critical for `LIVE_SHADOW` operation. The shadow signal tier is 100% reconciled (27/27). This discrepancy affects only historical live signal visibility in the dashboard.

## 3. Preliminary Investigation
The delta of 143 records likely represents historical signals generated before the Firestore mirroring service was fully hardened or signals that fall outside the current incremental sync window (typically 24h-7d).

## 4. Recommended Action
- Perform a one-time manual backfill of the 143 missing records from Neon to Firestore.
- Ensure the `ShadowSyncService` incremental window is sufficient to catch late-arriving outcomes for historical signals.

## 5. Status
**OPEN** (Monitoring only. Do not resolve until shadow accumulation milestone is reached).
