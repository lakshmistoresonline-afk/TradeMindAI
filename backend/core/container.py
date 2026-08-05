from backend.core.database import db_client
from backend.infrastructure.repositories.firestore_repository import FirestoreStockRepository, FirestoreDataPlatformRepository
from backend.infrastructure.repositories.yfinance_provider import YFinanceProvider
from backend.infrastructure.repositories.groq_provider import GroqAIProvider
from backend.services.stock_service import StockService
from backend.services.ml_service import MLService
from backend.services.feature_store import FeatureStoreService

# Simple Singleton Container for Service Injection
class Container:
    def __init__(self):
        self.repository = FirestoreStockRepository(db_client)
        self.data_platform_repo = FirestoreDataPlatformRepository(db_client)
        self.provider = YFinanceProvider()
        self.ai_provider = GroqAIProvider()
        self.ml_service = MLService(self.data_platform_repo)
        self.feature_store = FeatureStoreService(self.data_platform_repo)
        self.stock_service = StockService(
            self.repository,
            self.provider,
            self.provider, # YFinance acts as NewsProvider
            self.provider  # YFinance acts as IInstitutionalDataProvider
        )

container = Container()

def get_stock_service():
    return container.stock_service

def get_ai_provider():
    return container.ai_provider

def get_ml_service():
    return container.ml_service

def get_feature_store():
    return container.feature_store
