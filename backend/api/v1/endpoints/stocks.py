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
    """
    Hardened Market Index Fetcher (Institutional V2.2).
    Fetches NIFTY 50, 100, 200 and VIX via authoritative yfinance bulk wrappers.
    """
    from backend.services.market_data_service import MarketDataService
    market_state = await MarketDataService.get_market_state()

    indices = {
        "^NSEI": "NIFTY 50",
        "^CNX100": "NIFTY 100",
        "^CNX200": "NIFTY 200",
        "^INDIAVIX": "India VIX"
    }
    stats = {}

    # Initialize with default/cache values
    for name in indices.values():
        stats[name] = {"value": 0, "change": 0}

    stats["India VIX"]["value"] = market_state.get("vix", 14.5)

    try:
        # P0: Bulk download indices for atomic consistency
        symbols = list(indices.keys())
        data = yf.download(symbols, period="2d", interval="1d", group_by='ticker', progress=False)

        for sym, name in indices.items():
            try:
                ticker_data = data[sym] if len(symbols) > 1 else data
                if not ticker_data.empty and 'Close' in ticker_data.columns:
                    valid_df = ticker_data.dropna(subset=['Close'])
                    if len(valid_df) >= 1:
                        curr = float(valid_df['Close'].iloc[-1])
                        prev = float(valid_df['Close'].iloc[-2]) if len(valid_df) > 1 else curr

                        stats[name] = {
                            "value": round(curr, 2),
                            "change": round(((curr - prev) / prev * 100), 2) if prev != 0 else 0.0
                        }
            except Exception as e:
                print(f"   [!] Stats parsing error for {name}: {e}")

        return stats
    except Exception as e:
        print(f"[!] Global Market Stats Retrieval Failed: {e}")
        return stats
    except Exception as e:
        print(f"Global market stats error: {e}")
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

@router.get("/{symbol}/option-chain")
async def get_option_chain(symbol: str, expiry: Optional[str] = None):
    exp_dt = datetime.datetime.fromisoformat(expiry) if expiry else None
    return await container.provider.get_option_chain(symbol, exp_dt)

@router.get("/{symbol}/ltp")
async def get_stock_ltp(symbol: str):
    return {"symbol": symbol, "ltp": await container.provider.get_ltp(symbol)}
