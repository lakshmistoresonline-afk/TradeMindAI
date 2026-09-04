# TRADEMIND AI: CANONICAL SIGNAL LEDGER V2 SCHEMA

## 1. SIGNAL IDENTITY
- `signal_id`: Globally unique immutable identifier.
- `symbol`: Ticker symbol.
- `asset_type`: EQUITY or DERIVATIVE.
- `exchange`: Default "NSE".
- `direction`: LONG or SHORT.
- `strategy_version`: Default "v2.2".
- `model_version`: Associated Random Forest or legacy model.

## 2. DECISION & PRICING
- `probability`: Raw ML sigmoid output.
- `calibrated_probability`: Platt-scaled win probability.
- `expected_value`: Risk-adjusted expectancy.
- `entry`: Signal entry price.
- `target`: Signal target price.
- `stop_loss`: Signal stop loss price.
- `current_price`: Real-time market price (Authority: Neon).

## 3. TIMING & LIFECYCLE
- `created_at`: Physical record creation time.
- `signal_timestamp`: Logical generation time.
- `entry_timestamp`: Time of trigger.
- `exit_timestamp`: Time of terminal event.
- `lifecycle_state`: CREATED -> ENTERED -> TERMINAL.
- `verification_level`: 0 (Unverified) to 4 (Live Shadow Verified).

## 4. TRACEABILITY
- `prediction_id`: UUID link to the inference event.
- `provenance_id`: UUID link to the data snapshot.
- `feature_snapshot_id`: ID of the exact feature vector used.

## 5. PERFORMANCE
- `net_pnl`: P&L after 0.20% friction.
- `mae`: Max Adverse Excursion.
- `mfe`: Max Favorable Excursion.
- `holding_period`: Duration from entry to exit.
