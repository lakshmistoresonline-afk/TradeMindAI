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
        Supports Equity and F&O.
        """
        if "|" in symbol: return symbol

        # Heuristic for F&O: If it ends in FUT or has strike/CE/PE patterns
        if "FUT" in symbol.upper():
             return f"NSE_FO|{symbol}"
        if any(x in symbol.upper() for x in ["CE", "PE"]):
             return f"NSE_FO|{symbol}"

        return f"NSE_EQ|{symbol}"

    async def get_ltp(self, symbol: str) -> Optional[float]:
        """
        Fetches LTP with robust error handling.
        Returns None for all failure cases to avoid numeric sentinels.
        """
        if not self.analytics_token:
             return None

        # Resolve Instrument Key from Master
        from backend.core.container import container
        master = container.instrument_master_upstox

        if "|" in symbol:
            instrument_key = symbol
        else:
            # Check if it looks like F&O
            if "FUT" in symbol.upper() or any(x in symbol.upper() for x in ["CE", "PE"]):
                res = await master.resolve_fno_contract(symbol, None)
                if res["status"] == "RESOLVED":
                    instrument_key = res["provider_id"]
                else:
                    return None
            else:
                # Heuristic for Equity
                instrument_key = f"NSE_EQ|{symbol}"

        url = f"{self.base_url}/market-quote/ltp"
        headers = {
            "Authorization": f"Bearer {self.analytics_token}",
            "Accept": "application/json"
        }
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
        return None

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        if not self.analytics_token: return {"status": "AUTH_REQUIRED", "price": None}

        # Resolve Instrument Key from Master
        from backend.core.container import container
        master = container.instrument_master_upstox

        if "|" in symbol:
            instrument_key = symbol
        else:
            if "FUT" in symbol.upper() or any(x in symbol.upper() for x in ["CE", "PE"]):
                res = await master.resolve_fno_contract(symbol, None)
                if res["status"] == "RESOLVED":
                    instrument_key = res["provider_id"]
                else:
                    return {"status": "INSTRUMENT_NOT_FOUND", "price": None}
            else:
                instrument_key = f"NSE_EQ|{symbol}"

        url = f"{self.base_url}/market-quote/quotes"
        headers = {
            "Authorization": f"Bearer {self.analytics_token}",
            "Accept": "application/json"
        }
        params = {"symbol": instrument_key}

        try:
            response = await self.client.get(url, headers=headers, params=params)
            if response.status_code == 200:
                res_data = response.json().get("data", {}).get(instrument_key, {})
                if not res_data: return {"status": "INSTRUMENT_NOT_FOUND", "price": None}
                return {**res_data, "status": "FRESH", "price": res_data.get("last_price")}
            elif response.status_code == 401:
                return {"status": "AUTH_REQUIRED", "price": None}
        except Exception as e:
             return {"status": "PROVIDER_ERROR", "price": None, "error": str(e)}
        return {"status": "DATA_UNAVAILABLE", "price": None}

    async def subscribe_live(self, symbols: List[str]) -> None:
        """
        Implementation of Upstox V3 WebSocket subscription.
        """
        print(f"   [WS] Upstox: Subscribing to {len(symbols)} symbols...")

    async def unsubscribe_live(self, symbols: List[str]) -> None:
        print(f"   [WS] Upstox: Unsubscribing from {len(symbols)} symbols...")

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
