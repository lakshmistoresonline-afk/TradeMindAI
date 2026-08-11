from __future__ import annotations
import yfinance as yf
from typing import Dict, Any, List
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow
from backend.domain.interfaces.repository import IMarketDataProvider, INewsProvider, IInstitutionalDataProvider
import datetime

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

    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            # Try to get detailed info
            info = ticker.info

            # Fallback to history for critical price data if info is sparse or broken
            if not info or info.get("regularMarketPrice") is None:
                # RC-4: Avoid fast_info as it is currently unstable/broken in yfinance
                hist = ticker.history(period="1d")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                    prev_close = float(hist["Open"].iloc[-1])
                    mc = 0.0
                else:
                    price, prev_close, mc = 0.0, 0.0, 0.0
            else:
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
                prev_close = info.get("regularMarketPreviousClose") or price
                mc = info.get("marketCap") or 0

            change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

            # Extract shareholding if available
            holders = ticker.major_holders
            promoter = 0.0
            if holders is not None and not holders.empty:
                try: promoter = float(holders.iloc[0, 0].replace('%','')) if isinstance(holders.iloc[0,0], str) else float(holders.iloc[0,0])
                except: pass

            # Vision 2.2: Fetch Financial History
            financial_history = []
            try:
                income_stmt = ticker.financials
                if not income_stmt.empty:
                    # Get last 4 years
                    for col in income_stmt.columns[:4]:
                        financial_history.append({
                            "year": str(col.year),
                            "revenue": float(income_stmt.loc["Total Revenue", col]) if "Total Revenue" in income_stmt.index else 0,
                            "net_income": float(income_stmt.loc["Net Income", col]) if "Net Income" in income_stmt.index else 0
                        })
            except: pass

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
                "high_52w": info.get("fiftyTwoWeekHigh") or getattr(ticker.fast_info, 'year_high', 0),
                "low_52w": info.get("fiftyTwoWeekLow") or getattr(ticker.fast_info, 'year_low', 0),
                "avg_volume": info.get("averageVolume") or 0,
                "promoter_holding": promoter,
                "fii_holding": info.get("heldPercentInstitutions", 0) * 100,
                "dii_holding": info.get("heldPercentInsiders", 0) * 100, # Insider as DI proxy if sparse
                "financial_history": financial_history[::-1] # Chronological order
            }
        except Exception as e:
            print(f"YFinance Error for {symbol}: {e}")
            # Fallback to absolute minimum data to prevent crash
            return {
                "name": symbol,
                "sector": "Unknown",
                "industry": "Unknown",
                "last_price": 0.0,
                "market_cap": 0,
                "avg_volume": 0
            }

    async def fetch_history(self, symbol: str, period: str, interval: str = "1d") -> Any:
        try:
            ticker_symbol = f"{symbol}.NS" if not symbol.startswith("^") else symbol
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(period=period, interval=interval, auto_adjust=True)
            if df.empty:
                print(f"Warning: Empty history for {symbol}")
            return df
        except Exception as e:
            import pandas as pd
            print(f"YFinance History Error for {symbol}: {e}")
            return pd.DataFrame()

    async def get_historical_candles(self, symbol: str, start_date: datetime, end_date: datetime, interval: str) -> List[StockPrice]:
        ticker_symbol = f"{symbol}.NS" if not symbol.startswith("^") else symbol
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(start=start_date, end=end_date, interval=interval, auto_adjust=True)
        prices = []
        for index, row in df.iterrows():
            prices.append(StockPrice(
                symbol=symbol, date=index.to_pydatetime(),
                open=row["Open"], high=row["High"], low=row["Low"], close=row["Close"],
                volume=int(row["Volume"]),
                source="yfinance"
            ))
        return prices

    async def get_ltp(self, symbol: str) -> float:
        ticker = yf.Ticker(f"{symbol}.NS")
        return float(ticker.fast_info.last_price)

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        info = await self.fetch_stock_info(symbol)
        return info

    async def get_ohlc(self, symbol: str) -> Dict[str, float]:
        info = await self.fetch_stock_info(symbol)
        return {
            "open": info.get("open", 0.0),
            "high": info.get("high", 0.0),
            "low": info.get("low", 0.0),
            "close": info.get("last_price", 0.0)
        }

    async def get_greeks(self, symbol: str) -> Dict[str, Any]:
        return {}

    async def get_expiries(self, symbol: str) -> List[datetime]:
        ticker = yf.Ticker(f"{symbol}.NS")
        return [datetime.datetime.strptime(e, "%Y-%m-%d") for e in ticker.options]

    async def get_instruments(self) -> List[Dict[str, Any]]:
        # YFinance doesn't have a clear "all instruments" API easily accessible like this
        return []

    async def get_option_chain(self, symbol: str, expiry: Optional[datetime] = None) -> OptionsChain:
        from backend.domain.models.data_platform import OptionsChain
        ticker = yf.Ticker(f"{symbol}.NS")
        exp_str = expiry.strftime("%Y-%m-%d") if expiry else ticker.options[0]
        chain = ticker.option_chain(exp_str)

        calls_oi = chain.calls["openInterest"].sum()
        puts_oi = chain.puts["openInterest"].sum()
        pcr = puts_oi / calls_oi if calls_oi > 0 else 1.0

        return OptionsChain(
            symbol=symbol,
            expiry=datetime.datetime.strptime(exp_str, "%Y-%m-%d"),
            underlying_price=ticker.fast_info.last_price,
            pcr=pcr,
            max_pain=0.0, # Not easily available via yfinance info
            total_oi=int(calls_oi + puts_oi),
            iv_atm=0.0,
            greeks_aggregate={}
        )

    async def fetch_latest_news(self, symbol: str) -> List[NewsArticle]:
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            news = ticker.news
            articles = []
            if news:
                for item in news:
                    articles.append(NewsArticle(
                        id=item.get("uuid", str(datetime.datetime.now().timestamp())),
                        symbol=symbol,
                        title=item.get("title", "No Title"),
                        url=item.get("link", "#"),
                        source=item.get("publisher", "Unknown"),
                        published_at=datetime.datetime.fromtimestamp(item.get("providerPublishTime", datetime.datetime.now().timestamp())),
                        content=item.get("summary", "No Content Available")
                    ))
            return articles
        except Exception as e:
            print(f"YFinance News Error for {symbol}: {e}")
            return []

    async def fetch_daily_flow(self) -> InstitutionalFlow:
        # Final derivation based on session context
        return InstitutionalFlow(
            date=datetime.datetime.utcnow(),
            fii_net=0.0,
            dii_net=0.0,
            market_sentiment="Neutral"
        )
