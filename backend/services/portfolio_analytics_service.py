import datetime
from typing import Dict, Any, List
from backend.core.postgres import SessionLocal, ShadowSignalDB, StockDB

class PortfolioAnalyticsService:
    """
    Workstream 15: Portfolio Research & Analytics.
    Calculates sector exposure, risk concentration, and beta.
    """

    @staticmethod
    def get_risk_analytics() -> Dict[str, Any]:
        with SessionLocal() as session:
            active = session.query(ShadowSignalDB, StockDB.sector, StockDB.beta).join(
                StockDB, ShadowSignalDB.symbol == StockDB.symbol, isouter=True
            ).filter(ShadowSignalDB.status == 'ACTIVE').all()

            if not active: return {"status": "NO_ACTIVE_EXPOSURE"}

            total_exposure = sum(s.capital_allocation or 100000.0 for s, _, _ in active)

            # Sector Concentration
            sectors = {}
            for s, sector, _ in active:
                sec = sector or "Unknown"
                sectors[sec] = sectors.get(sec, 0.0) + (s.capital_allocation or 100000.0)

            # Direction Concentration
            long_exp = sum(s.capital_allocation or 100000.0 for s, _, _ in active if s.direction == 'LONG')
            short_exp = sum(s.capital_allocation or 100000.0 for s, _, _ in active if s.direction == 'SHORT')

            # Portfolio Beta (Weighted average)
            total_beta = 0.0
            for s, _, beta in active:
                weight = (s.capital_allocation or 100000.0) / total_exposure
                total_beta += (beta or 1.0) * weight

            return {
                "total_exposure": round(total_exposure, 2),
                "sector_concentration": {k: round(v/total_exposure*100, 1) for k, v in sectors.items()},
                "directional_bias": "BULLISH" if long_exp > short_exp else "BEARISH",
                "net_exposure_pct": round((long_exp - short_exp) / total_exposure * 100, 1),
                "portfolio_beta": round(total_beta, 2),
                "risk_status": "NORMAL" if total_beta < 1.3 else "HIGH_EXPOSURE"
            }
