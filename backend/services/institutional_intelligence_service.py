import datetime
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, InstitutionalMetricDB, BulkDealDB

class InstitutionalIntelligenceService:
    """
    Workstream 7: Institutional Intelligence.
    Tracks FII/DII net flows and aggregate institutional pressure.
    """

    @staticmethod
    async def record_daily_flow(fii_net: float, dii_net: float):
        with SessionLocal() as session:
            today = datetime.date.today()

            # Fetch cumulative
            prev = session.query(InstitutionalMetricDB).order_by(InstitutionalMetricDB.date.desc()).first()
            fii_cum = (prev.fii_cumulative if prev else 0.0) + fii_net
            dii_cum = (prev.dii_cumulative if prev else 0.0) + dii_net

            metric = InstitutionalMetricDB(
                date=today,
                fii_net=fii_net,
                dii_net=dii_net,
                fii_cumulative=fii_cum,
                dii_cumulative=dii_cum,
                sentiment_bias="BULLISH" if fii_net > 0 else "BEARISH",
                institutional_pressure=1.0 if fii_net > 1000 else -1.0 if fii_net < -1000 else 0.0
            )
            session.merge(metric)
            session.commit()

    @staticmethod
    def get_institutional_bias() -> Dict[str, Any]:
        with SessionLocal() as session:
            res = session.query(InstitutionalMetricDB).order_by(InstitutionalMetricDB.date.desc()).limit(10).all()
            if not res: return {"bias": "NEUTRAL", "pressure": 0.0}

            latest = res[0]
            avg_fii = sum(r.fii_net for r in res) / len(res)

            return {
                "bias": latest.sentiment_bias,
                "pressure": latest.institutional_pressure,
                "fii_net_today": latest.fii_net,
                "dii_net_today": latest.dii_net,
                "fii_avg_10d": round(avg_fii, 2)
            }
