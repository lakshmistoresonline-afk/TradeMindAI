import datetime
import pandas as pd
from typing import Dict, Any, Optional, List
from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.services.pnl_service import PnlService

class OutcomeService:
    """
    Consolidated Outcome Engine.
    Handles terminal state evaluation for both Live and Replay.
    """

    TERMINAL_STATES = ["TARGET_HIT", "STOP_LOSS", "EXPIRED", "CANCELLED", "TIMEOUT"]

    @staticmethod
    def evaluate_signal_outcome(
        signal: LiveSignal,
        price_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Determines if a signal hit Target, Stop, or Expired.
        Price Data should be a DataFrame with [Open, High, Low, Close].
        """
        if price_data.empty:
            return {"status": signal.status, "outcome_verified": False}

        entry = signal.entry_price
        target = signal.target_price
        stop = signal.stop_price
        direction = signal.direction.upper()

        # 1. Horizon Check
        horizon_days = {"INTRADAY": 1, "SHORT_TERM": 7, "SWING": 30, "POSITIONAL": 365}
        max_days = horizon_days.get(signal.timeframe, 30)
        expiry_ts = signal.timestamp + datetime.timedelta(days=max_days)

        current_status = signal.status
        outcome_ts = None
        exit_price = None
        mfe = 0.0
        mae = 0.0

        # Sort data chronologically
        eval_data = price_data[price_data.index >= signal.timestamp].sort_index()

        for ts, row in eval_data.iterrows():
            high, low, open_p, close = row["High"], row["Low"], row["Open"], row["Close"]

            # Update MFE/MAE
            if direction == "LONG":
                mfe = max(mfe, ((high - entry) / entry) * 100)
                mae = min(mae, ((low - entry) / entry) * 100)
            else:
                mfe = max(mfe, ((entry - low) / entry) * 100)
                mae = min(mae, ((entry - high) / entry) * 100)

            # Check for Expiry
            if ts > expiry_ts:
                current_status = "EXPIRED"
                outcome_ts = ts.to_pydatetime()
                exit_price = open_p
                break

            # A. ENTRY MONITORING (If waiting)
            if current_status == "WAITING_FOR_ENTRY":
                triggered = False
                if direction == "LONG" and low <= entry: triggered = True
                elif direction == "SHORT" and high >= entry: triggered = True

                if triggered:
                    current_status = "ACTIVE" # Move straight to ACTIVE for outcome check
                    # We can use ENTRY_TRIGGERED as a sub-state or just transition to ACTIVE

            # B. OUTCOME MONITORING (Only if ACTIVE)
            if current_status == "ACTIVE":
                hit_target = False
                hit_stop = False

                if direction == "LONG":
                    if open_p <= stop: hit_stop, exit_price = True, open_p
                    elif open_p >= target: hit_target, exit_price = True, open_p
                    elif low <= stop: hit_stop, exit_price = True, stop
                    elif high >= target: hit_target, exit_price = True, target
                else: # SHORT
                    if open_p >= stop: hit_stop, exit_price = True, open_p
                    elif open_p <= target: hit_target, exit_price = True, open_p
                    elif high >= stop: hit_stop, exit_price = True, stop
                    elif low <= target: hit_target, exit_price = True, target

                if hit_stop:
                    current_status = "STOP_LOSS"
                    outcome_ts = ts.to_pydatetime()
                    break
                if hit_target:
                    current_status = "TARGET_HIT"
                    outcome_ts = ts.to_pydatetime()
                    break

        # 2. Finalize Results
        if current_status in ["TARGET_HIT", "STOP_LOSS", "EXPIRED"]:
            pnl_results = PnlService.calculate_trade_pnl(
                entry_price=entry,
                exit_price=exit_price,
                direction=direction,
                position_size=signal.capital_allocation or 100000.0
            )

            return {
                "status": current_status,
                "outcome_date": outcome_ts,
                "exit_price": float(exit_price),
                "gross_pnl": pnl_results["gross_pnl"],
                "net_pnl": pnl_results["net_pnl"],
                "realized_return": pnl_results["net_return_pct"],
                "mfe": float(mfe),
                "mae": float(mae),
                "outcome_verified": True,
                "exit_reason": f"{current_status}_REACHED"
            }

        return {
            "status": "ACTIVE",
            "mfe": float(mfe),
            "mae": float(mae),
            "outcome_verified": False
        }
