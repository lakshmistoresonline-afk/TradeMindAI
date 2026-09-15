import datetime
import json
from typing import Dict, Any, List, Optional
from backend.core.postgres import SessionLocal, StockIntelligenceDB, StockDB

class StockIntelligenceService:
    """
    Workstream 3: Stock Intelligence Engine.
    Creates structured intelligence profiles for every constituent.
    """

    @staticmethod
    async def generate_stock_profile(symbol: str, features: Dict[str, Any], stock: Any, regime: str) -> Dict[str, Any]:
        """
        Synthesizes raw features into a high-level technical/fundamental profile.
        """
        price = stock.last_price or 0.0
        ema200 = features.get("ema_200", price)
        rsi = features.get("rsi", 50.0)

        # 1. Technical Structure
        structure = {
            "trend": "UP" if price > ema200 else "DOWN",
            "overbought_oversold": "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL",
            "support": price * 0.95, # Placeholder for real S/R detection
            "resistance": price * 1.05
        }

        profile = {
            "symbol": symbol,
            "date": datetime.date.today(),
            "trend_score": 1.0 if price > ema200 else 0.0,
            "momentum_score": round(float((rsi - 50) / 50), 2),
            "volatility_score": round(features.get("ATR", 0.0) / price, 4) if price > 0 else 0.0,
            "rs_rating": features.get("rs_rating", 0.0),
            "technical_structure": json.dumps(structure),
            "fundamental_score": None, # DATA_UNAVAILABLE
            "institutional_pressure": None,
            "market_regime": regime,
            "sector_regime": None,
            "composite_intelligence_score": None,
            "last_updated": datetime.datetime.utcnow()
        }

        return profile

    @staticmethod
    async def persist_profile(profile: Dict[str, Any]):
        with SessionLocal() as session:
            db_p = StockIntelligenceDB(**profile)
            session.add(db_p)
            session.commit()

    @staticmethod
    def get_latest_profile(symbol: str) -> Optional[Dict[str, Any]]:
        with SessionLocal() as session:
            res = session.query(StockIntelligenceDB).filter(StockIntelligenceDB.symbol == symbol).order_by(StockIntelligenceDB.last_updated.desc()).first()
            if res:
                data = {c.name: getattr(res, c.name) for c in res.__table__.columns}
                if data.get('technical_structure'):
                    data['technical_structure'] = json.loads(data['technical_structure'])
                return data
            return None
