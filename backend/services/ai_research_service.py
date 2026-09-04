import datetime
from typing import Dict, Any, Optional
from backend.core.container import container

class AIResearchService:
    """
    Workstream 6: AI Research Copilot.
    Provides structured research summaries based on stored evidence.
    """

    @staticmethod
    async def get_comprehensive_research(symbol: str) -> Dict[str, Any]:
        # 1. Gather all sub-intelligence
        stock = await container.repository.get_stock_by_symbol(symbol)
        if not stock: return {"status": "NOT_FOUND"}

        matrix = container.evidence_matrix_service.get_stock_evidence_matrix(symbol)
        profile = container.stock_intelligence_service.get_latest_profile(symbol)
        fnd = await container.fundamental_service.get_stock_fundamentals(symbol)

        # 2. Synthesize Summary
        # (In a real product this would call LLM with these facts as context)
        summary = f"{symbol} is showing a {matrix['matrix']['TECHNICAL']['bias']} technical bias within a {matrix['matrix']['MARKET']['bias']} market regime."

        return {
            "symbol": symbol,
            "summary": summary,
            "market_context": matrix['matrix']['MARKET'],
            "sector_context": matrix['matrix']['SECTOR'],
            "technical_context": profile,
            "fundamental_context": fnd,
            "supporting_evidence": [
                f"Trend Score: {profile.get('trend_score') if profile else 'N/A'}",
                f"PE Ratio: {fnd.get('pe_ratio') if fnd else 'N/A'}"
            ],
            "contradicting_evidence": [],
            "risk_factors": [
                f"Market Volatility: {matrix['matrix']['MARKET'].get('confidence')}"
            ],
            "timestamp": datetime.datetime.utcnow()
        }
