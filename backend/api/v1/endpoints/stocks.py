from fastapi import APIRouter, Depends
from backend.core.container import get_stock_service, container
from backend.services.stock_service import StockService
from backend.services.portfolio_engine import PortfolioEngine
from backend.core.auth import get_current_user
from fastapi_cache.decorator import cache
import yfinance as yf
from typing import List
import datetime

router = APIRouter()

@router.post("/portfolio/analyze")
async def analyze_portfolio(
    symbols: List[str],
    current_user: dict = Depends(get_current_user)
):
    service = get_stock_service()
    holdings = []
    for symbol in symbols:
        stock = await service.repository.get_stock_by_symbol(symbol)
        if stock:
            holdings.append(stock)

    health = PortfolioEngine.analyze_health(current_user["uid"], holdings)
    await container.data_platform_repo.save_portfolio_health(health)
    return health

@router.get("/market-stats")
@cache(expire=300) # Cache indices for 5 minutes
async def get_market_stats():
    # Keep public for dashboard loading
    indices = {
        "^NSEI": "NIFTY 50",
        "^CNX100": "NIFTY 100",
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

    # Vision 2.0: Market Breadth Calculation
    from backend.core.database import db_client
    stocks_ref = db_client.collection("stocks").limit(100).stream()
    advancing, declining = 0, 0
    for doc in stocks_ref:
        data = doc.to_dict()
        change = data.get("change_pct", 0)
        if change > 0: advancing += 1
        elif change < 0: declining += 1

    stats["Breadth"] = {
        "advancing": advancing,
        "declining": declining,
        "ratio": round(advancing/declining, 2) if declining > 0 else advancing
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
@cache(expire=600)
async def get_stocks(
    limit: int = 50,
    offset: int = 0,
    service: StockService = Depends(get_stock_service)
):
    return await service.get_market_overview(limit, offset)

@router.get("/{symbol}")
@cache(expire=600)
async def get_stock_detail(
    symbol: str,
    service: StockService = Depends(get_stock_service)
):
    stock = await service.repository.get_stock_by_symbol(symbol)
    if stock:
        return stock
    return {"error": "Stock not found"}
