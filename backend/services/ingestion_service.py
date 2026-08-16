import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from backend.domain.models.stock import StockPrice
from backend.domain.interfaces.repository import IStockRepository, IMarketDataProvider

class IngestionService:
    def __init__(self, repository: IStockRepository, provider: IMarketDataProvider):
        self.repository = repository
        self.provider = provider

    async def ingest_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Robustly ingests historical data with retries, chunking and validation.
        """
        print(f"[*] Starting robust ingestion for {symbol} ({interval})")

        # 1. Fetch candles from provider
        # provider.get_historical_candles should already handle chunking internally for specific providers
        # but we add another layer of robustness here.

        attempt = 0
        prices = []
        while attempt < retries:
            try:
                prices = await self.provider.get_historical_candles(symbol, start_date, end_date, interval)
                if prices: break
                attempt += 1
                await asyncio.sleep(2 ** attempt) # Exponential backoff
            except Exception as e:
                print(f"[!] Ingestion attempt {attempt} failed for {symbol}: {e}")
                attempt += 1
                await asyncio.sleep(2 ** attempt)

        if not prices:
            return {"status": "FAILED", "reason": "No data received from provider after retries"}

        # 2. Validation & Deduplication
        validated_prices = self._validate_and_deduplicate(prices)

        # 3. Persistence
        await self.repository.save_historical_prices(symbol, validated_prices)

        return {
            "status": "SUCCESS",
            "count": len(validated_prices),
            "duplicates_removed": len(prices) - len(validated_prices),
            "start": validated_prices[0].date if validated_prices else None,
            "end": validated_prices[-1].date if validated_prices else None
        }

    def _validate_and_deduplicate(self, prices: List[StockPrice]) -> List[StockPrice]:
        if not prices: return []

        # Sort by date
        prices.sort(key=lambda x: x.date)

        seen_timestamps = set()
        unique_prices = []

        for p in prices:
            # Basic validation
            if p.open <= 0 or p.high <= 0 or p.low <= 0 or p.close <= 0:
                continue # Skip invalid prices

            if p.date not in seen_timestamps:
                unique_prices.append(p)
                seen_timestamps.add(p.date)

        return unique_prices
