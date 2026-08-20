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
        Implements limit-order gap semantics and strict state machine.
        """
        if future_data.empty:
            return {"status": "DATA_UNAVAILABLE"}

        # 1. Setup Parameters
        entry_limit = signal.entry_price
        target = signal.target_price
        stop = signal.stop_loss_price
        direction = signal.direction # LONG or SHORT

        # Default horizons (bars)
        horizons = {"INTRADAY": 15, "SHORT_TERM": 50, "SWING": 200, "POSITIONAL": 1000}
        max_bars = horizons.get(signal.timeframe, 200)

        # Timezone Alignment
        import pytz
        sig_ts = signal.timestamp
        if sig_ts.tzinfo is None: sig_ts = pytz.UTC.localize(sig_ts)
        if future_data.index.tz is None:
            future_data.index = future_data.index.tz_localize(pytz.UTC)
        else:
            future_data.index = future_data.index.tz_convert(pytz.UTC)

        future_data = future_data[future_data.index >= sig_ts].head(max_bars)
        if future_data.empty:
            return {"status": "DATA_UNAVAILABLE"}

        # State Variables
        current_status = "WAITING_FOR_ENTRY"
        actual_entry_price = None
        entry_ts = None
        entry_execution_type = None

        outcome_ts = None
        exit_price = None
        profit_pct = 0.0
        mfe = 0.0
        mae = 0.0
        events = []

        bars_to_entry = 0
        bars_in_position = 0
        bars_to_expiry = 0

        for ts, row in future_data.iterrows():
            high = row["High"]
            low = row["Low"]
            open_price = row["Open"]
            close = row["Close"]

            # A. ENTRY MONITORING
            if current_status == "WAITING_FOR_ENTRY":
                bars_to_entry += 1
                is_filled = False

                # 1. Favorable Gap Execution
                # LONG: Open < Entry_Limit | SHORT: Open > Entry_Limit
                potential_gap_fill = False
                if direction == "LONG" and open_price < entry_limit:
                    potential_gap_fill = True
                elif direction == "SHORT" and open_price > entry_limit:
                    potential_gap_fill = True

                if potential_gap_fill:
                    # RULE B: Invalid Fill Protection (Stop Breach before Fill)
                    is_invalid = False
                    if direction == "LONG" and open_price <= stop:
                        is_invalid = True
                    elif direction == "SHORT" and open_price >= stop:
                        is_invalid = True

                    if not is_invalid:
                        is_filled = True
                        actual_entry_price = open_price
                        entry_execution_type = "FAVORABLE_GAP"
                    else:
                        # Order invalidated because market gapped through stop
                        # We stay in WAITING_FOR_ENTRY (effectively cancelling the signal for this evaluation)
                        pass

                # 2. Intrabar Execution (Only if not already filled or invalidated by gap)
                if not is_filled and not potential_gap_fill:
                    if low <= entry_limit <= high:
                        # Check if stop was hit before entry intrabar (Maximum Conservatism)
                        # We assume if both entry and stop are hit in same bar, stop happens first if we weren't in.
                        if (direction == "LONG" and low <= stop) or (direction == "SHORT" and high >= stop):
                            # Stop breach happens in same bar as potential entry
                            pass
                        else:
                            is_filled = True
                            actual_entry_price = entry_limit
                            entry_execution_type = "NORMAL"

                if is_filled:
                    current_status = "ACTIVE"
                    entry_ts = ts.to_pydatetime()
                    events.append(SignalEvent(
                        type="ENTRY_TRIGGERED",
                        timestamp=entry_ts,
                        price=actual_entry_price,
                        message=f"Entry filled ({entry_execution_type}) at {actual_entry_price:.2f}"
                    ))
                    # Fall through to check outcome in same bar (Step 4 Requirement)

            # B. OUTCOME MONITORING
            if current_status == "ACTIVE":
                bars_in_position += 1
                target_hit = False
                stop_hit = False

                # Check for Gap through Stop/Target on OPEN (if entry happened on previous bar or this bar)
                # If we just entered on this bar's OPEN (FAVORABLE_GAP), we check High/Low for the same bar.
                # If we just entered on this bar's INTRABAR, we check High/Low.

                if direction == "LONG":
                    if open_price <= stop:
                        stop_hit = True
                        exit_price = open_price # Gap through stop
                    elif open_price >= target:
                        target_hit = True
                        exit_price = open_price # Gap through target
                    elif low <= stop:
                        stop_hit = True
                        exit_price = stop
                    elif high >= target:
                        target_hit = True
                        exit_price = target
                else: # SHORT
                    if open_price >= stop:
                        stop_hit = True
                        exit_price = open_price # Gap through stop
                    elif open_price <= target:
                        target_hit = True
                        exit_price = open_price # Gap through target
                    elif high >= stop:
                        stop_hit = True
                        exit_price = stop
                    elif low <= target:
                        target_hit = True
                        exit_price = target

                # Conservative same-candle priority: STOP > TARGET
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

                # MFE/MAE (relative to actual entry)
                if direction == "LONG":
                    curr_mfe = ((high - actual_entry_price) / actual_entry_price) * 100
                    curr_mae = ((low - actual_entry_price) / actual_entry_price) * 100
                else:
                    curr_mfe = ((actual_entry_price - low) / actual_entry_price) * 100
                    curr_mae = ((actual_entry_price - high) / actual_entry_price) * 100
                if curr_mfe > mfe: mfe = curr_mfe
                if curr_mae < mae: mae = curr_mae

        # C. EXPIRY
        if current_status == "ACTIVE" and len(future_data) >= max_bars:
            current_status = "EXPIRED"
            outcome_ts = future_data.index[-1].to_pydatetime()
            exit_price = float(future_data["Close"].iloc[-1])
            events.append(SignalEvent(type="EXPIRED", timestamp=outcome_ts, price=exit_price))

        # 3. Finalize
        bars_to_expiry = len(future_data)

        if entry_ts and exit_price and actual_entry_price:
            if direction == "LONG":
                profit_pct = ((exit_price - actual_entry_price) / actual_entry_price) * 100
            else:
                profit_pct = ((actual_entry_price - exit_price) / actual_entry_price) * 100
        else:
            profit_pct = 0.0

        return {
            "status": current_status,
            "outcome_date": outcome_ts,
            "outcome_price": float(exit_price) if exit_price else None,
            "actual_entry_price": actual_entry_price,
            "entry_execution_type": entry_execution_type,
            "profit_pct": float(profit_pct),
            "mfe": float(mfe),
            "mae": float(mae),
            "bars_to_entry": bars_to_entry,
            "bars_in_position": bars_in_position,
            "bars_to_expiry": bars_to_expiry,
            "events": events,
            "triggered_at": entry_ts
        }
