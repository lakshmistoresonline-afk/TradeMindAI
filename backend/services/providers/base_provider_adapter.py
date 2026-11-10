"""
================================================================================
TradeMindAI Phase 4: Base Market Data Provider Adapter Interface
================================================================================
Defines the standard abstraction for all market-data provider adapters.
Every provider implementation (FYERS, Angel One SmartAPI, etc.) must implement this contract.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import datetime

class BaseMarketDataProviderAdapter(ABC):

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the canonical name of the provider (e.g., 'FYERS', 'ANGEL_ONE')."""
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        """Validates credentials and obtains an active session/access token."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Returns provider status, latency, and operational health state."""
        pass

    @abstractmethod
    def discover_capabilities(self) -> Dict[str, Any]:
        """Returns provider features, max lookback, supported timeframes, and rate limits."""
        pass

    @abstractmethod
    async def fetch_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime.date,
        end_date: datetime.date
    ) -> List[Dict[str, Any]]:
        """
        Fetches historical OHLCV candles for a symbol between start_date and end_date.
        Handles date-window splitting, pagination, rate-limiting, and error classification.
        """
        pass

    @abstractmethod
    def normalize_candles(self, raw_data: Any, symbol: str) -> List[Dict[str, Any]]:
        """Normalizes raw provider API responses into canonical TradeMindAI OHLCV candle dictionaries."""
        pass

    @abstractmethod
    def get_rate_limit_state(self) -> Dict[str, Any]:
        """Returns rate-limit budget, remaining quota, and reset timestamp."""
        pass

    @abstractmethod
    def get_provider_metadata(self) -> Dict[str, Any]:
        """Returns metadata such as provider version, API endpoint URLs, and entitlement status."""
        pass
