from fastapi import APIRouter, Depends
from backend.core.container import get_stock_service, container
from backend.services.stock_service import StockService
from backend.services.portfolio_engine import PortfolioEngine
from backend.core.auth import get_current_user
from fastapi_cache.decorator import cache
import yfinance as yf
from typing import List, Optional
import datetime
import requests
import json
import traceback

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
async def get_market_stats():
    indices = {
        "^NSEI": "NIFTY 50",
        "^CNX100": "NIFTY 100",
        "^NSEBANK": "BANK NIFTY",
        "^INDIAVIX": "India VIX"
    }
    stats = {}

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        for symbol, name in indices.items():
            try:
                # 1. Try manual scraper first (Fastest and most reliable on servers)
                price, prev = 0.0, 0.0
                try:
                    r = session.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d", timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        chart = data['chart']['result'][0]
                        closes = chart['indicators']['quote'][0]['close']
                        valid_closes = [c for c in closes if c is not None]
                        if valid_closes:
                            price = valid_closes[-1]
                            prev = valid_closes[-2] if len(valid_closes) > 1 else price
                except: pass

                # 2. Try yfinance history as fallback
                if price == 0:
                    ticker = yf.Ticker(symbol, session=session)
                    df = ticker.history(period="2d")
                    if not df.empty:
                        price = float(df["Close"].iloc[-1])
                        prev = float(df["Close"].iloc[-2]) if len(df) > 1 else price

                stats[name] = {
                    "value": round(float(price), 2),
                    "change": round(float(((price - prev) / prev) * 100), 2) if (prev and prev != 0) else 0.0
                }
            except Exception as e:
                print(f"Error fetching index {name}: {e}")
                stats[name] = {"value": 0, "change": 0}

        # 3. Market Breadth Calculation (SQL Tier)
        stocks_list = await container.repository.get_all_stocks(limit=150)
        advancing, declining = 0, 0
        for stock in stocks_list:
            change = getattr(stock, 'change_pct', 0) or 0
            if change > 0: advancing += 1
            elif change < 0: declining += 1

        stats["Breadth"] = {
            "advancing": advancing,
            "declining": declining,
            "ratio": round(advancing/declining, 2) if declining > 0 else float(advancing)
        }
    except Exception as e:
        print(f"Global market stats error: {e}")
        if "Breadth" not in stats:
            stats["Breadth"] = {"advancing": 0, "declining": 0, "ratio": 0}

    return stats

@router.get("/fii-dii")
async def get_institutional_flow():
    stats = await get_market_stats()
    return container.intel_service.estimate_institutional_flow(stats)

@router.get("/")
async def get_stocks(
    limit: int = 50,
    offset: int = 0,
    service: StockService = Depends(get_stock_service)
):
    return await service.get_market_overview(limit, offset)

@router.get("/{symbol}")
async def get_stock_detail(
    symbol: str,
    service: StockService = Depends(get_stock_service)
):
    stock = await service.repository.get_stock_by_symbol(symbol)
    if stock:
        return stock
    return {"error": "Stock not found"}

@router.get("/provider/capabilities")
async def get_provider_capabilities():
    return container.provider.capabilities

@router.get("/{symbol}/option-chain")
async def get_option_chain(symbol: str, expiry: Optional[str] = None):
    exp_dt = datetime.datetime.fromisoformat(expiry) if expiry else None
    return await container.provider.get_option_chain(symbol, exp_dt)

@router.get("/{symbol}/ltp")
async def get_stock_ltp(symbol: str):
    return {"symbol": symbol, "ltp": await container.provider.get_ltp(symbol)}

@router.get("/{symbol}/news")
async def get_stock_news(symbol: str):
    return await container.data_platform_repo.get_latest_news(symbol)

@router.get("/{symbol}/earnings")
async def get_stock_earnings(symbol: str):
    return await container.data_platform_repo.get_latest_earnings(symbol)

@router.get("/{symbol}/timeline")
async def get_stock_timeline(symbol: str):
    from google.cloud import firestore
    from backend.core.database import db_client

    if db_client is None:
        return []

    try:
        docs = db_client.collection("stocks").document(symbol).collection("timeline")\
            .order_by("date", direction=firestore.Query.DESCENDING).limit(20).stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Firestore timeline error: {e}")
        return []
