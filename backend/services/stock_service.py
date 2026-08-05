from typing import List, Dict, Any
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider
from backend.domain.models.stock import Stock, StockPrice
import pandas as pd

class StockService:
    def __init__(self, repository: IStockRepository, provider: IMarketDataProvider):
        self.repository = repository
        self.provider = provider

    async def collect_stock_data(self, symbol: str, period: str = "10y") -> Stock:
        # 1. Check existing record
        existing_stock = await self.repository.get_stock_by_symbol(symbol)

        # 2. Fetch from Market
        info = await self.provider.fetch_stock_info(symbol)

        # Incremental Logic:
        # If we already have data, just fetch the last month to ensure we bridge the gap.
        # Otherwise, fetch the full period.
        fetch_period = "1mo" if existing_stock and existing_stock.updated_at else period
        history_df = await self.provider.fetch_history(symbol, fetch_period)

        # 3. Map to Domain
        stock = Stock(symbol=symbol, **info)

        prices = []
        for index, row in history_df.iterrows():
            prices.append(StockPrice(
                symbol=symbol,
                date=index.to_pydatetime(),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"])
            ))

        # 3. Persist
        await self.repository.save_stock(stock)
        await self.repository.save_historical_prices(symbol, prices)

        return stock

    async def get_market_overview(self) -> List[Stock]:
        return await self.repository.get_all_stocks()
