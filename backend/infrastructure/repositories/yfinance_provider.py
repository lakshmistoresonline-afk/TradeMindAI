import yfinance as yf
from typing import Dict, Any
from backend.domain.interfaces.repository import IMarketDataProvider

class YFinanceProvider(IMarketDataProvider):
    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        return {
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "last_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
        }

    async def fetch_history(self, symbol: str, period: str) -> Any:
        ticker = yf.Ticker(f"{symbol}.NS")
        # auto_adjust=True handles stock splits and dividends automatically
        return ticker.history(period=period, auto_adjust=True)
