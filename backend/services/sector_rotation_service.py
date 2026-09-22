import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from sqlalchemy import text
from backend.core.postgres import SessionLocal, SectorMetricDB, StockDB

class SectorRotationService:
    """
    Workstream 2: Sector Rotation Engine.
    Calculates relative strength and momentum for sectors.
    """

    @staticmethod
    async def calculate_sector_metrics(stocks: List[Any]) -> List[Dict[str, Any]]:
        """
        Calculates aggregate performance and momentum for each sector.
        """
        if not stocks: return []

        df = pd.DataFrame([{"symbol": s.symbol, "sector": s.sector, "change": s.change_pct, "price": s.last_price} for s in stocks])
        if df.empty or 'sector' not in df.columns or 'change' not in df.columns:
            return []

        df = df.dropna(subset=['sector', 'change'])

        if df.empty: return []

        sector_groups = df.groupby('sector')
        metrics = []

        for sector, group in sector_groups:
            avg_change = group['change'].mean()
            volatility = group['change'].std()

            # Simple Volume score placeholder (requires volume data in df)
            volume_score = 0.5

            metrics.append({
                "date": datetime.date.today(),
                "sector": sector,
                "relative_strength": round(float(avg_change * 10), 2), # Heuristic
                "momentum": round(float(avg_change), 2),
                "trend": "BULLISH" if avg_change > 0.5 else "BEARISH" if avg_change < -0.5 else "SIDEWAYS",
                "volume_score": volume_score,
                "volatility": round(float(volatility), 2) if not pd.isna(volatility) else 0.0
            })

        # Rank sectors by momentum
        metrics.sort(key=lambda x: x['momentum'], reverse=True)
        for i, m in enumerate(metrics):
            m['rank'] = i + 1

        return metrics

    @staticmethod
    async def persist_sector_snapshots(metrics: List[Dict[str, Any]]):
        with SessionLocal() as session:
            for m in metrics:
                db_m = SectorMetricDB(**m)
                session.add(db_m)
            session.commit()

    @staticmethod
    def get_latest_sector_rankings() -> List[Dict[str, Any]]:
        with SessionLocal() as session:
            latest_date = session.query(text("max(date)")).from_statement(text("SELECT max(date) FROM sector_metrics")).scalar()
            if not latest_date: return []

            res = session.query(SectorMetricDB).filter(SectorMetricDB.date == latest_date).order_by(SectorMetricDB.rank.asc()).all()
            return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in res]

    @staticmethod
    def get_stock_sector_bias(sector: Optional[str]) -> Dict[str, Any]:
        """
        Retrieves sector rank, trend, and relative strength bias for a given sector name.
        """
        if not sector:
            return {"rank": 5, "total_sectors": 10, "trend": "NEUTRAL", "bias": "NEUTRAL"}

        try:
            rankings = SectorRotationService.get_latest_sector_rankings()
            if not rankings:
                return {"rank": 5, "total_sectors": 10, "trend": "NEUTRAL", "bias": "NEUTRAL"}

            total = len(rankings)
            for item in rankings:
                if item.get("sector", "").lower() == sector.lower():
                    rank = item.get("rank", 5)
                    trend = item.get("trend", "NEUTRAL")
                    bias = "STRONG" if rank <= 3 else "WEAK" if rank >= (total - 2) else "NEUTRAL"
                    return {
                        "sector": sector,
                        "rank": rank,
                        "total_sectors": total,
                        "trend": trend,
                        "bias": bias,
                        "momentum": item.get("momentum", 0.0)
                    }
        except Exception:
            pass

        return {"sector": sector, "rank": 5, "total_sectors": 10, "trend": "NEUTRAL", "bias": "NEUTRAL"}
