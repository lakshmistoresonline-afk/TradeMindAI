from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow, FeatureVector, Prediction, FeatureDefinition, ModelMetadata, MLDataset, PortfolioHealth, Alert

class IStockRepository(ABC):
    @abstractmethod
    async def get_all_stocks(self, limit: int = 50, offset: int = 0) -> List[Stock]:
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
    async def get_recent_prices(self, symbol: str, limit: int = 250) -> List[StockPrice]:
        pass

    @abstractmethod
    async def update_analysis(self, symbol: str, analysis: Dict[str, Any]) -> None:
        pass

class IDataPlatformRepository(ABC):
    @abstractmethod
    async def save_news(self, articles: List[NewsArticle]) -> None:
        pass

    @abstractmethod
    async def get_latest_news(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        pass

    @abstractmethod
    async def save_institutional_flow(self, flow: InstitutionalFlow) -> None:
        pass

    @abstractmethod
    async def get_latest_institutional_flow(self) -> Optional[InstitutionalFlow]:
        pass

    @abstractmethod
    async def save_feature_vector(self, vector: FeatureVector) -> None:
        pass

    @abstractmethod
    async def save_prediction(self, prediction: Prediction) -> None:
        pass

    @abstractmethod
    async def save_portfolio_health(self, health: PortfolioHealth) -> None:
        pass

    @abstractmethod
    async def get_portfolio_health(self, user_id: str) -> Optional[PortfolioHealth]:
        pass

    @abstractmethod
    async def save_alert(self, alert: Alert) -> None:
        pass

    @abstractmethod
    async def get_active_alerts(self, limit: int = 20) -> List[Alert]:
        pass

    @abstractmethod
    async def save_earnings(self, earnings: EarningsData) -> None:
        pass

    @abstractmethod
    async def get_latest_earnings(self, symbol: str) -> Optional[EarningsData]:
        pass

    @abstractmethod
    async def save_options_chain(self, chain: OptionsChain) -> None:
        pass

    @abstractmethod
    async def get_latest_options_chain(self, symbol: str) -> Optional[OptionsChain]:
        pass

    @abstractmethod
    async def save_feature_definition(self, definition: FeatureDefinition) -> None:
        pass

    @abstractmethod
    async def get_feature_definitions(self, category: Optional[str] = None) -> List[FeatureDefinition]:
        pass

    @abstractmethod
    async def save_model_metadata(self, metadata: ModelMetadata) -> None:
        pass

    @abstractmethod
    async def get_champion_model(self, symbol: str) -> Optional[ModelMetadata]:
        pass

    @abstractmethod
    async def save_ml_dataset(self, dataset: MLDataset) -> None:
        pass

    @abstractmethod
    async def get_features_by_range(self, symbol: str, start_date: datetime, end_date: datetime) -> List[FeatureVector]:
        pass

class IMarketDataProvider(ABC):
    @abstractmethod
    async def fetch_stock_info(self, symbol: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def fetch_history(self, symbol: str, period: str) -> Any:
        pass

class INewsProvider(ABC):
    @abstractmethod
    async def fetch_latest_news(self, symbol: str) -> List[NewsArticle]:
        pass

class IInstitutionalDataProvider(ABC):
    @abstractmethod
    async def fetch_daily_flow(self) -> InstitutionalFlow:
        pass
