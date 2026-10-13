"""
Indian Market Tick Size & Slippage Model
Models NSE ₹0.05 tick size rounding, STT, exchange turnover fees, and impact cost.
"""

from typing import Dict, Any

class NSESlippageModel:
    @staticmethod
    def calculate_execution_cost(price: float, quantity: int, is_intraday: bool = True) -> Dict[str, Any]:
        """
        Calculates realistic transaction costs and slippage for Indian cash equities.
        Tick size = ₹0.05
        """
        # Round price to nearest 0.05 tick
        tick_rounded_price = round(price * 20) / 20.0
        turnover = price * quantity

        # Estimated statutory & brokerage charges (STT, Exchange transaction charges, GST, SEBI turnover)
        stt = turnover * 0.00025 if is_intraday else turnover * 0.001
        exchange_charges = turnover * 0.0000325
        gst = exchange_charges * 0.18
        sebi_charges = turnover * 0.000001
        total_taxes = stt + exchange_charges + gst + sebi_charges

        # Impact cost slippage (approx 0.05% for liquid stocks)
        estimated_slippage_rs = turnover * 0.0005

        return {
            "tick_rounded_price": tick_rounded_price,
            "total_taxes_rs": total_taxes,
            "estimated_slippage_rs": estimated_slippage_rs,
            "net_execution_cost_rs": total_taxes + estimated_slippage_rs
        }
