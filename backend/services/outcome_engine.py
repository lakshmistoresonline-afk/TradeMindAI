from typing import List, Dict, Any, Optional, Tuple
import datetime
import pandas as pd
import numpy as np
from backend.domain.models.ios import LiveSignal, SignalEvent

class OutcomeEngine:
    @staticmethod
    def evaluate_live_lifecycle(signal: LiveSignal) -> Dict[str, Any]:
        """
        Step 4 Hardened Live Lifecycle Safety.
        Implements:
        - Part 7/8/15: Expiry & Lifecycle Events
        - Part 9/24: Irreversible terminal states
        - Part 17: Outcome verification
        - Part 20: Immutable terminal outcomes
        - Part 23: Immutability for verified outcomes
        """
        # Part 23: Verified outcomes are immutable
        if signal.outcome_verified:
            return {
                "status": signal.status,
                "progress": None,
                "pnl": signal.net_pnl,
                "msg": "LIFECYCLE_IMMUTABLE_VERIFIED"
            }

        # Hard Invariant: Terminal states are irreversible (Part 24)
        TERMINAL_STATES = ["TARGET_HIT", "STOP_LOSS", "EXPIRED", "CANCELLED", "TIMEOUT"]
        if signal.status in TERMINAL_STATES:
            return {
                "status": signal.status,
                "progress": None,
                "pnl": signal.net_pnl,
                "msg": "LIFECYCLE_STAY_TERMINAL"
            }

        # Part 7/8/9/14/15: Instrument Expiry Rule
        if signal.price_status == "EXPIRED" or signal.signal_eligibility == "EXPIRED_INSTRUMENT":
            return {
                "status": "EXPIRED",
                "progress": None,
                "pnl": None,
                "msg": "LIFECYCLE_TRANSITION_EXPIRED",
                "outcome_verified": True # Expiry is a deterministic system state
            }

        # Part 12: Lifecycle Safety - NULL semantics
        if signal.current_price is None or signal.price_status in ["DATA_UNAVAILABLE", "PROVIDER_UNSUPPORTED", "INSTRUMENT_NOT_FOUND", "INVALID"]:
            return {
                "status": signal.status,
                "progress": None,
                "pnl": None,
                "msg": "LIFECYCLE_BLOCKED_DATA_UNAVAILABLE"
            }

        # Part 13 & 14: P&L and Progress Safety
        entry = signal.entry_price
        target = signal.target_price
        stop = signal.stop_price
        current = signal.current_price
        direction = signal.direction

        if not entry or not target or not stop:
            return {"status": signal.status, "progress": None, "pnl": None}

        # Calculate Progress % (Part 14)
        progress = 0.0
        try:
            if direction == "LONG":
                if current >= entry:
                    # Positive progress towards target
                    denom = (target - entry)
                    progress = ((current - entry) / denom * 100) if denom != 0 else 0.0
                else:
                    # Negative progress towards stop
                    denom = (entry - stop)
                    progress = ((current - entry) / denom * 100) if denom != 0 else 0.0
            else: # SHORT
                if current <= entry:
                    denom = (entry - target)
                    progress = ((entry - current) / denom * 100) if denom != 0 else 0.0
                else:
                    denom = (stop - entry)
                    progress = ((entry - current) / denom * 100) if denom != 0 else 0.0
        except ZeroDivisionError:
            progress = 0.0

        # terminal check
        new_status = signal.status
        exit_price = current
        outcome_verified = False

        if direction == "LONG":
            if current >= target:
                new_status = "TARGET_HIT"
                exit_price = target
            elif current <= stop:
                new_status = "STOP_LOSS"
                exit_price = stop
        else:
            if current <= target:
                new_status = "TARGET_HIT"
                exit_price = target
            elif current >= stop:
                new_status = "STOP_LOSS"
                exit_price = stop

        # Part 23: Cost Model for terminal hits
        fees = 0.0
        slippage = 0.0
        net_pnl = round(progress, 2)

        if new_status in ["TARGET_HIT", "STOP_LOSS"]:
            fees = 0.10
            slippage = 0.10
            net_pnl = round(progress - 0.20, 2)
            # Part 17: Verify the outcome
            outcome_verified = OutcomeEngine.verify_terminal_outcome(signal, new_status, exit_price)

        return {
            "status": new_status,
            "progress": round(progress, 2),
            "pnl": round(progress, 2), # Gross %
            "fees": fees,
            "slippage": slippage,
            "net_pnl": net_pnl,
            "exit_price": float(exit_price),
            "outcome_verified": outcome_verified,
            "msg": "LIFECYCLE_EVALUATED"
        }

    @staticmethod
    def verify_terminal_outcome(signal: LiveSignal, status: str, exit_price: float) -> bool:
        """
        Part 17 & 35: Forensic Outcome Verification.
        """
        if not signal or not exit_price: return False

        # 1. Price Validation
        if exit_price <= 0: return False

        # 2. Target/Stop Validation
        if status in ["TARGET_HIT"]:
            if signal.direction == "LONG" and exit_price < signal.target_price: return False
            if signal.direction == "SHORT" and exit_price > signal.target_price: return False
        elif status in ["STOP_LOSS", "BREAKEVEN_HIT", "TRAILING_STOP_HIT"]:
            # Flexible validation for dynamic stops
            if signal.direction == "LONG" and exit_price > signal.target_price: return False
            if signal.direction == "SHORT" and exit_price < signal.target_price: return False

        # 3. Instrument Validation
        if not signal.instrument_id: return False

        return True

    @staticmethod
    def calculate_dynamic_stop_loss(
        entry: float,
        current_stop: float,
        direction: str,
        high: float,
        low: float,
        atr: float
    ) -> Tuple[float, Optional[str]]:
        """
        Calculates dynamic stop loss updates based on MFE (Maximum Favorable Excursion):
        1. Move to Break-Even (Entry + 0.1 ATR) when price reaches >= 1.5 ATR MFE.
        2. Trail Stop Loss at 1.5 ATR behind peak when price reaches >= 2.0 ATR MFE.
        """
        if not entry or not current_stop or not atr or atr <= 0:
            return current_stop, None

        mfe_abs = (high - entry) if direction == "LONG" else (entry - low)
        mfe_atr = mfe_abs / atr

        updated_stop = current_stop
        event_type = None

        # 1. Break-Even Trigger (at >= 1.5 ATR MFE)
        if mfe_atr >= 1.5:
            be_stop = (entry + 0.1 * atr) if direction == "LONG" else (entry - 0.1 * atr)
            if direction == "LONG" and be_stop > updated_stop:
                updated_stop = be_stop
                event_type = "MOVED_TO_BREAKEVEN"
            elif direction == "SHORT" and be_stop < updated_stop:
                updated_stop = be_stop
                event_type = "MOVED_TO_BREAKEVEN"

        # 2. Trailing Stop Trigger (at >= 2.0 ATR MFE)
        if mfe_atr >= 2.0:
            trail_stop = (high - 1.5 * atr) if direction == "LONG" else (low + 1.5 * atr)
            if direction == "LONG" and trail_stop > updated_stop:
                updated_stop = trail_stop
                event_type = "TRAILING_STOP_UPDATED"
            elif direction == "SHORT" and trail_stop < updated_stop:
                updated_stop = trail_stop
                event_type = "TRAILING_STOP_UPDATED"

        return round(updated_stop, 2), event_type

    @staticmethod
    def evaluate_outcome(signal: LiveSignal, future_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generic Outcome Evaluation with High/Low & Dynamic Exit Support.
        Processes terminal states chronologically with Break-Even & Trailing Stop Loss triggers.
        """
        if future_data.empty:
            return {"status": "ACTIVE", "outcome_date": None, "outcome_price": None, "profit_pct": 0.0, "events": []}

        # 1. Setup Parameters
        entry_limit = signal.entry_price
        target = signal.target_price
        stop = signal.stop_price
        direction = signal.direction # LONG or SHORT

        # Estimate ATR if not available directly
        atr_est = abs(entry_limit - stop) / 2.0 if (entry_limit and stop and entry_limit != stop) else (entry_limit * 0.015)

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
        current_status = "ACTIVE"
        actual_entry_price = signal.entry_price

        outcome_ts = None
        exit_price = None
        profit_pct = 0.0
        mfe = 0.0
        mae = 0.0
        events = []

        # Horizons check
        horizon_days = {"INTRADAY": 1, "SHORT_TERM": 7, "SWING": 30, "POSITIONAL": 365}
        max_days = horizon_days.get(signal.timeframe, 30)
        expiry_ts = sig_ts + datetime.timedelta(days=max_days)

        active_stop = stop

        for ts, row in eval_data.iterrows():
            high = row["High"]
            low = row["Low"]
            open_price = row["Open"]
            close = row["Close"]

            # Update MFE/MAE first
            if direction == "LONG":
                mfe = max(mfe, ((high - actual_entry_price) / actual_entry_price) * 100)
                mae = min(mae, ((low - actual_entry_price) / actual_entry_price) * 100)
            else:
                mfe = max(mfe, ((actual_entry_price - low) / actual_entry_price) * 100)
                mae = min(mae, ((actual_entry_price - high) / actual_entry_price) * 100)

            # Evaluate Dynamic Exit Adjustment
            new_stop, stop_event = OutcomeEngine.calculate_dynamic_stop_loss(
                actual_entry_price, active_stop, direction, high, low, atr_est
            )
            if stop_event and new_stop != active_stop:
                active_stop = new_stop
                events.append(SignalEvent(type=stop_event, timestamp=ts.to_pydatetime(), price=active_stop, message=f"Dynamic stop updated to ₹{active_stop} ({stop_event})"))

            # Expiry Check
            if ts > expiry_ts:
                current_status = "EXPIRED"
                outcome_ts = ts.to_pydatetime()
                exit_price = open_price
                events.append(SignalEvent(type="EXPIRED", timestamp=outcome_ts, price=exit_price, message="Signal horizon timeout reached."))
                break

            target_hit = False
            stop_hit = False

            # Evaluate chronologically with active dynamic stop
            if direction == "LONG":
                if open_price <= active_stop:
                    stop_hit = True
                    exit_price = open_price
                elif open_price >= target:
                    target_hit = True
                    exit_price = open_price
                else:
                    if low <= active_stop:
                        stop_hit = True
                        exit_price = active_stop
                    elif high >= target:
                        target_hit = True
                        exit_price = target
            else: # SHORT
                if open_price >= active_stop:
                    stop_hit = True
                    exit_price = open_price
                elif open_price <= target:
                    target_hit = True
                    exit_price = open_price
                else:
                    if high >= active_stop:
                        stop_hit = True
                        exit_price = active_stop
                    elif low <= target:
                        target_hit = True
                        exit_price = target

            if stop_hit:
                # Classify stop loss type
                if active_stop > stop if direction == "LONG" else active_stop < stop:
                    current_status = "TRAILING_STOP_HIT" if mfe >= 2.0 else "BREAKEVEN_HIT"
                else:
                    current_status = "STOP_LOSS"

                outcome_ts = ts.to_pydatetime()
                events.append(SignalEvent(type=current_status, timestamp=outcome_ts, price=exit_price, message=f"Exit triggered intrabar at ₹{exit_price} ({current_status})."))
                break

            if target_hit:
                current_status = "TARGET_HIT"
                outcome_ts = ts.to_pydatetime()
                events.append(SignalEvent(type="TARGET_HIT", timestamp=outcome_ts, price=exit_price, message="Target achievement verified intrabar."))
                break

        # 3. Finalize P&L if terminal
        if current_status != "ACTIVE":
            if direction == "LONG":
                profit_pct = ((exit_price - actual_entry_price) / actual_entry_price) * 100
            else:
                profit_pct = ((actual_entry_price - exit_price) / actual_entry_price) * 100

            # Part 23: Cost Model Implementation (RC-5/Step 3)
            # Standard NSE Equity Friction: ~0.20% (Brokerage + STT + Slippage)
            friction_pct = 0.20
            fees_pct = 0.10
            slippage_pct = 0.10
            net_profit_pct = profit_pct - friction_pct

            # Part 17: Forensic Outcome Verification
            outcome_verified = OutcomeEngine.verify_terminal_outcome(signal, current_status, exit_price)

            # Phase 6: Time Analysis
            duration_delta = (outcome_ts - sig_ts).total_seconds()

            return {
                "status": current_status,
                "outcome_date": outcome_ts,
                "outcome_price": float(exit_price) if exit_price else None,
                "profit_pct": float(profit_pct),
                "fees": float(fees_pct),
                "slippage": float(slippage_pct),
                "net_profit_pct": float(net_profit_pct),
                "mfe": float(mfe),
                "mae": float(mae),
                "outcome_verified": outcome_verified,
                "duration_seconds": duration_delta,
                "time_to_outcome_label": f"TIME_TO_{current_status}",
                "events": events
            }

        return {
            "status": current_status,
            "outcome_date": outcome_ts,
            "outcome_price": float(exit_price) if exit_price else None,
            "profit_pct": float(profit_pct),
            "mfe": float(mfe),
            "mae": float(mae),
            "events": events
        }
