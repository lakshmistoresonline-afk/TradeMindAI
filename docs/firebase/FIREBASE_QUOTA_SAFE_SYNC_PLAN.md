# Firebase Quota-Safe Synchronization Plan

## 1. Context
TradeMind AI uses the Firestore Free Tier, which has a daily limit of **20,000 writes**. During intensive validation and sync cycles, this quota can be exhausted. This plan establishes a "Quota-Safe" architecture to ensure data integrity without service interruption.

## 2. Core Strategies

### A. Persistent Queue (`data/firebase/firebase_sync_queue.json`)
- All pending writes are stored in a local JSON queue.
- The sync engine processes this queue in small, prioritized batches.
- Progress is saved after every batch, allowing resumption after a 429 error or manual stop.

### B. Upsert Optimization (Check-Before-Write)
- The engine performs a `get()` before every `set()`.
- If the local data matches the remote document exactly, the write is skipped.
- This preserves write quota at the cost of read quota (which is 2.5x larger on the free tier).

### C. Data Tiering
- **Tier 1 (Vital)**: System status, stock metadata, performance summaries. Synchronized first.
- **Tier 2 (Historical)**: Equity curves, recent price history (last 5-100 bars). Synchronized as quota allows.
- **Tier 3 (Archived)**: Full 1M+ price history, research signals. Kept local only to avoid quota burn.

## 3. Quota Guard Rails
- **Batch Size**: Configurable (default 20-50).
- **Max Writes per Session**: Prevents a single run from consuming the entire daily budget.
- **429 Detection**: Immediate graceful exit upon receiving `RESOURCE_EXHAUSTED`.

**STATUS**: `ENABLED`
The system is now operating in Quota-Safe mode.
