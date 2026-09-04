import datetime
import uuid
from typing import List, Dict, Any
from backend.core.postgres import SessionLocal, OpportunityDB, StockDB, SectorMetricDB
from sqlalchemy import func

class OpportunityRadarService:
    """
    Workstream 4: Opportunity Radar.
    Discovery layer separate from trade signals.
    Categories: MOMENTUM, BREAKOUT, BREAKDOWN, RELATIVE STRENGTH, etc.
    """

    @staticmethod
    async def scan_opportunities(stocks: List[Any]) -> List[Dict[str, Any]]:
        """
        Runs multiple discovery algorithms to identify technical/institutional opportunities.
        """
        opportunities = []
        now = datetime.datetime.utcnow()

        for stock in stocks:
            # 1. Momentum / Relative Strength
            if stock.change_pct and stock.change_pct > 3.0:
                opportunities.append({
                    "id": str(uuid.uuid4()),
                    "symbol": stock.symbol,
                    "type": "MOMENTUM",
                    "conviction_score": 85.0,
                    "ai_thesis": f"Strong intraday momentum in {stock.symbol} with positive price velocity.",
                    "indicators": json.dumps(["Price > 3%", "High Volume"]),
                    "timestamp": now
                })

            # 2. Breakout (Near 52W High)
            if stock.last_price and stock.high_52w and stock.last_price > (stock.high_52w * 0.98):
                opportunities.append({
                    "id": str(uuid.uuid4()),
                    "symbol": stock.symbol,
                    "type": "BREAKOUT",
                    "conviction_score": 75.0,
                    "ai_thesis": f"{stock.symbol} is testing 52-week highs. Potential for trend expansion.",
                    "indicators": json.dumps(["Near 52W High", "Trend Alignment"]),
                    "timestamp": now
                })

            # 3. Institutional Pressure (Heuristic)
            if stock.avg_volume and stock.volume and stock.volume > (stock.avg_volume * 2.0):
                 opportunities.append({
                    "id": str(uuid.uuid4()),
                    "symbol": stock.symbol,
                    "type": "INSTITUTIONAL_ACCUMULATION",
                    "conviction_score": 80.0,
                    "ai_thesis": f"Abnormal volume spike in {stock.symbol} suggests institutional interest.",
                    "indicators": json.dumps(["Volume > 2x Avg", "Delivery Spike"]),
                    "timestamp": now
                })

        # Persist top 20
        with SessionLocal() as session:
            # Clear old opportunities (Rolling window)
            session.query(OpportunityDB).delete()
            for opp in opportunities[:50]:
                session.add(OpportunityDB(**opp))
            session.commit()

        return opportunities

    @staticmethod
    def get_radar_view() -> List[Dict[str, Any]]:
        with SessionLocal() as session:
            res = session.query(OpportunityDB).order_by(OpportunityDB.conviction_score.desc()).all()
            return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in res]

import json
