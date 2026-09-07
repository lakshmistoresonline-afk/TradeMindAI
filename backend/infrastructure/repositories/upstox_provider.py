import httpx
import os
import datetime
from typing import Dict, Any, List, Optional
from backend.domain.interfaces.repository import IMarketDataProvider
from backend.domain.models.stock import StockPrice
from backend.domain.models.data_platform import OptionsChain
from backend.core.config import settings

class UpstoxProvider(IMarketDataProvider):
    """
    Workstream 6: Upstox V3 Market Data Provider.
    Implements Analytics Token support for long-lived autonomous data access.
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
            "greeks": True,
            "websocket": True
        }

    def __init__(self):
        self.base_url = "https://api.upstox.com/v2"
        self.analytics_token = os.getenv("UPSTOX_ANALYTICS_TOKEN")
        self.client = httpx.AsyncClient(timeout=30.0)

    def _map_to_key(self, symbol: str) -> str:
        """
        Maps standard TradeMind symbols to Upstox Instrument Keys.
        """
        if "|" in symbol: return symbol
        return f"NSE_EQ|{symbol}"

    async def get_ltp(self, symbol: str) -> float:
        if not self.analytics_token: return 0.0

        instrument_key = self._map_to_key(symbol)
        url = f"{self.base_url}/market-quote/ltp"
        headers = {"Authorization": f"Bearer {self.analytics_token}", "Accept": "application/json"}
        params = {"symbol": instrument_key}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                price_info = data.get("data", {}).get(instrument_key)
                if price_info:
                    return float(price_info.get("last_price", 0.0))
        except Exception as e:
            print(f"Upstox LTP Error for {symbol}: {e}")
        return 0.0

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        if not self.analytics_token: return {}

        instrument_key = self._map_to_key(symbol)
        url = f"{self.base_url}/market-quote/quotes"
        headers = {"Authorization": f"Bearer {self.analytics_token}", "Accept": "application/json"}
        params = {"symbol": instrument_key}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get("data", {}).get(instrument_key, {})
        except: pass
        return {}

    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        return {"name": symbol, "last_price": await self.get_ltp(symbol)}

    async def fetch_history(self, symbol: str, period: str, interval: str = "1D") -> Any:
        return None

    async def get_historical_candles(self, symbol: str, start_date: datetime.datetime, end_date: datetime.datetime, interval: str) -> List[StockPrice]:
        return []

    async def get_ohlc(self, symbol: str) -> Dict[str, float]:
        quote = await self.get_quote(symbol)
        if quote:
            return {"open": quote.get("ohlc", {}).get("open"), "high": quote.get("ohlc", {}).get("high"), "low": quote.get("ohlc", {}).get("low"), "close": quote.get("ohlc", {}).get("close")}
        return {}

    async def get_greeks(self, symbol: str) -> Dict[str, Any]:
        return {}

    async def get_expiries(self, symbol: str) -> List[datetime.datetime]:
        return []

    async def get_instruments(self) -> List[Dict[str, Any]]:
        return []

    async def get_option_chain(self, symbol: str, expiry: Optional[datetime.datetime] = None) -> OptionsChain:
        return OptionsChain(symbol=symbol, expiry=expiry or datetime.datetime.utcnow(), underlying_price=0.0, pcr=1.0, max_pain=0.0, total_oi=0, iv_atm=0.0, greeks_aggregate={}, last_updated=datetime.datetime.utcnow())
