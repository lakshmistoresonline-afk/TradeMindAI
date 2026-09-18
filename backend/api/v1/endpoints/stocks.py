from fastapi import APIRouter, Depends
from backend.core.container import get_stock_service, container
from backend.services.stock_service import StockService
from backend.core.auth import get_current_user
from fastapi_cache.decorator import cache
import yfinance as yf
from typing import List, Optional
import datetime
import requests
import json
import traceback

router = APIRouter()

@router.get("/market-stats")
@cache(expire=300)
async def get_market_stats():
    from backend.services.market_data_service import MarketDataService
    market_state = await MarketDataService.get_market_state()

    indices = {
        "^NSEI": "NIFTY 50",
        "^CNX100": "NIFTY 100",
        "^NSEBANK": "BANK NIFTY",
        "^INDIAVIX": "India VIX"
    }
    stats = {}

    stats["NIFTY 50"] = {"value": 0, "change": 0}
    stats["India VIX"] = {"value": market_state.get("vix", 14.5), "change": 0}

    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        for symbol, name in indices.items():
            if name == "India VIX": continue

            try:
                price, prev = 0.0, 0.0
                r = session.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    chart = data['chart']['result'][0]
                    closes = chart['indicators']['quote'][0]['close']
                    valid_closes = [c for c in closes if c is not None]
                    if valid_closes:
                        price = valid_closes[-1]
                        prev = valid_closes[-2] if len(valid_closes) > 1 else price

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
            except:
                stats[name] = {"value": 0, "change": 0}

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
