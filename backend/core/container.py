# Simple Singleton Container for Service Injection
class Container:
    def __init__(self):
        self._repository = None
        self._data_platform_repo = None
        self._ios_repo = None
        self._provider = None
        self._ai_provider = None
        self._ml_service = None
        self._feature_store = None
        self._knowledge_service = None
        self._strategy_engine = None
        self._regime_engine = None
        self._opportunity_engine = None
        self._intel_service = None
        self._timeframe_service = None
        self._coach_service = None
        self._graph_service = None
        self._twin_service = None
        self._adaptive_service = None
        self._stock_service = None

    @property
    def repository(self):
        if self._repository is None:
            from backend.infrastructure.repositories.firestore_repository import FirestoreStockRepository
            from backend.core.database import db_client
            self._repository = FirestoreStockRepository(db_client)
        return self._repository

    @property
    def data_platform_repo(self):
        if self._data_platform_repo is None:
            from backend.infrastructure.repositories.firestore_repository import FirestoreDataPlatformRepository
            from backend.core.database import db_client
            self._data_platform_repo = FirestoreDataPlatformRepository(db_client)
        return self._data_platform_repo

    @property
    def ios_repo(self):
        if self._ios_repo is None:
            from backend.infrastructure.repositories.firestore_ios_repository import FirestoreIOSRepository
            from backend.core.database import db_client
            self._ios_repo = FirestoreIOSRepository(db_client)
        return self._ios_repo

    @property
    def provider(self):
        if self._provider is None:
            from backend.infrastructure.repositories.yfinance_provider import YFinanceProvider
            self._provider = YFinanceProvider()
        return self._provider

    @property
    def ai_provider(self):
        if self._ai_provider is None:
            from backend.infrastructure.repositories.groq_provider import GroqAIProvider
            self._ai_provider = GroqAIProvider()
        return self._ai_provider

    @property
    def ml_service(self):
        if self._ml_service is None:
            from backend.services.ml_service import MLService
            self._ml_service = MLService(self.data_platform_repo)
        return self._ml_service

    @property
    def feature_store(self):
        if self._feature_store is None:
            from backend.services.feature_store import FeatureStoreService
            self._feature_store = FeatureStoreService(self.data_platform_repo)
        return self._feature_store

    @property
    def knowledge_service(self):
        if self._knowledge_service is None:
            from backend.services.knowledge_service import KnowledgeService
            self._knowledge_service = KnowledgeService(self.data_platform_repo)
        return self._knowledge_service

    @property
    def strategy_engine(self):
        if self._strategy_engine is None:
            from backend.services.strategy_engine import StrategyEngine
            self._strategy_engine = StrategyEngine()
        return self._strategy_engine

    @property
    def regime_engine(self):
        if self._regime_engine is None:
            from backend.services.ios.regime_engine import MarketRegimeEngine
            self._regime_engine = MarketRegimeEngine()
        return self._regime_engine

    @property
    def opportunity_engine(self):
        if self._opportunity_engine is None:
            from backend.services.ios.opportunity_engine import OpportunityEngine
            self._opportunity_engine = OpportunityEngine()
        return self._opportunity_engine

    @property
    def intel_service(self):
        if self._intel_service is None:
            from backend.services.ios.intelligence_service import MarketIntelligenceService
            self._intel_service = MarketIntelligenceService()
        return self._intel_service

    @property
    def timeframe_service(self):
        if self._timeframe_service is None:
            from backend.services.ios.timeframe_service import MultiTimeframeService
            self._timeframe_service = MultiTimeframeService(self.provider)
        return self._timeframe_service

    @property
    def coach_service(self):
        if self._coach_service is None:
            from backend.services.ios.coach_service import TradeCoachService
            self._coach_service = TradeCoachService()
        return self._coach_service

    @property
    def graph_service(self):
        if self._graph_service is None:
            from backend.services.ios.graph_service import KnowledgeGraphService
            self._graph_service = KnowledgeGraphService(self.repository)
        return self._graph_service

    @property
    def twin_service(self):
        if self._twin_service is None:
            from backend.services.ios.digital_twin import DigitalTwinService
            self._twin_service = DigitalTwinService(self.repository, self.data_platform_repo)
        return self._twin_service

    @property
    def adaptive_service(self):
        if self._adaptive_service is None:
            from backend.services.ios.adaptive_learning import AdaptiveLearningService
            self._adaptive_service = AdaptiveLearningService(self.data_platform_repo)
        return self._adaptive_service

    @property
    def stock_service(self):
        if self._stock_service is None:
            from backend.services.stock_service import StockService
            self._stock_service = StockService(
                self.repository,
                self.provider,
                self.provider, # YFinance acts as NewsProvider
                self.provider  # YFinance acts as IInstitutionalDataProvider
            )
        return self._stock_service

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
