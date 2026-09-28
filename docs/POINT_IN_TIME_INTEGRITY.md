# TradeMind AI — Point-in-Time Data Integrity & Lookahead Prevention

---

## 1. Point-in-Time Invariant

Every feature used in TradeMindAI obeys the strict temporal invariant:

$$\text{Timestamp}(\text{Feature}_t) \le \text{Timestamp}(\text{Signal}_t) < \text{Timestamp}(\text{Outcome}_t)$$

No feature, price quote, options snapshot, fundamental metric, or news sentiment value timestamped *after* signal decision time $t$ is permitted to enter the feature matrix or training set.

---

## 2. Temporal Leakage Controls

To guarantee point-in-time safety across all models and backtests:
1. **No Centered Moving Averages**: All technical indicators use strictly lagging or backward-looking windows (e.g. `EMA(14)`, `SMA(200)`).
2. **Purged Cross-Validation**: Machine learning model validation uses Purged Group Time-Series Split, purging overlapping label intervals between train and test splits to prevent label leakage.
3. **Embargo Periods**: A 5-day embargo period is enforced after every test split before the next training fold begins.
4. **Historical Fundamental Alignment**: Fundamental metrics are aligned to official public release/filing timestamps rather than period-end dates.
