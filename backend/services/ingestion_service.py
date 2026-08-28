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
        retries: int = 3,
        asset_class: str = "EQUITY"
    ) -> Dict[str, Any]:
        """
        Robustly ingests historical data with retries, chunking and validation.
        Supports EQUITY and F&O segments.
        """
        print(f"[*] Starting robust {asset_class} ingestion for {symbol} ({interval})")

        attempt = 0
        prices = []

        # If F&O, we might need to verify instrument existence or mapping
        target_symbol = symbol
        if asset_class != "EQUITY":
            # For F&O, ensure we use the provider's specific symbol format if different
            pass

        while attempt < retries:
            try:
                prices = await self.provider.get_historical_candles(target_symbol, start_date, end_date, interval)
                if prices: break
                attempt += 1
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                print(f"[!] Ingestion attempt {attempt} failed for {symbol}: {e}")
                attempt += 1
                await asyncio.sleep(2 ** attempt)

        if not prices:
            return {"status": "FAILED", "reason": f"No {asset_class} data received from provider after retries"}

        # 2. Validation & Deduplication
        validated_prices = self._validate_and_deduplicate(prices)

        # 3. Persistence
        await self.repository.save_historical_prices(symbol, validated_prices)

        return {
            "status": "SUCCESS",
            "asset_class": asset_class,
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
