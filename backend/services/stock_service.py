from __future__ import annotations
from typing import List, Dict, Any
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider, INewsProvider, IInstitutionalDataProvider
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow
from datetime import datetime
import gc

class StockService:
    def __init__(self, repository: IStockRepository, provider: IMarketDataProvider, news_provider: INewsProvider, inst_provider: IInstitutionalDataProvider):
        self.repository = repository
        self.provider = provider
        self.news_provider = news_provider
        self.inst_provider = inst_provider

    async def collect_stock_data(self, symbol: str, period: str = "10y") -> Stock:
        # 1. Sync Base Data
        existing_stock = await self.repository.get_stock_by_symbol(symbol)
        info = await self.provider.fetch_stock_info(symbol)

        is_initial_load = not (existing_stock and existing_stock.updated_at)
        fetch_period = period if is_initial_load else "1mo"
        history_df = await self.provider.fetch_history(symbol, fetch_period)

        if history_df.empty:
            print(f"No history found for {symbol}. Skipping detailed analysis.")
            return Stock(symbol=symbol, **info)

        # 2. Sync News (Vision 2.0)
        from backend.core.container import container
        try:
            news = await self.news_provider.fetch_latest_news(symbol)
            if news:
                await container.data_platform_repo.save_news(news)
        except: pass

        # 3. Map to Domain & Persist
        stock = Stock(symbol=symbol, **info)
        await self.repository.save_stock(stock)

        # 4. Sync Earnings (Vision 2.0)
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.NS")
            calendar = ticker.calendar
            if calendar is not None and not calendar.empty:
                from backend.domain.models.data_platform import EarningsData
                # Convert timestamp to datetime
                earning_date = calendar.iloc[0, 0] if hasattr(calendar, 'iloc') else datetime.utcnow()
                earnings = EarningsData(
                    symbol=symbol,
                    date=earning_date,
                    eps_actual=0.0, # Will be updated after results
                    eps_estimate=info.get("forwardEps", 0.0),
                    revenue_actual=0.0,
                    revenue_estimate=0.0
                )
                await container.data_platform_repo.save_earnings(earnings)
        except: pass

        if is_initial_load:
            # Memory Optimization: For initial 10Y load, we save everything but only
            # calculate complex indicators for the most recent 2 years.
            from backend.analysis.technical import TechnicalAnalysis

            # A. Process Full History (Raw Price Data)
            raw_prices = []
            for index, row in history_df.iterrows():
                raw_prices.append(StockPrice(
                    symbol=symbol, date=index.to_pydatetime(),
                    open=row["Open"], high=row["High"], low=row["Low"], close=row["Close"],
                    volume=int(row["Volume"])
                ))

            # Batch save raw prices first
            await self.repository.save_historical_prices(symbol, raw_prices)
            del raw_prices
            gc.collect()

            # B. Calculate Indicators for Recent 2 Years (Approx 500 trading days)
            recent_df = history_df.tail(600) # Buffer for long EMAs
            df_ta = TechnicalAnalysis.calculate_indicators(recent_df)

            ta_prices = []
            for index, row in df_ta.tail(500).iterrows():
                indicator_keys = ["EMA_20", "EMA_50", "EMA_200", "RSI", "MACD_12_26_9", "Pivot"]
                indicators = {k: row[k] for k in indicator_keys if k in row}

                ta_prices.append(StockPrice(
                    symbol=symbol, date=index.to_pydatetime(),
                    open=row["Open"], high=row["High"], low=row["Low"], close=row["Close"],
                    volume=int(row["Volume"]),
                    indicators=indicators
                ))

            # Update specific docs with indicators
            await self.repository.save_historical_prices(symbol, ta_prices)
            del ta_prices, df_ta
        else:
            await self.sync_incremental_prices(symbol, history_df)

        gc.collect()
        return stock

    async def sync_incremental_prices(self, symbol: str, new_history_df: Any):
        for index, row in new_history_df.iterrows():
            price = StockPrice(
                symbol=symbol,
                date=index.to_pydatetime(),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"])
            )
            await self.repository.save_historical_prices(symbol, [price])

    async def get_market_overview(self, limit: int = 50, offset: int = 0) -> List[Stock]:
        return await self.repository.get_all_stocks(limit, offset)

    async def validate_data_quality(self, symbol: str, df: Any) -> Dict[str, Any]:
        import pandas as pd
        report = {"symbol": symbol, "timestamp": datetime.now(), "status": "passed", "issues": []}
        if df.isnull().values.any():
            report["status"] = "failed"
            report["issues"].append("Missing OHLCV data found")
        return report
