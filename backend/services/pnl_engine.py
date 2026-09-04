from typing import Dict, Any, Optional
import math

class PNLEngine:
    """
    Workstream 9: Canonical P&L Engine.
    One single path for all profit/loss calculations.
    """
    DEFAULT_FRICTION_PCT = 0.0020 # 0.20% Round-trip

    @staticmethod
    def calculate_pnl(
        entry_price: float,
        exit_price: float,
        direction: str,
        quantity: int = 1,
        friction_pct: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Standardized P&L calculation with friction.
        """
        if not entry_price or not exit_price or entry_price <= 0:
            return {"gross_pnl": 0.0, "net_pnl": 0.0, "pnl_pct": 0.0}

        # 1. Gross Calculation
        if direction == "LONG":
            gross_pct = ((exit_price - entry_price) / entry_price) * 100
        else:
            gross_pct = ((entry_price - exit_price) / entry_price) * 100

        # 2. Friction
        f_pct = friction_pct if friction_pct is not None else PNLEngine.DEFAULT_FRICTION_PCT
        net_pct = gross_pct - (f_pct * 100)

        # 3. Absolute P&L (if quantity > 1)
        gross_amt = (gross_pct / 100) * (entry_price * quantity)
        net_amt = (net_pct / 100) * (entry_price * quantity)

        return {
            "gross_pnl_pct": round(gross_pct, 4),
            "net_pnl_pct": round(net_pct, 4),
            "gross_pnl_amt": round(gross_amt, 2),
            "net_pnl_amt": round(net_amt, 2),
            "fees_pct": round(f_pct * 100, 4)
        }
