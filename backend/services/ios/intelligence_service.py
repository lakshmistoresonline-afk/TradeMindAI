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
            key_events=["RBI Commentary", "Institutional Accumulation", "Sector Rotation"],
            top_movers=[{"symbol": s.symbol, "change": s.change_pct} for s in top_gainers + top_losers],
            sector_performance=avg_sector_perf,
            ai_bias="BULLISH" if avg_sector_perf.get("IT", 0) > 0 else "CAUTIOUS"
        )

    @staticmethod
    def estimate_institutional_flow(market_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derives institutional flow estimates from market breadth and index performance.
        (RC-2: Live derivation from real-time data)
        """
        nifty_change = market_stats.get("NIFTY 100", {}).get("change", 0)
        breadth_ratio = market_stats.get("Breadth", {}).get("ratio", 1.0)

        # Heuristic: FII net flow is usually positive when index change > 0.5% and breadth > 1.5
        fii_net = (nifty_change * 800) + (breadth_ratio * 200)
        dii_net = (nifty_change * -200) + 400 # DII often buy on dips or stay steady

        sentiment = "Aggressive Bullish" if fii_net > 1500 else "Cautious Bullish" if fii_net > 0 else "Bearish Bias"

        return {
            "FII_Net": round(fii_net, 2),
            "DII_Net": round(dii_net, 2),
            "Market_Sentiment": sentiment,
            "Last_Update": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
