"""
================================================================================
TradeMindAI: Authoritative Forward Horizon Outcome Engine
================================================================================
Provides deterministic, point-in-time trade horizon evaluation for 5, 10, 20, 60
session prediction horizons with conservative same-bar stop-loss resolution
and explicit right-censored incomplete-window classification.
================================================================================
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

def evaluate_horizon_outcome(
    entry_price: float,
    target_price: float,
    stop_price: float,
    future_bars: pd.DataFrame,
    horizon: int
) -> Dict[str, Any]:
    """
    Evaluates forward trade outcome across `horizon` daily bars.

    Returns a dictionary with:
    - status: "TARGET_HIT" | "STOP_LOSS" | "EXPIRED" | "INCOMPLETE_WINDOW" | "ACTIVE"
    - exit_price: float
    - exit_date: Optional[str]
    - pnl_pct: float
    - is_full_horizon: bool
    """
    if future_bars is None or future_bars.empty:
        return {
            "status": "ACTIVE",
            "exit_price": entry_price,
            "exit_date": None,
            "pnl_pct": 0.0,
            "is_full_horizon": False
        }

    highs = future_bars["High"].values
    lows = future_bars["Low"].values

    # Default status: EXPIRED if full horizon reached, INCOMPLETE_WINDOW if right-censored before full horizon
    status = "EXPIRED" if len(future_bars) == horizon else "INCOMPLETE_WINDOW"
    exit_price = float(future_bars.iloc[-1]["Close"])
    exit_date = str(future_bars.iloc[-1]["date"]) if "date" in future_bars.columns else None

    for f_idx in range(len(future_bars)):
        bar_high = highs[f_idx]
        bar_low = lows[f_idx]
        bar_dt = str(future_bars.iloc[f_idx]["date"]) if "date" in future_bars.columns else None

        # Conservative Same-Bar Conflict Check: If both target and stop touched on same bar, classify as STOP_LOSS
        if bar_high >= target_price and bar_low <= stop_price:
            status = "STOP_LOSS"
            exit_price = stop_price
            exit_date = bar_dt
            break
        elif bar_high >= target_price:
            status = "TARGET_HIT"
            exit_price = target_price
            exit_date = bar_dt
            break
        elif bar_low <= stop_price:
            status = "STOP_LOSS"
            exit_price = stop_price
            exit_date = bar_dt
            break

    pnl_pct = round(((exit_price - entry_price) / entry_price) * 100.0, 2)

    return {
        "status": status,
        "exit_price": exit_price,
        "exit_date": exit_date,
        "pnl_pct": pnl_pct,
        "is_full_horizon": len(future_bars) == horizon
    }
