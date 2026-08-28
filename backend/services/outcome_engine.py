from typing import List, Dict, Any, Optional
import datetime
import pandas as pd
import numpy as np
from backend.domain.models.ios import LiveSignal, SignalEvent

class OutcomeEngine:
    @staticmethod
    def evaluate_outcome(signal: LiveSignal, future_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generic Outcome Evaluation with High/Low support.
        Processes terminal states chronologically.
        """
        if future_data.empty:
            return {"status": "ACTIVE", "outcome_date": None, "outcome_price": None, "profit_pct": 0.0, "events": []}

        # 1. Setup Parameters
        entry_limit = signal.entry_price
        target = signal.target_price
        stop = signal.stop_loss_price
        direction = signal.direction # LONG or SHORT

        # Timezone Alignment
        import pytz
        sig_ts = signal.timestamp
        if sig_ts.tzinfo is None: sig_ts = pytz.UTC.localize(sig_ts)

        # Ensure future_data index is UTC and sorted
        import pytz
        if not isinstance(future_data.index, pd.DatetimeIndex):
            try:
                future_data.index = pd.to_datetime(future_data.index)
            except:
                return {"status": "ACTIVE", "outcome_date": None, "outcome_price": None, "profit_pct": 0.0, "events": []}

        if future_data.index.tzinfo is None:
            future_data.index = future_data.index.tz_localize(pytz.UTC)
        else:
            future_data.index = future_data.index.tz_convert(pytz.UTC)

        future_data = future_data.sort_index()

        # Slice data strictly since signal timestamp
        eval_data = future_data[future_data.index >= sig_ts]
        if eval_data.empty:
            return {"status": "ACTIVE", "outcome_date": None, "outcome_price": None, "profit_pct": 0.0, "events": []}

        # 2. State Machine (Assumes signal is already ACTIVE/Triggered for Shadow Audit)
        # For Shadow monitoring, we mostly care about signals already in progress.
        current_status = "ACTIVE"
        actual_entry_price = signal.entry_price

        outcome_ts = None
        exit_price = None
        profit_pct = 0.0
        mfe = 0.0
        mae = 0.0
        events = []

        # Horizons check (Time-based instead of Bar-based for robustness)
        # SWING: 30 days | INTRADAY: 1 day | SHORT_TERM: 7 days | POSITIONAL: 365 days
        horizon_days = {"INTRADAY": 1, "SHORT_TERM": 7, "SWING": 30, "POSITIONAL": 365}
        max_days = horizon_days.get(signal.timeframe, 30)
        expiry_ts = sig_ts + datetime.timedelta(days=max_days)

        for ts, row in eval_data.iterrows():
            high = row["High"]
            low = row["Low"]
            open_price = row["Open"]
            close = row["Close"]

            # Expiry Check
            if ts > expiry_ts:
                current_status = "EXPIRED"
                outcome_ts = ts.to_pydatetime()
                exit_price = open_price # Close at start of expiration window
                events.append(SignalEvent(type="EXPIRED", timestamp=outcome_ts, price=exit_price))
                break

            target_hit = False
            stop_hit = False

            # Evaluate chronologically within bar:
            # 1. Check Open (Gap)
            # 2. Check High/Low (Intrabar)

            if direction == "LONG":
                # Check for Gap through Stop/Target on OPEN
                if open_price <= stop:
                    stop_hit = True
                    exit_price = open_price
                elif open_price >= target:
                    target_hit = True
                    exit_price = open_price
                # Check Intrabar levels
                elif low <= stop:
                    stop_hit = True
                    exit_price = stop
                elif high >= target:
                    target_hit = True
                    exit_price = target
            else: # SHORT
                if open_price >= stop:
                    stop_hit = True
                    exit_price = open_price
                elif open_price <= target:
                    target_hit = True
                    exit_price = open_price
                elif high >= stop:
                    stop_hit = True
                    exit_price = stop
                elif low <= target:
                    target_hit = True
                    exit_price = target

            # Priority: STOP > TARGET (Conservative Rule)
            if stop_hit:
                current_status = "STOP_LOSS"
                outcome_ts = ts.to_pydatetime()
                events.append(SignalEvent(type="STOP_LOSS", timestamp=outcome_ts, price=exit_price))
                break

            if target_hit:
                current_status = "TARGET_HIT"
                outcome_ts = ts.to_pydatetime()
                events.append(SignalEvent(type="TARGET_HIT", timestamp=outcome_ts, price=exit_price))
                break

            # Update MFE/MAE
            if direction == "LONG":
                mfe = max(mfe, ((high - actual_entry_price) / actual_entry_price) * 100)
                mae = min(mae, ((low - actual_entry_price) / actual_entry_price) * 100)
            else:
                mfe = max(mfe, ((actual_entry_price - low) / actual_entry_price) * 100)
                mae = min(mae, ((actual_entry_price - high) / actual_entry_price) * 100)

        # 3. Finalize P&L if terminal
        if current_status != "ACTIVE":
            if direction == "LONG":
                profit_pct = ((exit_price - actual_entry_price) / actual_entry_price) * 100
            else:
                profit_pct = ((actual_entry_price - exit_price) / actual_entry_price) * 100

        return {
            "status": current_status,
            "outcome_date": outcome_ts,
            "outcome_price": float(exit_price) if exit_price else None,
            "profit_pct": float(profit_pct),
            "mfe": float(mfe),
            "mae": float(mae),
            "events": events
        }
