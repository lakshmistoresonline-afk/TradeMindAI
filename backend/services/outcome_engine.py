from typing import List, Dict, Any, Optional
import datetime
import pandas as pd
import numpy as np
from backend.domain.models.ios import LiveSignal, SignalEvent

class OutcomeEngine:
    @staticmethod
    def evaluate_outcome(signal: LiveSignal, future_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Canonical Outcome Evaluation for Equity, Futures, and Options.
        Matches signal targets/stops against future price action.
        """
        # Baseline result structure to prevent KeyError in callers
        result = {
            "status": "DATA_UNAVAILABLE",
            "outcome_date": None,
            "outcome_price": None,
            "profit_pct": 0.0,
            "mfe": 0.0,
            "mae": 0.0,
            "events": [],
            "trigger_price": None,
            "triggered_at": None
        }

        if future_data.empty:
            return result

        # 1. Setup Parameters
        entry = signal.entry_price
        target = signal.target_price
        stop = signal.stop_loss_price
        direction = signal.direction # LONG or SHORT
        asset_class = signal.asset_class or "EQUITY"

        # 2. Timeframe-based Expiry
        # Default horizons (bars)
        horizons = {
            "INTRADAY": 15,    # Bars (assuming 15m or 1H data)
            "SHORT_TERM": 50,
            "SWING": 200,
            "POSITIONAL": 1000
        }
        max_bars = horizons.get(signal.timeframe, 200)

        # Filter data starting from signal timestamp
        sig_ts = signal.timestamp
        # Ensure comparison is possible between timezone-aware and naive datetimes (RC-5 Alignment)
        import pytz
        if sig_ts.tzinfo is None:
            sig_ts = pytz.UTC.localize(sig_ts)

        if future_data.index.tz is None:
            future_data.index = future_data.index.tz_localize(pytz.UTC)
        else:
            future_data.index = future_data.index.tz_convert(pytz.UTC)

        future_data = future_data[future_data.index >= sig_ts].head(max_bars)
        if future_data.empty:
            return {"status": "DATA_UNAVAILABLE"}

        current_status = signal.status
        trigger_price = None
        trigger_ts = None
        outcome_ts = None
        exit_price = None
        profit_pct = 0.0
        mfe = 0.0
        mae = 0.0

        events = []

        for ts, row in future_data.iterrows():
            high = row["High"]
            low = row["Low"]
            close = row["Close"]

            # A. ENTRY MONITORING
            if current_status == "WAITING_FOR_ENTRY":
                is_triggered = False
                if direction == "LONG" and low <= entry <= high:
                    is_triggered = True
                    trigger_price = entry
                elif direction == "SHORT" and low <= entry <= high:
                    is_triggered = True
                    trigger_price = entry
                # Gap detection
                elif direction == "LONG" and low > entry:
                    # Gapped up above entry
                    is_triggered = True
                    trigger_price = low
                elif direction == "SHORT" and high < entry:
                    # Gapped down below entry
                    is_triggered = True
                    trigger_price = high

                if is_triggered:
                    current_status = "ACTIVE"
                    trigger_ts = ts.to_pydatetime()
                    events.append(SignalEvent(
                        type="ENTRY_TRIGGERED",
                        timestamp=trigger_ts,
                        price=trigger_price,
                        message=f"Price engaged at entry zone: {trigger_price:.2f}"
                    ))
                    # Continue to check same bar for outcome

            # B. OUTCOME MONITORING (Only if ACTIVE)
            if current_status == "ACTIVE":
                target_hit = False
                stop_hit = False

                if direction == "LONG":
                    if target and high >= target: target_hit = True
                    if stop and low <= stop: stop_hit = True
                else: # SHORT
                    if target and low <= target: target_hit = True
                    if stop and high >= stop: stop_hit = True

<<<<<<< HEAD
                # SAME-CANDLE AMBIGUITY (P0 Requirement: Deterministic Conservative Policy)
                if target_hit and stop_hit:
                    # Policy: Always assume STOP HIT first in same candle (Maximum Conservatism)
                    current_status = "STOP_LOSS"
                    outcome_ts = ts.to_pydatetime()
                    exit_price = stop
                    events.append(SignalEvent(
                        type="STOP_LOSS",
                        timestamp=outcome_ts,
                        price=stop,
                        message="Target and Stop hit in same candle. Assuming Stop Hit (Conservative Policy)."
=======
                # SAME-CANDLE AMBIGUITY
                if target_hit and stop_hit:
                    current_status = "AMBIGUOUS"
                    outcome_ts = ts.to_pydatetime()
                    exit_price = (target + stop) / 2
                    events.append(SignalEvent(
                        type="AMBIGUOUS",
                        timestamp=outcome_ts,
                        message="Both target and stop touched in same candle. Conflict unresolved."
>>>>>>> origin/main
                    ))
                    break

                if target_hit:
                    current_status = "TARGET_HIT"
                    outcome_ts = ts.to_pydatetime()
                    exit_price = target
                    events.append(SignalEvent(type="TARGET_HIT", timestamp=outcome_ts, price=target))
                    break

                if stop_hit:
                    current_status = "STOP_LOSS"
                    outcome_ts = ts.to_pydatetime()
                    exit_price = stop
                    events.append(SignalEvent(type="STOP_LOSS", timestamp=outcome_ts, price=stop))
                    break

                # Update Running MFE/MAE (only for active trades)
                if direction == "LONG":
                    curr_mfe = ((high - entry) / entry) * 100
                    curr_mae = ((low - entry) / entry) * 100
                else:
                    curr_mfe = ((entry - low) / entry) * 100
                    curr_mae = ((entry - high) / entry) * 100

                if curr_mfe > mfe: mfe = curr_mfe
                if curr_mae < mae: mae = curr_mae

        # C. EXPIRY / TIMEOUT CHECK
        if current_status in ["WAITING_FOR_ENTRY", "ACTIVE"]:
            if len(future_data) >= max_bars:
                current_status = "EXPIRED"
                outcome_ts = future_data.index[-1].to_pydatetime()
                exit_price = float(future_data["Close"].iloc[-1])
                events.append(SignalEvent(
                    type="EXPIRED",
                    timestamp=outcome_ts,
                    price=exit_price,
                    message="Signal reached maximum holding period without target/stop trigger."
                ))

        # 3. Finalize Stats
        if exit_price and entry:
            if direction == "LONG":
                profit_pct = ((exit_price - entry) / entry) * 100
            else:
                profit_pct = ((entry - exit_price) / entry) * 100

        return {
            "status": current_status,
            "outcome_date": outcome_ts,
            "outcome_price": float(exit_price) if exit_price else None,
            "profit_pct": float(profit_pct),
            "mfe": float(mfe),
            "mae": float(mae),
            "events": events,
            "trigger_price": float(trigger_price) if trigger_price else None,
            "triggered_at": trigger_ts
        }
