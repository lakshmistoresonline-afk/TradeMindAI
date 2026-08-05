from fastapi import APIRouter, Depends
from backend.core.container import get_stock_service
from backend.services.stock_service import StockService
from backend.core.auth import get_current_user
import yfinance as yf

router = APIRouter()

@router.get("/market-stats")
async def get_market_stats():
    # Keep public for dashboard loading
    indices = {
        "^NSEI": "NIFTY 50",
        "^NSEBANK": "BANK NIFTY",
        "^INDIAVIX": "India VIX"
    }
    stats = {}
    for symbol, name in indices.items():
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        stats[name] = {
            "value": round(info.last_price, 2),
            "change": round(((info.last_price - info.previous_close) / info.previous_close) * 100, 2)
        }
    return stats

@router.get("/fii-dii")
async def get_institutional_flow():
    # Mock data for institutional flow
    return {
        "FII_Net": 1240.50, # In Crores
        "DII_Net": -850.20,
        "Market_Sentiment": "Cautious Bullish",
        "Last_Update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }

@router.get("/")
async def get_stocks(
    service: StockService = Depends(get_stock_service)
):
    return await service.get_market_overview()

@router.get("/{symbol}")
async def get_stock_detail(
    symbol: str,
    service: StockService = Depends(get_stock_service)
):
    stock = await service.repository.get_stock_by_symbol(symbol)
    if stock:
        return stock
    return {"error": "Stock not found"}
