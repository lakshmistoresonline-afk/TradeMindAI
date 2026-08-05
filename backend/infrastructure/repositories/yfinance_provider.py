import yfinance as yf
from typing import Dict, Any, List
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow
from backend.domain.interfaces.repository import IMarketDataProvider, INewsProvider, IInstitutionalDataProvider
import datetime

class YFinanceProvider(IMarketDataProvider, INewsProvider, IInstitutionalDataProvider):
    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        return {
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "last_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "pe_ratio": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "peg_ratio": info.get("pegRatio"),
            "roe": info.get("returnOnEquity"),
            "roce": info.get("returnOnAssets"), # ROCE not directly in basic info, using ROA as proxy or need more calcs
            "eps": info.get("forwardEps"),
            "debt_to_equity": info.get("debtToEquity"),
            "book_value": info.get("bookValue"),
            "dividend_yield": info.get("dividendYield"),
            "face_value": info.get("faceValue"),
            "high_52w": info.get("fiftyTwoWeekHigh"),
            "low_52w": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
        }

    async def fetch_history(self, symbol: str, period: str) -> Any:
        ticker = yf.Ticker(f"{symbol}.NS")
        # auto_adjust=True handles stock splits and dividends automatically
        return ticker.history(period=period, auto_adjust=True)

    async def fetch_latest_news(self, symbol: str) -> List[NewsArticle]:
        ticker = yf.Ticker(f"{symbol}.NS")
        news = ticker.news
        articles = []
        for item in news:
            articles.append(NewsArticle(
                id=item["uuid"],
                symbol=symbol,
                title=item["title"],
                url=item["link"],
                source=item["publisher"],
                published_at=datetime.datetime.fromtimestamp(item["providerPublishTime"]),
                content=item.get("summary", "")
            ))
        return articles

    async def fetch_daily_flow(self) -> InstitutionalFlow:
        # Placeholder: FII/DII data isn't directly available in yfinance OHLC.
        # In a real enterprise app, we would scrape the NSE India website
        # or use a provider like Refinitiv.
        return InstitutionalFlow(
            date=datetime.datetime.utcnow(),
            fii_net=1200.50, # Mock data
            dii_net=-450.20,
            market_sentiment="Bullish"
        )
