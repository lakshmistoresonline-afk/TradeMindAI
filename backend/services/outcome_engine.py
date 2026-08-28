from typing import List, Dict, Any, Optional
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
        stop = signal.stop_loss_price
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
        if status == "TARGET_HIT":
            if signal.direction == "LONG" and exit_price < signal.target_price: return False
            if signal.direction == "SHORT" and exit_price > signal.target_price: return False
        elif status == "STOP_LOSS":
            if signal.direction == "LONG" and exit_price > signal.stop_loss_price: return False
            if signal.direction == "SHORT" and exit_price < signal.stop_loss_price: return False

        # 3. Instrument Validation
        if not signal.instrument_id: return False

        return True

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

            # Expiry Check (Part 15)
            if ts > expiry_ts:
                current_status = "EXPIRED"
                outcome_ts = ts.to_pydatetime()
                exit_price = open_price # Close at start of expiration window
                events.append(SignalEvent(type="EXPIRED", timestamp=outcome_ts, price=exit_price, message="Signal horizon timeout reached."))
                break

            target_hit = False
            stop_hit = False

            # Evaluate chronologically (Part 10, 11, 12)
            if direction == "LONG":
                # Priority 1: Gap down through stop on Open
                if open_price <= stop:
                    stop_hit = True
                    exit_price = open_price
                # Priority 2: Gap up through target on Open
                elif open_price >= target:
                    target_hit = True
                    exit_price = open_price
                # Priority 3: Intrabar touch
                else:
                    # Part 12: Same-candle rule. If both hit, STOP_LOSS wins.
                    if low <= stop:
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
                else:
                    if high >= stop:
                        stop_hit = True
                        exit_price = stop
                    elif low <= target:
                        target_hit = True
                        exit_price = target

            if stop_hit:
                current_status = "STOP_LOSS"
                outcome_ts = ts.to_pydatetime()
                events.append(SignalEvent(type="STOP_LOSS", timestamp=outcome_ts, price=exit_price, message="Stop loss triggered intrabar."))
                break

            if target_hit:
                current_status = "TARGET_HIT"
                outcome_ts = ts.to_pydatetime()
                events.append(SignalEvent(type="TARGET_HIT", timestamp=outcome_ts, price=exit_price, message="Target achievement verified intrabar."))
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
