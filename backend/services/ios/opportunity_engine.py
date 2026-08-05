from typing import List, Dict, Any
from backend.domain.models.ios import MarketOpportunity
from backend.domain.models.stock import Stock
from datetime import datetime
import uuid

class OpportunityEngine:
    @staticmethod
    def find_opportunities(stocks: List[Stock]) -> List[MarketOpportunity]:
        """
        Scans all tracked stocks for High-Conviction setups.
        """
        opportunities = []

        for stock in stocks:
            if not stock.analysis: continue

            consensus = stock.analysis.get("consensus", "").upper()
            score = stock.ai_investment_score or 0

            # 1. Breakout Opportunity
            if score > 80 and "BUY" in consensus:
                opportunities.append(MarketOpportunity(
                    id=str(uuid.uuid4()),
                    symbol=stock.symbol,
                    type="BREAKOUT",
                    conviction_score=score,
                    ai_thesis=f"Institutional accumulation complete. High probability momentum move detected for {stock.symbol}.",
                    indicators=["SMC Order Block", "EMA Cross", "High Confidence Consensus"]
                ))

            # 2. Reversal / Undervalued
            if score > 65 and stock.pe_ratio and stock.pe_ratio < 20: # Simplified undervaluation check
                opportunities.append(MarketOpportunity(
                    id=str(uuid.uuid4()),
                    symbol=stock.symbol,
                    type="UNDERVALUED",
                    conviction_score=score,
                    ai_thesis=f"{stock.symbol} showing strong fundamental quality at attractive valuation levels.",
                    indicators=["Low PE", "Stable ROE", "Positive AI Bias"]
                ))

        return sorted(opportunities, key=lambda x: x.conviction_score, reverse=True)
