from typing import Dict, Any, Optional

class PnlService:
    """
    Authoritative P&L Service.
    ONE implementation for all historical, shadow, and research calculations.
    """

    @staticmethod
    def calculate_trade_pnl(
        entry_price: float,
        exit_price: float,
        direction: str,
        position_size: float = 100000.0,
        transaction_cost_pct: float = 0.10,
        slippage_pct: float = 0.10
    ) -> Dict[str, Any]:
        """
        Inputs:
            entry: Entry Price
            exit: Exit Price
            direction: LONG or SHORT
            position_size: Total capital allocated to trade (INR)
            transaction_cost_pct: Brokerage, STT, etc. (per side, but usually applied as round-trip total here)
            slippage_pct: Estimated execution slippage
        """
        if not entry_price or not exit_price or entry_price <= 0:
            return {
                "gross_return_pct": 0.0,
                "net_return_pct": 0.0,
                "gross_pnl": 0.0,
                "net_pnl": 0.0,
                "transaction_cost": 0.0,
                "slippage": 0.0
            }

        # 1. Gross Return %
        if direction.upper() == "LONG":
            gross_return_pct = ((exit_price - entry_price) / entry_price) * 100
        else:
            gross_return_pct = ((entry_price - exit_price) / entry_price) * 100

        # 2. Capital-based Gross P&L
        gross_pnl = (gross_return_pct / 100) * position_size

        # 3. Costs (Absolute)
        # Assuming transaction_cost_pct and slippage_pct are total round-trip percentages
        total_cost_pct = transaction_cost_pct + slippage_pct
        cost_amount = (total_cost_pct / 100) * position_size

        transaction_cost = (transaction_cost_pct / 100) * position_size
        slippage = (slippage_pct / 100) * position_size

        # 4. Net Calculations
        net_pnl = gross_pnl - cost_amount
        net_return_pct = (net_pnl / position_size) * 100

        return {
            "gross_return_pct": round(gross_return_pct, 4),
            "net_return_pct": round(net_return_pct, 4),
            "gross_pnl": round(gross_pnl, 2),
            "net_pnl": round(net_pnl, 2),
            "transaction_cost": round(transaction_cost, 2),
            "slippage": round(slippage, 2)
        }
