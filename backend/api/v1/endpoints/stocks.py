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
    Hardened Market Index Fetcher (Institutional V2.3).
    Returns value, source, provider_timestamp, and canonical freshness.
    """
    from backend.services.market_data_service import MarketDataService
    from backend.services.freshness_policy import FreshnessPolicy
    from yahooquery import Ticker as YQTicker

    market_state = await MarketDataService.get_market_state()

    indices = {
        "^NSEI": "NIFTY 50",
        "^CNX100": "NIFTY 100",
        "^CNX200": "NIFTY 200",
        "^INDIAVIX": "India VIX"
    }
    stats = {}
    now = datetime.datetime.now(datetime.timezone.utc)

    # Initialize with truthful nulls
    for name in indices.values():
        stats[name] = {
            "value": None, "change": None, "source": "YAHOO_QUERY",
            "provider_timestamp": None, "received_at": now.isoformat(),
            "freshness": "UNAVAILABLE", "status": "UNAVAILABLE"
        }

    # 1. Integrate VIX from authorative state
    vix_val = market_state.get("vix")
    obs_ts = market_state.get("observation_timestamp")
    stats["India VIX"].update({
        "value": vix_val,
        "provider_timestamp": obs_ts,
        "freshness": market_state.get("freshness", "UNAVAILABLE"),
        "status": market_state.get("status", "UNAVAILABLE")
    })

    try:
        symbols = " ".join(indices.keys())
        yq = YQTicker(symbols)
        data = yq.history(period="2d")

        if not data.empty:
            for sym, name in indices.items():
                try:
                    if sym in data.index.get_level_values('symbol'):
                        ticker_data = data.xs(sym, level='symbol')
                        if not ticker_data.empty and 'close' in ticker_data.columns:
                            valid_df = ticker_data.dropna(subset=['close'])
                            if len(valid_df) >= 1:
                                curr = float(valid_df['close'].iloc[-1])
                                prev = float(valid_df['close'].iloc[-2]) if len(valid_df) > 1 else None

                                # Resolve timestamp
                                ts_raw = valid_df.index[-1]
                                if hasattr(ts_raw, 'to_pydatetime'): ts_raw = ts_raw.to_pydatetime()
                                if ts_raw.tzinfo is None: ts_raw = ts_raw.replace(tzinfo=datetime.timezone.utc)

                                stats[name].update({
                                    "value": round(curr, 2),
                                    "change": round(((curr - prev) / prev * 100), 2) if prev else None,
                                    "provider_timestamp": ts_raw.isoformat(),
                                    "freshness": FreshnessPolicy.get_status(ts_raw),
                                    "status": "HEALTHY"
                                })
                except: pass

        return stats
    except Exception as e:
        print(f"[!] Global Market Stats Retrieval Failed: {e}")
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
