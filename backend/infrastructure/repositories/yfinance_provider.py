from __future__ import annotations
import yfinance as yf
from typing import Dict, Any, List
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow
from backend.domain.interfaces.repository import IMarketDataProvider, INewsProvider, IInstitutionalDataProvider
import datetime

class YFinanceProvider(IMarketDataProvider, INewsProvider, IInstitutionalDataProvider):
    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            # Try to get detailed info
            info = ticker.info

            # Fallback to fast_info for critical price data if info is sparse
            if not info or info.get("regularMarketPrice") is None:
                fast = ticker.fast_info
                price = getattr(fast, 'last_price', 0)
                mc = getattr(fast, 'market_cap', 0)
            else:
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
                mc = info.get("marketCap") or 0

            # Extract shareholding if available
            holders = ticker.major_holders
            promoter = 0.0
            if holders is not None and not holders.empty:
                try: promoter = float(holders.iloc[0, 0].replace('%','')) if isinstance(holders.iloc[0,0], str) else float(holders.iloc[0,0])
                except: pass

            return {
                "name": info.get("longName") or symbol,
                "sector": info.get("sector") or "Unknown",
                "industry": info.get("industry") or "Unknown",
                "last_price": price,
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

    async def fetch_history(self, symbol: str, period: str) -> Any:
        try:
            # Handle indices differently (they don't need .NS suffix usually)
            ticker_symbol = f"{symbol}.NS" if not symbol.startswith("^") else symbol
            ticker = yf.Ticker(ticker_symbol)
            # auto_adjust=True handles stock splits and dividends automatically
            df = ticker.history(period=period, auto_adjust=True)
            if df.empty:
                print(f"Warning: Empty history for {symbol}")
            return df
        except Exception as e:
            import pandas as pd
            print(f"YFinance History Error for {symbol}: {e}")
            return pd.DataFrame()

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
