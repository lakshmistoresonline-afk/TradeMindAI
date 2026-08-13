import httpx
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.domain.interfaces.repository import IMarketDataProvider
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.models.data_platform import OptionsChain
from backend.core.config import settings

class GrowwProvider(IMarketDataProvider):
    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "historical_equity": True,
            "historical_index": True,
            "historical_fno": True,
            "historical_commodity": False,
            "live_equity": True,
            "live_fno": True,
            "option_chain": True,
            "greeks": True
        }

    def __init__(self):
        self.base_url = settings.GROWW_BASE_URL
        self.api_key = settings.GROWW_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches basic stock information using Groww's live quote.
        """
        groww_symbol = f"NSE-{symbol}"
        url = f"{self.base_url}/live/quote"
        params = {"symbol": groww_symbol}
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        response = await self.client.get(url, params=params, headers=headers)
        if response.status_code != 200:
            return {"name": symbol, "last_price": 0.0}

        data = response.json()
        return {
            "name": data.get("companyName", symbol),
            "last_price": data.get("ltp", 0.0),
            "previous_close": data.get("prevClose", 0.0),
            "change_pct": data.get("dayChangePerc", 0.0),
            "market_cap": data.get("marketCap", 0.0),
            "volume": data.get("volume", 0.0)
        }

    async def fetch_history(self, symbol: str, period: str, interval: str = "1D") -> Any:
        """
        Fetches historical data for a period.
        Supports: 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y
        """
        # Convert period to start/end dates
        end_date = datetime.utcnow()

        # Robust period parsing
        import re
        match = re.match(r"(\d+)(\w+)", period)
        if match:
            val, unit = int(match.group(1)), match.group(2)
            if unit == "mo": start_date = end_date - timedelta(days=val * 30)
            elif unit == "y": start_date = end_date - timedelta(days=val * 365)
            elif unit == "d": start_date = end_date - timedelta(days=val)
            else: start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=30)

        prices = await self.get_historical_candles(symbol, start_date, end_date, interval)
        if not prices:
            return pd.DataFrame()

        df = pd.DataFrame([p.model_dump() for p in prices])
        df.set_index('date', inplace=True)
        # Rename columns to match existing TradeMind expectation (Capitalized)
        df.columns = [c.capitalize() for c in df.columns]
        return df

    async def get_historical_candles(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str
    ) -> List[StockPrice]:
        """
        Fetches historical candles with auto-chunking based on Groww limits.
        """
        groww_symbol = self._map_to_groww_symbol(symbol)
        url = f"{self.base_url}/historical/candles"
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        limit_days = self._get_interval_limit_days(interval)
        all_prices = []

        current_start = start_date
        while current_start < end_date:
            current_end = min(current_start + timedelta(days=limit_days), end_date)

            params = {
                "symbol": groww_symbol,
                "interval": interval,
                "startTime": int(current_start.timestamp() * 1000),
                "endTime": int(current_end.timestamp() * 1000)
            }

            try:
                response = await self.client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    for c in data.get("candles", []):
                        # Format: [timestamp, open, high, low, close, volume, oi]
                        ts = datetime.fromtimestamp(c[0] / 1000.0)
                        all_prices.append(StockPrice(
                            symbol=symbol,
                            date=ts,
                            open=float(c[1]),
                            high=float(c[2]),
                            low=float(c[3]),
                            close=float(c[4]),
                            volume=int(c[5]),
                            open_interest=int(c[6]) if len(c) > 6 else 0,
                            source="groww"
                        ))
            except Exception as e:
                print(f"Error fetching Groww historical for {symbol}: {e}")

            current_start = current_end + timedelta(milliseconds=1)

        return all_prices

    async def get_ltp(self, symbol: str) -> float:
        info = await self.fetch_stock_info(symbol)
        return info.get("last_price", 0.0)

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        return await self.fetch_stock_info(symbol)

    async def get_expiries(self, symbol: str) -> List[datetime]:
        """
        Discovers expiries for F&O.
        """
        url = f"{self.base_url}/historical/expiries"
        params = {"symbol": self._map_to_groww_symbol(symbol)}
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        response = await self.client.get(url, params=params, headers=headers)
        if response.status_code != 200:
            return []

        data = response.json()
        return [datetime.fromtimestamp(e / 1000.0) for e in data.get("expiries", [])]

    async def get_instruments(self) -> List[Dict[str, Any]]:
        """
        Syncs all instruments from Groww.
        """
        url = f"{self.base_url}/instruments/all"
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        try:
            response = await self.client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("instruments", [])
        except Exception as e:
            print(f"Error fetching Groww instruments: {e}")
        return []

    async def get_contracts(self, underlying: str, expiry: datetime) -> List[Dict[str, Any]]:
        """
        Discovers contracts for a given underlying and expiry.
        """
        url = f"{self.base_url}/historical/contracts"
        params = {
            "underlying": self._map_to_groww_symbol(underlying),
            "expiry": int(expiry.timestamp() * 1000)
        }
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        try:
            response = await self.client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json().get("contracts", [])
        except Exception as e:
            print(f"Error fetching Groww contracts: {e}")
        return []

    async def get_ohlc(self, symbol: str) -> Dict[str, float]:
        """
        Fetches live OHLC snapshot.
        """
        url = f"{self.base_url}/live/ohlc"
        params = {"symbol": self._map_to_groww_symbol(symbol)}
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        try:
            response = await self.client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
        except: pass
        return {}

    async def get_greeks(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches Greeks for an option.
        """
        url = f"{self.base_url}/live/greeks"
        params = {"symbol": symbol}
        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        try:
            response = await self.client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
        except: pass
        return {}

    async def get_option_chain(self, symbol: str, expiry: Optional[datetime] = None) -> OptionsChain:
        """
        Vision 2.2: Professional Option Chain discovery via Groww.
        """
        groww_symbol = self._map_to_groww_symbol(symbol)
        url = f"{self.base_url}/live/option-chain"
        params = {"symbol": groww_symbol}
        if expiry: params["expiry"] = int(expiry.timestamp() * 1000)

        headers = {"X-API-KEY": self.api_key} if self.api_key else {}

        try:
            response = await self.client.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Aggregate Greeks for overall sentiment
                aggr = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
                total_strikes = len(data.get("strikes", []))

                if total_strikes > 0:
                    for s in data["strikes"]:
                        # Average of ATM/Near-ATM Greeks
                        aggr["delta"] += (s.get("call_greeks", {}).get("delta", 0) + s.get("put_greeks", {}).get("delta", 0)) / 2

                    for k in aggr: aggr[k] = round(aggr[k] / total_strikes, 4)

                return OptionsChain(
                    symbol=symbol,
                    expiry=expiry or datetime.utcnow(),
                    underlying_price=data.get("underlyingPrice", 0.0),
                    pcr=float(data.get("pcr", 1.0)),
                    max_pain=float(data.get("maxPain", 0.0)),
                    total_oi=int(data.get("totalOI", 0)),
                    iv_atm=float(data.get("atmIV", 0.0)),
                    greeks_aggregate=aggr,
                    last_updated=datetime.utcnow()
                )
        except Exception as e:
            print(f"Option Chain Error for {symbol}: {e}")

        return OptionsChain(
            symbol=symbol,
            expiry=expiry or datetime.utcnow(),
            underlying_price=await self.get_ltp(symbol),
            pcr=1.0,
            max_pain=0.0,
            total_oi=0,
            iv_atm=0.0,
            greeks_aggregate={},
            last_updated=datetime.utcnow()
        )

    def _map_to_groww_symbol(self, symbol: str) -> str:
        # Predefined mappings for common indices
        mapping = {
            "NIFTY": "NIFTY", # Groww index format
            "BANKNIFTY": "BANKNIFTY",
            "FINNIFTY": "FINNIFTY",
            "^NSEI": "NIFTY",
            "^NSEBANK": "BANKNIFTY",
            "INDIAVIX": "INDIAVIX",
            "^INDIAVIX": "INDIAVIX"
        }
        if symbol in mapping: return mapping[symbol]
        }
        if symbol in mapping: return mapping[symbol]

        # Heuristic for Equities
        if "-" in symbol: return symbol # Already mapped?
        return f"NSE-{symbol}"

    def _get_interval_limit_days(self, interval: str) -> int:
        if interval in ["1m", "2m", "3m", "5m"]: return 30
        if interval in ["10m", "15m", "30m"]: return 90
        if interval in ["1h", "4h", "1D", "1W", "1M"]: return 180
        return 30
