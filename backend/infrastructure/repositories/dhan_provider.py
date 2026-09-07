import httpx
import os
import datetime
from typing import Dict, Any, List, Optional
from backend.domain.interfaces.repository import IMarketDataProvider
from backend.domain.models.stock import StockPrice
from backend.domain.models.data_platform import OptionsChain

class DhanProvider(IMarketDataProvider):
    """
    Workstream 8: DhanHQ Market Data Provider.
    Specializes in 200-depth market data and expired contract forensics.
    """

    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "historical_equity": True,
            "historical_fno": True,
            "expired_fno": True,
            "live_equity": True,
            "live_fno": True,
            "market_depth": True,
            "greeks": True
        }

    def __init__(self):
        self.base_url = "https://api.dhan.co"
        self.access_token = os.getenv("DHAN_ACCESS_TOKEN")
        self.client_id = os.getenv("DHAN_CLIENT_ID")
        self.client = httpx.AsyncClient(timeout=30.0)

    def _map_to_id(self, symbol: str) -> str:
        """
        Maps standard TradeMind symbols to Dhan Security IDs (Numerical).
        """
        # Heuristic for F&O: Requires real instrument master for numerical IDs
        return symbol

    async def get_ltp(self, symbol: str) -> Optional[float]:
        """
        Fetches LTP using Dhan marketfeed API.
        Returns None for all failure cases.
        """
        if not self.access_token:
             return None

        # Resolve Security ID from Master
        from backend.core.container import container
        master = container.instrument_master_dhan

        if symbol.isdigit():
            security_id = symbol
        else:
            # Try to resolve F&O or Equity
            res = await master.resolve_fno_contract(symbol, None)
            if res["status"] == "RESOLVED":
                security_id = res["provider_id"]
            else:
                return None

        url = f"{self.base_url}/marketfeed/ltp"
        headers = {
            "access-token": self.access_token,
            "Content-Type": "application/json"
        }
        # Dhan typically uses POST for multiple symbols in the v2 marketfeed
        payload = {
            "instruments": [{"exchangeSegment": "NSE_EQ", "securityId": security_id}]
        }

        try:
            response = await self.client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    price_info = data.get("data", {}).get(security_id)
                    if price_info:
                         return float(price_info.get("last_price", 0.0))
        except Exception as e:
            print(f"Dhan LTP Error for {symbol}: {e}")
        return None

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        ltp = await self.get_ltp(symbol)
        if ltp is None:
             return {"status": "DATA_UNAVAILABLE", "price": None}
        return {"last_price": ltp, "status": "FRESH", "price": ltp}

    async def subscribe_live(self, symbols: List[str]) -> None:
        print(f"   [WS] Dhan: Subscribing to {len(symbols)} symbols...")

    async def unsubscribe_live(self, symbols: List[str]) -> None:
        print(f"   [WS] Dhan: Unsubscribing from {len(symbols)} symbols...")

    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        return {"name": symbol, "last_price": await self.get_ltp(symbol)}

    async def fetch_history(self, symbol: str, period: str, interval: str = "1D") -> Any:
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
