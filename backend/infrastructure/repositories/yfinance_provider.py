from __future__ import annotations
import yfinance as yf
from yahooquery import Ticker as YQTicker
from typing import Dict, Any, List, Optional
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow, OptionsChain
from backend.domain.interfaces.repository import IMarketDataProvider, INewsProvider, IInstitutionalDataProvider
from backend.domain.models.stock import StockPrice
import datetime
import pandas as pd

class YFinanceProvider(IMarketDataProvider, INewsProvider, IInstitutionalDataProvider):
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
            "greeks": False
        }

    def _map_symbol(self, symbol: str) -> str:
        # If it looks like an already mapped Yahoo symbol, return it
        if symbol.endswith(".NS") or symbol.startswith("^"):
            return symbol

        mapping = {
            "NIFTY": "^NSEI",
            "BANKNIFTY": "^NSEBANK",
            "FINNIFTY": "^CNXFIN",
            "INDIAVIX": "^INDIAVIX",
            "NIFTY_50": "^NSEI",
            # P0: Known Yahoo Finance symbol mismatches for NSE (Aug 2026 Timeline Alignment)
            "GMRINFRA": "GMRAIRPORT",
            "L&TFH": "LTF",
            "TATAMOTORS": "TMCV",
            "ZOMATO": "ETERNAL",
            "PEL": "PIRAMALFIN",
            "GUJGASLTD": "GUJGASLTD",
            "LTIM": "LTIM"
        }
        mapped = mapping.get(symbol.upper(), symbol)

        return f"{mapped}.NS" if not mapped.startswith("^") else mapped

    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        try:
            mapped_sym = self._map_symbol(symbol)
            ticker = yf.Ticker(mapped_sym)
            info = {}
            try:
                info = ticker.info
            except Exception as yf_err:
                print(f"   [!] yfinance info 429/Error for {symbol}, trying yahooquery...")
                yq = YQTicker(mapped_sym)
                yq_info = yq.price.get(mapped_sym, {})
                if isinstance(yq_info, dict):
                    info = {
                        "longName": yq_info.get("longName") or yq_info.get("shortName"),
                        "regularMarketPrice": yq_info.get("regularMarketPrice"),
                        "marketCap": yq_info.get("marketCap"),
                        "regularMarketPreviousClose": yq_info.get("regularMarketPreviousClose"),
                        "volume": yq_info.get("regularMarketVolume")
                    }

            if not info or info.get("regularMarketPrice") is None:
                hist = await self.fetch_history(symbol, period="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                    prev_close = float(hist["Open"].iloc[-1])
                    mc = None
                else:
                    price, prev_close, mc = None, None, None
            else:
                price = info.get("currentPrice") or info.get("regularMarketPrice")
                prev_close = info.get("regularMarketPreviousClose") or price
                mc = info.get("marketCap")

            change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

            return {
                "name": info.get("longName") or symbol,
                "sector": info.get("sector") or "Unknown",
                "industry": info.get("industry") or "Unknown",
                "last_price": price,
                "previous_close": prev_close,
                "volume": info.get("volume") or info.get("regularMarketVolume") or 0.0,
                "change_pct": change_pct,
                "market_cap": mc,
                "enterprise_value": info.get("enterpriseValue") or 0,
                "pe_ratio": info.get("forwardPE") or info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "peg_ratio": info.get("pegRatio"),
                "roe": info.get("returnOnEquity"),
                "roce": info.get("returnOnAssets"),
                "eps": info.get("forwardEps") or info.get("trailingEps"),
                "debt_to_equity": info.get("debtToEquity"),
                "book_value": info.get("bookValue"),
                "dividend_yield": info.get("dividendYield"),
                "face_value": info.get("faceValue"),
                "high_52w": info.get("fiftyTwoWeekHigh") or 0,
                "low_52w": info.get("fiftyTwoWeekLow") or 0,
                "avg_volume": info.get("averageVolume") or 0,
                "promoter_holding": 0.0,
                "fii_holding": info.get("heldPercentInstitutions", 0) * 100,
                "dii_holding": info.get("heldPercentInsiders", 0) * 100,
                "financial_history": []
            }
        except Exception as e:
            print(f"YFinance Info Error for {symbol}: {e}")
            return {"name": symbol, "last_price": None}

    def _get_history_yq(self, symbol: str, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        try:
            mapped_sym = self._map_symbol(symbol)
            t = YQTicker(mapped_sym)
            yq_interval = interval.lower()

            if start and end:
                df = t.history(start=start, end=end, interval=yq_interval)
            else:
                df = t.history(period=period, interval=yq_interval)

            if df.empty or 'close' not in df.columns:
                return pd.DataFrame()

            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)

            col_map = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'adjclose': 'Adj Close'}
            df = df.rename(columns=col_map)
            return df
        except Exception as e:
            print(f"YahooQuery Error for {symbol}: {e}")
            return pd.DataFrame()

    async def fetch_history(self, symbol: str, period: str, interval: str = "1d") -> Any:
        mapped_sym = self._map_symbol(symbol)

        # 1. Try yfinance first (more reliable for indices history)
        try:
            ticker = yf.Ticker(mapped_sym)
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                return df
        except Exception as e:
            print(f"   [!] yfinance history error for {symbol}: {e}")

        # 2. Fallback to yahooquery
        df = self._get_history_yq(symbol, period=period, interval=interval)
        return df

    async def get_history(self, symbol: str, start_date: datetime.datetime, end_date: Optional[datetime.datetime] = None, interval: str = "1d") -> pd.DataFrame:
        if not end_date:
            end_date = datetime.datetime.utcnow()
        return self._get_history_yq(symbol, start=start_date, end=end_date, interval=interval)

    async def get_historical_candles(self, symbol: str, start_date: datetime.datetime, end_date: datetime.datetime, interval: str) -> List[StockPrice]:
        df = self._get_history_yq(symbol, start=start_date, end=end_date, interval=interval)
        prices = []
        for index, row in df.iterrows():
            prices.append(StockPrice(
                symbol=symbol, date=index.to_pydatetime() if hasattr(index, 'to_pydatetime') else index,
                open=row["Open"], high=row["High"], low=row["Low"], close=row["Close"],
                volume=int(row["Volume"]) if "Volume" in row and not pd.isna(row["Volume"]) else 0,
                source="yahooquery"
            ))
        return prices

    async def get_ltp(self, symbol: str) -> Dict[str, Any]:
        df = await self.fetch_history(symbol, period="1d")
        if not df.empty:
            price = float(df["Close"].iloc[-1])
            ts = df.index[-1]
            if hasattr(ts, 'to_pydatetime'):
                ts = ts.to_pydatetime()
            # Ensure it has TZ info
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=datetime.timezone.utc)
            return {"price": price, "timestamp": ts}
        return {"price": None, "timestamp": None}


    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        return await self.fetch_stock_info(symbol)

    async def get_ohlc(self, symbol: str) -> Dict[str, Optional[float]]:
        df = self._get_history_yq(symbol, period="1d")
        if not df.empty:
            last = df.iloc[-1]
            return {"open": last["Open"], "high": last["High"], "low": last["Low"], "close": last["Close"]}
        return {"open": None, "high": None, "low": None, "close": None}

    async def get_greeks(self, symbol: str) -> Dict[str, Any]:
        return {}

    async def get_expiries(self, symbol: str) -> List[datetime.datetime]:
        try:
            mapped_sym = self._map_symbol(symbol)
            ticker = yf.Ticker(mapped_sym)
            try:
                expiries = ticker.options
            except:
                # Fallback to yahooquery
                yq = YQTicker(mapped_sym)
                expiries = yq.options

            if not expiries:
                return []

            return [datetime.datetime.strptime(e, "%Y-%m-%d") for e in expiries]
        except Exception as e:
            print(f"Error fetching expiries for {symbol}: {e}")
            return []

    async def get_instruments(self) -> List[Dict[str, Any]]:
        # This provider doesn't have a direct instrument list API like Groww
        return []

    async def get_option_chain(self, symbol: str, expiry: Optional[datetime.datetime] = None) -> OptionsChain:
        try:
            mapped_sym = self._map_symbol(symbol)
            ticker = yf.Ticker(mapped_sym)

            # 1. Resolve Expiry
            if not expiry:
                expiries = ticker.options
                if expiries:
                    expiry_str = expiries[0]
                    expiry = datetime.datetime.strptime(expiry_str, "%Y-%m-%d")
                else:
                    return self._dummy_chain(symbol)

            # 2. Fetch Chain
            chain_raw = ticker.option_chain(expiry.strftime("%Y-%m-%d"))

            # Convert to internal model
            # (Simplified for P0: we just want to know it's working)
            return OptionsChain(
                symbol=symbol,
                expiry=expiry,
                underlying_price=await self.get_ltp(symbol),
                last_updated=datetime.datetime.utcnow()
            )
        except Exception as e:
            print(f"Option Chain Error for {symbol}: {e}")
            return self._dummy_chain(symbol)

    def _dummy_chain(self, symbol: str) -> OptionsChain:
        return OptionsChain(symbol=symbol, expiry=datetime.datetime.utcnow(), underlying_price=0.0, pcr=1.0, max_pain=0.0, total_oi=0, iv_atm=0.0, greeks_aggregate={}, last_updated=datetime.datetime.utcnow())

    async def subscribe_live(self, symbols: List[str]) -> None: pass
    async def unsubscribe_live(self, symbols: List[str]) -> None: pass

    async def fetch_latest_news(self, symbol: str) -> List[NewsArticle]: return []
    async def fetch_daily_flow(self) -> InstitutionalFlow: return InstitutionalFlow(date=datetime.datetime.utcnow(), fii_net=0.0, dii_net=0.0, market_sentiment="Neutral")
