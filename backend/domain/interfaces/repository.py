from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from backend.domain.models.stock import Stock, StockPrice

class IStockRepository(ABC):
    @abstractmethod
    async def get_all_stocks(self) -> List[Stock]:
        pass

    @abstractmethod
    async def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        pass

    @abstractmethod
    async def save_stock(self, stock: Stock) -> None:
        pass

    @abstractmethod
    async def save_historical_prices(self, symbol: str, prices: List[StockPrice]) -> None:
        pass

    @abstractmethod
    async def update_analysis(self, symbol: str, analysis: Dict[str, Any]) -> None:
        pass

class IMarketDataProvider(ABC):
    @abstractmethod
    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def fetch_history(self, symbol: str, period: str) -> Any:
        pass
