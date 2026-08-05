from backend.core.database import db_client
from backend.infrastructure.repositories.firestore_repository import FirestoreStockRepository, FirestoreDataPlatformRepository
from backend.infrastructure.repositories.yfinance_provider import YFinanceProvider
from backend.infrastructure.repositories.groq_provider import GroqAIProvider
from backend.services.stock_service import StockService
from backend.services.ml_service import MLService
from backend.services.feature_store import FeatureStoreService
from backend.services.knowledge_service import KnowledgeService
from backend.services.strategy_engine import StrategyEngine
from backend.services.ios.regime_engine import MarketRegimeEngine
from backend.services.ios.opportunity_engine import OpportunityEngine
from backend.services.ios.intelligence_service import MarketIntelligenceService
from backend.services.ios.timeframe_service import MultiTimeframeService
from backend.services.ios.coach_service import TradeCoachService
from backend.services.ios.graph_service import KnowledgeGraphService
from backend.services.ios.digital_twin import DigitalTwinService
from backend.services.ios.adaptive_learning import AdaptiveLearningService
from backend.infrastructure.repositories.firestore_ios_repository import FirestoreIOSRepository

# Simple Singleton Container for Service Injection
class Container:
    def __init__(self):
        self.repository = FirestoreStockRepository(db_client)
        self.data_platform_repo = FirestoreDataPlatformRepository(db_client)
        self.ios_repo = FirestoreIOSRepository(db_client)
        self.provider = YFinanceProvider()
        self.ai_provider = GroqAIProvider()
        self.ml_service = MLService(self.data_platform_repo)
        self.feature_store = FeatureStoreService(self.data_platform_repo)
        self.knowledge_service = KnowledgeService(self.data_platform_repo)
        self.strategy_engine = StrategyEngine()
        self.regime_engine = MarketRegimeEngine()
        self.opportunity_engine = OpportunityEngine()
        self.intel_service = MarketIntelligenceService()
        self.timeframe_service = MultiTimeframeService(self.provider)
        self.coach_service = TradeCoachService()
        self.graph_service = KnowledgeGraphService(self.repository)
        self.twin_service = DigitalTwinService(self.repository, self.data_platform_repo)
        self.adaptive_service = AdaptiveLearningService(self.data_platform_repo)
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

def get_knowledge_service():
    return container.knowledge_service

def get_strategy_engine():
    return container.strategy_engine

def get_ios_repo():
    return container.ios_repo
