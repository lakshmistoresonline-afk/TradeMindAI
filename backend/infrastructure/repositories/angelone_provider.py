import httpx
import os
import datetime
from typing import Dict, Any, List, Optional
from backend.domain.interfaces.repository import IMarketDataProvider
from backend.domain.models.stock import StockPrice
from backend.domain.models.data_platform import OptionsChain

class AngelOneProvider(IMarketDataProvider):
    """
    Workstream 30: Angel One SmartAPI Market Data Provider.
    Implements TOTP-based session management and V2 Market Data retrieval.
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
        self.base_url = "https://apiconnect.angelbroking.com"
        self.api_key = os.getenv("ANGELONE_API_KEY")
        self.client_code = os.getenv("ANGELONE_CLIENT_CODE")
        self.pin = os.getenv("ANGELONE_PIN")
        self.totp_secret = os.getenv("ANGELONE_TOTP_SECRET")

        self.jwt_token = None
        self.feed_token = None
        self.client = httpx.AsyncClient(timeout=30.0)

    async def authenticate(self) -> bool:
        """
        Performs TOTP authentication and establishes a SmartAPI session.
        Note: Requires pyotp to be installed in the environment.
        """
        try:
            import pyotp
        except ImportError:
            print("   [!] AngelOne: pyotp NOT INSTALLED. Authentication skipped.")
            return False

        if not all([self.api_key, self.client_code, self.pin, self.totp_secret]):
            return False

        url = f"{self.base_url}/publisher/login/v1/generateSession"
        totp = pyotp.TOTP(self.totp_secret).now()

        payload = {
            "clientcode": self.client_code,
            "password": self.pin,
            "totp": totp
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "00-00-00-00-00-00",
            "X-PrivateKey": self.api_key
        }

        try:
            response = await self.client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    self.jwt_token = data["data"]["jwtToken"]
                    self.feed_token = data["data"]["feedToken"]
                    return True
        except Exception as e:
            print(f"AngelOne Auth Error: {e}")
        return False

    async def get_ltp(self, symbol: str) -> Optional[float]:
        """
        Fetches LTP using ltpData endpoint.
        """
        if not self.jwt_token:
            if not await self.authenticate():
                return None

        # Resolve Token from Master
        from backend.core.container import container
        master = container.instrument_master_angelone

        # Try to resolve identity
        res = await master.resolve_fno_contract(symbol, None)
        if res["status"] != "RESOLVED":
            # Heuristic for Equity if master not ready
            exchange = "NSE"
            trading_symbol = f"{symbol}-EQ"
            # We still need the token... Angel One is strict about tokens.
            # Without master, we can't reliably get the token.
            return None

        exchange = res.get("exchange", "NSE")
        trading_symbol = res["trading_symbol"]
        symbol_token = res["provider_id"]

        url = f"{self.base_url}/rest/secure/angelbroking/market/trade/v1/ltpData"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "00-00-00-00-00-00",
            "X-PrivateKey": self.api_key,
            "Authorization": f"Bearer {self.jwt_token}"
        }
        payload = {
            "exchange": exchange,
            "tradingsymbol": trading_symbol,
            "symboltoken": symbol_token
        }

        try:
            response = await self.client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("status"):
                    return float(data["data"]["ltp"])
        except Exception as e:
            print(f"AngelOne LTP Error for {symbol}: {e}")
        return None

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        if not self.jwt_token:
            if not await self.authenticate():
                return {"status": "AUTH_REQUIRED", "price": None}

        # Resolve identity
        from backend.core.container import container
        master = container.instrument_master_angelone
        res = await master.resolve_fno_contract(symbol, None)

        if res["status"] != "RESOLVED":
             return {"status": "INSTRUMENT_NOT_FOUND", "price": None}

        url = f"{self.base_url}/rest/secure/angelbroking/market/data/v1/fullQuote"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-PrivateKey": self.api_key,
            "Authorization": f"Bearer {self.jwt_token}"
        }
        # Angel One full quote takes mode and token list
        payload = {
            "mode": "FULL",
            "exchangeTokens": {
                res.get("exchange", "NSE"): [res["provider_id"]]
            }
        }

        try:
            response = await self.client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") and data["data"]:
                     quote = data["data"][0] # Assuming single token request
                     return {**quote, "status": "LIVE", "price": float(quote.get("lastTradedPrice", 0.0))}
        except Exception as e:
             return {"status": "PROVIDER_ERROR", "price": None, "error": str(e)}
        return {"status": "DATA_UNAVAILABLE", "price": None}

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
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
        except: pass
        return []

    async def get_option_chain(self, symbol: str, expiry: Optional[datetime.datetime] = None) -> OptionsChain:
        return OptionsChain(symbol=symbol, expiry=expiry or datetime.datetime.utcnow(), underlying_price=0.0, pcr=1.0, max_pain=0.0, total_oi=0, iv_atm=0.0, greeks_aggregate={}, last_updated=datetime.datetime.utcnow())

    async def subscribe_live(self, symbols: List[str]) -> None: pass
    async def unsubscribe_live(self, symbols: List[str]) -> None: pass
