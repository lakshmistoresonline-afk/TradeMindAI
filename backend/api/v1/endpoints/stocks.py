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

    try:
        import requests
        # Mimic browser to avoid IP blocking
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        for symbol, name in indices.items():
            try:
                # RC-4: Extremely resilient index fetch using dual-layer fallback
                # 1. Try yfinance history
                ticker = yf.Ticker(symbol, session=session)
                df = ticker.history(period="2d")

                price, prev = 0.0, 0.0
                if not df.empty:
                    price = float(df["Close"].iloc[-1])
                    prev = float(df["Close"].iloc[-2]) if len(df) > 1 else price

                # 2. If history failed (Common on restricted servers), try manual scrape fallback
                if price == 0:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d", headers=headers)
                    if r.status_code == 200:
                        data = r.json()
                        meta = data['chart']['result'][0]['meta']
                        price = meta['regularMarketPrice']
                        prev = meta['previousClose']

                stats[name] = {
                    "value": round(float(price), 2),
                    "change": round(float(((price - prev) / prev) * 100), 2) if (prev and prev != 0) else 0.0
                }
            except Exception as e:
                import traceback
                print(f"Error fetching index {name}: {e}")
                stats[name] = {"value": 0, "change": 0, "error": str(e), "trace": traceback.format_exc()[:100]}
                import traceback
                print(f"Error fetching index {name}: {e}")
                stats[name] = {"value": 0, "change": 0, "error": str(e), "trace": traceback.format_exc()[:100]}

        # Vision 2.0: Market Breadth Calculation
        # Increased limit for broader coverage - Now using Repository (SQL)
        stocks_list = await container.repository.get_all_stocks(limit=150)
        advancing, declining = 0, 0
        for stock in stocks_list:
            # Resilient check for change_pct (SQL often returns float or None)
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
        # Ensure we return a valid structure even on failure
        if "Breadth" not in stats:
            stats["Breadth"] = {"advancing": 0, "declining": 0, "ratio": 0}

    return stats

@router.get("/fii-dii")
async def get_institutional_flow():
    """
    Vision 2.0: Institutional Cash Flow Audit.
    Returns estimates derived from real-time market breadth and volume.
    """
    stats = await get_market_stats()
    return container.intel_service.estimate_institutional_flow(stats)

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

@router.get("/{symbol}/news")
async def get_stock_news(
    symbol: str
):
    """
    Fetches the latest institutional news and AI sentiment for a stock.
    """
    return await container.data_platform_repo.get_latest_news(symbol)

@router.get("/{symbol}/earnings")
async def get_stock_earnings(
    symbol: str
):
    """
    Fetches the latest earnings data and upcoming dates for a stock.
    """
    return await container.data_platform_repo.get_latest_earnings(symbol)

@router.get("/{symbol}/timeline")
async def get_stock_timeline(
    symbol: str
):
    """
    Fetches the institutional intelligence timeline for a stock.
    """
    docs = container.repository.db.collection("stocks").document(symbol).collection("timeline")\
        .order_by("date", direction=firestore.Query.DESCENDING).limit(20).stream()
    return [doc.to_dict() for doc in docs]
