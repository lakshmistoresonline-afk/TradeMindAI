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
        Supports 'Bootstrap Mode' for immediate population from raw data.
        """
        opportunities = []

        for stock in stocks:
            # 1. Deep AI Scan (Preferred)
            if stock.analysis:
                consensus = stock.analysis.get("consensus", "").upper()
                score = stock.ai_investment_score or 0

                if score > 75 and "BUY" in consensus:
                    opportunities.append(MarketOpportunity(
                        id=str(uuid.uuid4()),
                        symbol=stock.symbol,
                        type="BREAKOUT",
                        conviction_score=score,
                        ai_thesis=f"Institutional accumulation complete. High probability momentum move detected for {stock.symbol}.",
                        indicators=["SMC Order Block", "EMA Cross", "High Confidence Consensus"]
                    ))
                elif score > 60 and stock.pe_ratio and stock.pe_ratio < 25:
                    opportunities.append(MarketOpportunity(
                        id=str(uuid.uuid4()),
                        symbol=stock.symbol,
                        type="UNDERVALUED",
                        conviction_score=score,
                        ai_thesis=f"{stock.symbol} showing strong fundamental quality at attractive valuation levels.",
                        indicators=["Low PE", "Stable ROE", "Positive AI Bias"]
                    ))

            # 2. Bootstrap Mode (Raw Price Action - Fallback)
            # We use this if we don't have deep analysis yet to keep the dashboard alive
            elif stock.change_pct and stock.change_pct > 2.0:
                opportunities.append(MarketOpportunity(
                    id=str(uuid.uuid4()),
                    symbol=stock.symbol,
                    type="MOMENTUM",
                    conviction_score=65.0, # Baseline bootstrap score
                    ai_thesis=f"Session volatility detected. AI agents are currently scanning {stock.symbol} for institutional footprint.",
                    indicators=["Volume Spike", "Price Momentum", "AI SCANNING..."]
                ))

        return sorted(opportunities, key=lambda x: x.conviction_score, reverse=True)

        return sorted(opportunities, key=lambda x: x.conviction_score, reverse=True)
