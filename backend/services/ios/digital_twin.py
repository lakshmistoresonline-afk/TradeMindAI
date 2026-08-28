from typing import Dict, Any, List
from backend.domain.interfaces.repository import IStockRepository, IDataPlatformRepository
from backend.domain.models.stock import Stock
from datetime import datetime

class DigitalTwinService:
    def __init__(self, stock_repo: IStockRepository, data_repo: IDataPlatformRepository):
        self.stock_repo = stock_repo
        self.data_repo = data_repo

    async def get_stock_twin(self, symbol: str) -> Dict[str, Any]:
        """
        Vision 2.0: Digital Twin.
        A unified, continuously updated profile of a stock combining all intelligence layers.
        """
        stock = await self.stock_repo.get_stock_by_symbol(symbol)
        if not stock: return {}

        # 1. Gather all intelligence layers
        history = await self.stock_repo.get_recent_prices(symbol, limit=30)
        features = await self.data_repo.get_features_by_range(
            symbol,
            datetime.utcnow().replace(hour=0, minute=0),
            datetime.utcnow()
        )

        # 2. Synthesize the "DNA" of the stock
        ema_50 = 0
        if history and history[-1].indicators:
            ema_50 = history[-1].indicators.get("EMA_50", 0)

        twin = {
            "identity": {
                "symbol": stock.symbol,
                "name": stock.name,
                "sector": stock.sector,
                "market_cap": stock.market_cap
            },
            "intelligence_state": {
                "ai_score": stock.ai_investment_score,
                "grade": stock.ai_investment_grade,
                "health": stock.health_metrics,
                "consensus": stock.analysis.get("consensus") if stock.analysis else "N/A"
            },
            "structured_consensus": getattr(stock, 'structured_consensus', {}),
            "technical_posture": {
                "trend": "BULLISH" if stock.last_price > ema_50 else "BEARISH" if ema_50 > 0 else "NEUTRAL",
                "volatility": "HIGH" if stock.beta and stock.beta > 1.2 else "LOW",
                "momentum": stock.analysis.get("technical_data", {}).get("indicators", {}).get("momentum_rsi", 0.5) if stock.analysis else 0.5
            },
            "risk_profile": {
                "beta": stock.beta,
                "max_drawdown": stock.analysis.get("technical_data", {}).get("quant_metrics", {}).get("max_drawdown", 0) if stock.analysis else 0,
                "confidence": stock.confidence_metrics.get("score") if stock.confidence_metrics else 0
            },
            "updated_at": datetime.utcnow()
        }

        return twin
