from __future__ import annotations
from typing import List, Dict, Any
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider, INewsProvider, IInstitutionalDataProvider
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow
from datetime import datetime

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

        # Vision 2.0: Dynamic Price Refresh
        last_price = info.get("last_price", 0.0)

        is_initial_load = not (existing_stock and existing_stock.updated_at)
        fetch_period = period if is_initial_load else "1mo"
        history_df = await self.provider.fetch_history(symbol, fetch_period)

        # 2. Sync News (Vision 2.0)
        from backend.core.container import container
        news = await self.news_provider.fetch_latest_news(symbol)
        if news:
            await container.data_platform_repo.save_news(news)

        # 3. Map to Domain & Persist
        stock = Stock(symbol=symbol, **info)
        await self.repository.save_stock(stock)

        if is_initial_load:
            # For initial load, we process the full history into the database
            from backend.analysis.technical import TechnicalAnalysis
            from backend.analysis.smc import SMCAnalysis

            # Precompute indicators for all historical rows
            df_ta = TechnicalAnalysis.calculate_indicators(history_df)

            prices = []
            for index, row in df_ta.iterrows():
                # Extract indicators for this specific date
                indicator_keys = ["EMA_20", "EMA_50", "EMA_200", "RSI", "MACD_12_26_9"]
                indicators = {k: row[k] for k in indicator_keys if k in row}

                prices.append(StockPrice(
                    symbol=symbol,
                    date=index.to_pydatetime(),
                    open=row["Open"],
                    high=row["High"],
                    low=row["Low"],
                    close=row["Close"],
                    volume=int(row["Volume"]),
                    indicators=indicators
                ))

            await self.repository.save_historical_prices(symbol, prices)
        else:
            # Incremental update logic: handled by separate pipeline method
            await self.sync_incremental_prices(symbol, history_df)

        return stock

    async def sync_incremental_prices(self, symbol: str, new_history_df: Any):
        # Implementation of incremental storage logic
        for index, row in new_history_df.iterrows():
            # Check if this date already exists in Firestore to avoid duplicate writes
            # (Note: Date-based doc IDs also handle this, but checking prevents batch overhead)

            # Create a simple price record for now
            # Full indicator calculation happens in the Analysis Pipeline
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
        """
        Enterprise Data Quality Engine:
        Automatically detects anomalies, gaps, and outliers.
        """
        import pandas as pd
        report = {
            "symbol": symbol,
            "timestamp": datetime.now(),
            "status": "passed",
            "issues": []
        }

        # 1. Missing Values
        if df.isnull().values.any():
            report["status"] = "failed"
            report["issues"].append("Missing OHLCV data found")

        # 2. Time Gaps
        expected_range = pd.date_range(start=df.index.min(), end=df.index[-1], freq='B')
        if len(df) < len(expected_range) * 0.9: # Allow 10% gap for holidays
             report["issues"].append(f"Significant time gap detected: {len(df)} bars vs {len(expected_range)} expected")

        # 3. Outlier Detection
        returns = df['Close'].pct_change()
        outliers = returns[returns.abs() > 0.2] # 20% single day move is anomalous for Nifty
        if not outliers.empty:
            report["issues"].append(f"Anomalous price moves detected on: {outliers.index.tolist()}")

        return report
