from .config import settings

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
        self._signal_engine = None
        self._universe_service = None
        self._data_quality_service = None
        self._derivative_service = None
        self._reconciliation_service = None
        self._audit_service = None
        self._model_registry = None
        self._audit_trail_service = None
        self._fno_registry = None
        self._health_service = None
        self._provenance_service = None
        self._quant_validation_service = None
        self._walk_forward_service = None
        self._experiment_service = None
        self._backtest_audit_service = None
        self._sector_rotation_service = None
        self._stock_intelligence_service = None
        self._institutional_intelligence_service = None
        self._intelligence_synthesis_service = None
        self._fundamental_service = None
        self._fno_intelligence_service = None
        self._monitoring_service = None
        self._opportunity_radar_service = None
        self._evidence_matrix_service = None
        self._ai_research_service = None
        self._historical_research_service = None
        self._portfolio_analytics_service = None
        self._canonical_signal_repo = None
        self._forensic_analytical_service = None
        self._export_service = None
        self._reconciliation_engine = None

    @property
    def signal_engine(self):
        if self._signal_engine is None:
            from backend.services.signal_engine import SignalEngine
            self._signal_engine = SignalEngine()
        return self._signal_engine

    @property
    def repository(self):
        if self._repository is None:
            from backend.infrastructure.repositories.hybrid_repository import HybridStockRepository
            from backend.core.database import get_db
            from backend.core.postgres import SessionLocal
            # SQL Init moved to background thread in main.py
            self._repository = HybridStockRepository(SessionLocal, get_db())
        return self._repository

    @property
    def data_platform_repo(self):
        if self._data_platform_repo is None:
            from backend.infrastructure.repositories.hybrid_repository import HybridDataPlatformRepository
            from backend.core.database import get_db
            from backend.core.postgres import SessionLocal
            self._data_platform_repo = HybridDataPlatformRepository(SessionLocal, get_db())
        return self._data_platform_repo

    @property
    def ios_repo(self):
        if self._ios_repo is None:
            from backend.infrastructure.repositories.hybrid_repository import HybridIOSRepository
            from backend.core.database import get_db
            from backend.core.postgres import SessionLocal
            self._ios_repo = HybridIOSRepository(SessionLocal, get_db())
        return self._ios_repo

    @property
    def provider(self):
        if self._provider is None:
            if settings.MARKET_DATA_PROVIDER == "groww":
                from backend.infrastructure.repositories.groww_provider import GrowwProvider
                self._provider = GrowwProvider()
            else:
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
    def universe_service(self):
        if self._universe_service is None:
            from backend.services.universe_service import UniverseService
            self._universe_service = UniverseService(self.repository, self.provider)
        return self._universe_service

    @property
    def data_quality_service(self):
        if self._data_quality_service is None:
            from backend.services.data_quality_service import DataQualityService
            self._data_quality_service = DataQualityService()
        return self._data_quality_service

    @property
    def derivative_service(self):
        if self._derivative_service is None:
            from backend.services.derivative_service import DerivativeService
            self._derivative_service = DerivativeService(self.repository, self.provider)
        return self._derivative_service

    @property
    def reconciliation_service(self):
        if self._reconciliation_service is None:
            from backend.services.reconciliation_service import ReconciliationService
            self._reconciliation_service = ReconciliationService()
        return self._reconciliation_service

    @property
    def audit_service(self):
        if self._audit_service is None:
            from backend.services.audit_service import AuditService
            self._audit_service = AuditService()
        return self._audit_service

    @property
    def model_registry(self):
        if self._model_registry is None:
            from backend.services.model_registry import ModelRegistryService
            self._model_registry = ModelRegistryService(self.data_platform_repo)
        return self._model_registry

    @property
    def audit_trail_service(self):
        if self._audit_trail_service is None:
            from backend.services.audit_trail_service import AuditTrailService
            self._audit_trail_service = AuditTrailService()
        return self._audit_trail_service

    @property
    def fno_registry(self):
        if self._fno_registry is None:
            from backend.services.fno_registry import FNORegistryService
            self._fno_registry = FNORegistryService()
        return self._fno_registry

    @property
    def health_service(self):
        if self._health_service is None:
            from backend.services.health_service import SystemHealthService
            self._health_service = SystemHealthService()
        return self._health_service

    @property
    def provenance_service(self):
        if self._provenance_service is None:
            from backend.services.provenance_service import ProvenanceService
            self._provenance_service = ProvenanceService()
        return self._provenance_service

    @property
    def quant_validation_service(self):
        if self._quant_validation_service is None:
            from backend.services.quant_validation_service import QuantitativeValidationService
            self._quant_validation_service = QuantitativeValidationService()
        return self._quant_validation_service

    @property
    def walk_forward_service(self):
        if self._walk_forward_service is None:
            from backend.services.walk_forward_service import WalkForwardValidationService
            self._walk_forward_service = WalkForwardValidationService()
        return self._walk_forward_service

    @property
    def experiment_service(self):
        if self._experiment_service is None:
            from backend.services.experiment_service import ExperimentService
            self._experiment_service = ExperimentService()
        return self._experiment_service

    @property
    def backtest_audit_service(self):
        if self._backtest_audit_service is None:
            from backend.services.backtest_audit_service import BacktestAuditService
            self._backtest_audit_service = BacktestAuditService()
        return self._backtest_audit_service

    @property
    def sector_rotation_service(self):
        if self._sector_rotation_service is None:
            from backend.services.sector_rotation_service import SectorRotationService
            self._sector_rotation_service = SectorRotationService()
        return self._sector_rotation_service

    @property
    def stock_intelligence_service(self):
        if self._stock_intelligence_service is None:
            from backend.services.stock_intelligence_service import StockIntelligenceService
            self._stock_intelligence_service = StockIntelligenceService()
        return self._stock_intelligence_service

    @property
    def institutional_intelligence_service(self):
        if self._institutional_intelligence_service is None:
            from backend.services.institutional_intelligence_service import InstitutionalIntelligenceService
            self._institutional_intelligence_service = InstitutionalIntelligenceService()
        return self._institutional_intelligence_service

    @property
    def intelligence_synthesis_service(self):
        if self._intelligence_synthesis_service is None:
            from backend.services.intelligence_synthesis_service import IntelligenceSynthesisService
            self._intelligence_synthesis_service = IntelligenceSynthesisService()
        return self._intelligence_synthesis_service

    @property
    def fundamental_service(self):
        if self._fundamental_service is None:
            from backend.services.fundamental_service import FundamentalService
            self._fundamental_service = FundamentalService()
        return self._fundamental_service

    @property
    def fno_intelligence_service(self):
        if self._fno_intelligence_service is None:
            from backend.services.fno_intelligence_service import FNOIntelligenceService
            self._fno_intelligence_service = FNOIntelligenceService()
        return self._fno_intelligence_service

    @property
    def monitoring_service(self):
        if self._monitoring_service is None:
            from backend.services.monitoring_service import MonitoringService
            self._monitoring_service = MonitoringService()
        return self._monitoring_service

    @property
    def monitoring_service(self):
        if self._monitoring_service is None:
            from backend.services.monitoring_service import MonitoringService
            self._monitoring_service = MonitoringService()
        return self._monitoring_service

    @property
    def opportunity_radar_service(self):
        if self._opportunity_radar_service is None:
            from backend.services.opportunity_radar_service import OpportunityRadarService
            self._opportunity_radar_service = OpportunityRadarService()
        return self._opportunity_radar_service

    @property
    def evidence_matrix_service(self):
        if self._evidence_matrix_service is None:
            from backend.services.evidence_matrix_service import EvidenceMatrixService
            self._evidence_matrix_service = EvidenceMatrixService()
        return self._evidence_matrix_service

    @property
    def ai_research_service(self):
        if self._ai_research_service is None:
            from backend.services.ai_research_service import AIResearchService
            self._ai_research_service = AIResearchService()
        return self._ai_research_service

    @property
    def historical_research_service(self):
        if self._historical_research_service is None:
            from backend.services.historical_research_service import HistoricalResearchService
            self._historical_research_service = HistoricalResearchService()
        return self._historical_research_service

    @property
    def portfolio_analytics_service(self):
        if self._portfolio_analytics_service is None:
            from backend.services.portfolio_analytics_service import PortfolioAnalyticsService
            self._portfolio_analytics_service = PortfolioAnalyticsService()
        return self._portfolio_analytics_service

    @property
    def canonical_signal_repo(self):
        if self._canonical_signal_repo is None:
            from backend.infrastructure.repositories.canonical_signal_repository import CanonicalSignalRepository
            from backend.core.postgres import SessionLocal
            self._canonical_signal_repo = CanonicalSignalRepository(SessionLocal)
        return self._canonical_signal_repo

    @property
    def forensic_analytical_service(self):
        if self._forensic_analytical_service is None:
            from backend.services.forensic_analytical_service import ForensicAnalyticalService
            self._forensic_analytical_service = ForensicAnalyticalService()
        return self._forensic_analytical_service

    @property
    def export_service(self):
        if self._export_service is None:
            from backend.services.export_service import ExportService
            self._export_service = ExportService()
        return self._export_service

    @property
    def reconciliation_engine(self):
        if self._reconciliation_engine is None:
            from backend.services.reconciliation_engine import ReconciliationEngine
            self._reconciliation_engine = ReconciliationEngine()
        return self._reconciliation_engine

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
