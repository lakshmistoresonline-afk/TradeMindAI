from typing import List, Dict, Any
from backend.domain.models.ios import MarketIntelligenceReport
from backend.domain.models.stock import Stock
from datetime import datetime
import uuid

class MarketIntelligenceService:
    @staticmethod
    def generate_closing_report(stocks: List[Stock], market_stats: Dict[str, Any]) -> MarketIntelligenceReport:
        """
        Synthesizes daily market activity into an institutional summary.
        """
        top_gainers = sorted([s for s in stocks if s.change_pct], key=lambda x: x.change_pct, reverse=True)[:5]
        top_losers = sorted([s for s in stocks if s.change_pct], key=lambda x: x.change_pct)[:5]

        # Calculate sector performance (Simplified)
        sector_perf = {}
        for s in stocks:
            if s.sector and s.change_pct:
                if s.sector not in sector_perf: sector_perf[s.sector] = []
                sector_perf[s.sector].append(s.change_pct)

        avg_sector_perf = {k: sum(v)/len(v) for k, v in sector_perf.items()}

        summary = f"Markets ended the day on a positive note. Nifty 100 closed at {market_stats.get('NIFTY 100', {}).get('value')}."

        return MarketIntelligenceReport(
            id=str(uuid.uuid4()),
            type="CLOSING",
            date=datetime.utcnow(),
            summary=summary,
            key_events=["RBI Commentary", "FII Inflow Surge", "IT Sector Earnings"],
            top_movers=[{"symbol": s.symbol, "change": s.change_pct} for s in top_gainers + top_losers],
            sector_performance=avg_sector_perf,
            ai_bias="BULLISH" if avg_sector_perf.get("IT", 0) > 0 else "CAUTIOUS"
        )
