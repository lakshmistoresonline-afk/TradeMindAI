# TRADEMIND AI: CANONICAL DATA DICTIONARY (V2.2)

## 1. Core Signal Fields
- **Entry Price**: The price at which the signal was triggered or activated.
- **Current Price**: The latest authoritative price from the Neon database.
- **Target Price**: The primary exit objective for a win.
- **Stop Loss Price**: The hard exit threshold for a loss.
- **Net P&L**: Profit or loss after 0.20% round-trip friction.

## 2. Evidence Levels
- **LEVEL 0**: RAW data, no validation.
- **LEVEL 1**: STRUCTURALLY VALID (Correct geometry, valid symbol).
- **LEVEL 2**: TEMPORALLY VALID (Time-stamped, no future data).
- **LEVEL 3**: MARKET VERIFIED (Confirmed hit against daily data).
- **LEVEL 4**: EXECUTION VERIFIED (Forensic 1m OHLC verification).
- **LEVEL 5**: PORTFOLIO VERIFIED (MTM impact confirmed).

## 3. Populations
- **LIVE_SHADOW**: Real-time signals monitored by the production engine.
- **LEGACY_LOG**: Signals recorded during early development (V2.0-V2.1).
- **SYNTHETIC**: Derived records for structural testing or pattern matching.
