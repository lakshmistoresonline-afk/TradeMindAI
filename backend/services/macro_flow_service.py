"""
================================================================================
TradeMindAI: Macroeconomic Liquidity & FII/DII Flow Gating Service
================================================================================
Evaluates institutional net cash flows and macro liquidity conditions as gating filters.
"""

from typing import Dict, Any

class MacroFlowService:
    @staticmethod
    def evaluate_macro_gate(fii_net_crores: float = 500.0, usd_inr_change: float = 0.0) -> Dict[str, Any]:
        """
        Blocks long trades during heavy FII institutional outflow or currency stress.
        """
        # Block long entries if FII net selling exceeds ₹2,000 Crores
        macro_approved = bool(fii_net_crores >= -2000.0 and usd_inr_change <= 0.25)

        return {
            "fii_net_crores": fii_net_crores,
            "macro_approved": macro_approved,
            "reason": "Institutional liquidity supportive" if macro_approved else "Heavy FII outflow or currency pressure detected"
        }
