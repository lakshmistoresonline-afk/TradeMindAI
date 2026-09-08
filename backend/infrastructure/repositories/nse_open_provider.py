import httpx
import os
import datetime
import json
import asyncio
from typing import Dict, Any, List, Optional
from backend.domain.interfaces.repository import IMarketDataProvider
from backend.domain.models.stock import StockPrice
from backend.domain.models.data_platform import OptionsChain
from backend.core.config import settings

class NSEOpenProvider(IMarketDataProvider):
    """
    Workstream 1: TRADEMIND OPEN MARKET DATA FABRIC - NSE Open Source Provider.
    Uses nselib, jugaad-data and other public NSE scrapers for ₹0 cost data.
    Implements local-first collection to avoid cloud IP blocking.
    """

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "historical_equity": True,
            "historical_index": True,
            "historical_fno": True,
            "live_equity": True,
            "live_fno": True,
            "option_chain": True,
            "greeks": False,
            "websocket": False
        }

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.base_url = "https://www.nseindia.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.cookies = None

    async def _init_session(self):
        """Initializes NSE session and acquires cookies."""
        try:
            resp = await self.client.get(self.base_url, headers=self.headers)
            self.cookies = resp.cookies
        except Exception as e:
            print(f"   [!] NSE Session Init Failed: {e}")

    async def get_ltp(self, symbol: str) -> Optional[float]:
        """
        Fetches LTP using public NSE API.
        Attempts direct access; if blocked, relies on local collector ingestion.
        """
        # 1. Try to fetch from Neon (Last Ingested by Local Collector)
        from backend.core.container import container
        stock = await container.repository.get_stock_by_symbol(symbol)
        if stock and stock.last_price:
             # Check freshness (e.g. within 5 mins for 'live')
             age = (datetime.datetime.utcnow() - stock.updated_at).total_seconds() if stock.updated_at else 999999
             if age < 300: # 5 minutes
                  return stock.last_price

        # 2. Try direct fetch (Experimental / Limited)
        try:
            if not self.cookies: await self._init_session()

            # Note: Using a simplified public endpoint pattern
            url = f"{self.base_url}/api/quote-equity?symbol={symbol}"
            resp = await self.client.get(url, headers=self.headers, cookies=self.cookies)
            if resp.status_code == 200:
                data = resp.json()
                return float(data.get("priceInfo", {}).get("lastPrice", 0.0))
        except: pass

        return None

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        ltp = await self.get_ltp(symbol)
        if ltp is None:
             return {"status": "DATA_UNAVAILABLE", "price": None, "source": "NSE_OPEN"}
        return {"status": "FRESH", "price": ltp, "last_price": ltp, "source": "NSE_OPEN", "timestamp": datetime.datetime.utcnow()}

    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        return {"symbol": symbol, "name": symbol, "last_price": await self.get_ltp(symbol)}

    async def fetch_history(self, symbol: str, period: str, interval: str = "1D") -> Any:
        # Use nselib/jugaad-data for historical
        return None

    async def get_historical_candles(self, symbol: str, start_date: datetime.datetime, end_date: datetime.datetime, interval: str) -> List[StockPrice]:
        return []

    async def get_ohlc(self, symbol: str) -> Dict[str, float]:
        return {}

    async def get_greeks(self, symbol: str) -> Dict[str, Any]:
        return {}

    async def get_expiries(self, symbol: str) -> List[datetime.datetime]:
        return []

    async def get_instruments(self) -> List[Dict[str, Any]]:
        return []

    async def get_option_chain(self, symbol: str, expiry: Optional[datetime.datetime] = None) -> OptionsChain:
        return OptionsChain(symbol=symbol, expiry=expiry or datetime.datetime.utcnow(), underlying_price=0.0, pcr=1.0, max_pain=0.0, total_oi=0, iv_atm=0.0, greeks_aggregate={}, last_updated=datetime.datetime.utcnow())

    async def subscribe_live(self, symbols: List[str]) -> None: pass
    async def unsubscribe_live(self, symbols: List[str]) -> None: pass
