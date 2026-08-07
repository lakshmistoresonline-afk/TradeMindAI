from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.interfaces.repository import IStockRepository, IDataPlatformRepository
from backend.core.postgres import StockDB, PriceDB, RegimeDB, PredictionDB, IntelReportDB
from backend.core.duckdb_engine import analytical_engine
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow, FeatureVector, Prediction, FeatureDefinition, ModelMetadata, MLDataset, PortfolioHealth, Alert, EarningsData, OptionsChain
from backend.domain.models.strategy import UserStrategy, PaperOrder, VirtualPortfolio
from backend.domain.models.ios import WorkspaceState, ResearchNote, MarketRegime, MarketOpportunity, MarketIntelligenceReport, TradeFeedback
from backend.domain.interfaces.ios_repository import IIOSRepository
import pandas as pd
import json
import uuid

class HybridStockRepository(IStockRepository):
    def __init__(self, pg_session: Session, firestore_db: Any):
        self.pg = pg_session
        self.fs = firestore_db

    @property
    def db(self):
        """Compatibility property for legacy Firestore access in workers."""
        return self.fs

    async def get_all_stocks(self, limit: int = 50, offset: int = 0) -> List[Stock]:
        stocks = self.pg.query(StockDB).order_by(StockDB.symbol).limit(limit).offset(offset).all()
        return [self._map_db_to_stock(s) for s in stocks]

    async def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        s = self.pg.query(StockDB).filter(StockDB.symbol == symbol).first()
        return self._map_db_to_stock(s) if s else None

    async def save_stock(self, stock: Stock) -> None:
        db_stock = self.pg.query(StockDB).filter(StockDB.symbol == stock.symbol).first()
        data = stock.model_dump()

        # Clean data for SQL: filter out keys that don't exist in DB model
        db_columns = {c.name for c in StockDB.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in db_columns}

        if db_stock:
            for key, value in filtered_data.items():
                setattr(db_stock, key, value)
        else:
            db_stock = StockDB(**filtered_data)
            self.pg.add(db_stock)
        self.pg.commit()

    async def save_historical_prices(self, symbol: str, prices: List[StockPrice]) -> None:
        for p in prices:
            db_price = PriceDB(
                symbol=symbol,
                date=p.date,
                open=p.open,
                high=p.high,
                low=p.low,
                close=p.close,
                volume=p.volume,
                indicators=p.indicators
            )
            self.pg.add(db_price)
        self.pg.commit()

    async def get_recent_prices(self, symbol: str, limit: int = 250) -> List[StockPrice]:
        prices = self.pg.query(PriceDB)\
            .filter(PriceDB.symbol == symbol)\
            .order_by(PriceDB.date.desc())\
            .limit(limit).all()

        results = [StockPrice(**{
            "symbol": p.symbol,
            "date": p.date,
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume,
            "indicators": p.indicators
        }) for p in prices]

        return sorted(results, key=lambda x: x.date)

    async def update_analysis(self, symbol: str, analysis: Dict[str, Any]) -> None:
        self.pg.query(StockDB).filter(StockDB.symbol == symbol).update({
            "analysis": analysis,
            "updated_at": datetime.utcnow()
        })
        self.pg.commit()

    def _map_db_to_stock(self, db_obj: StockDB) -> Stock:
        # Generic mapping from DB to Pydantic
        data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        return Stock(**data)

class HybridDataPlatformRepository(IDataPlatformRepository):
    def __init__(self, pg_session: Session, firestore_db: Any):
        self.pg = pg_session
        self.fs = firestore_db
        self.duck = analytical_engine

    async def save_news(self, articles: List[NewsArticle]) -> None:
        pass # To be implemented in Postgres if needed

    async def get_latest_news(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        return []

    async def save_institutional_flow(self, flow: InstitutionalFlow) -> None:
        pass

    async def get_latest_institutional_flow(self) -> Optional[InstitutionalFlow]:
        return None

    async def save_feature_vector(self, vector: FeatureVector) -> None:
        df = pd.DataFrame([{"date": vector.date, **vector.features}])
        self.duck.ingest_features(vector.symbol, df)

    async def save_prediction(self, prediction: Prediction) -> None:
        db_pred = PredictionDB(
            symbol=prediction.symbol,
            date=prediction.date,
            model_version=prediction.model_version,
            prediction=prediction.prediction,
            confidence=prediction.confidence,
            metadata_json=prediction.metadata
        )
        self.pg.add(db_pred)
        self.pg.commit()

    async def save_portfolio_health(self, health: PortfolioHealth) -> None:
        self.fs.collection("portfolio_health").document(health.user_id).set(health.model_dump())

    async def get_portfolio_health(self, user_id: str) -> Optional[PortfolioHealth]:
        doc = self.fs.collection("portfolio_health").document(user_id).get()
        return PortfolioHealth(**doc.to_dict()) if doc.exists else None

    async def save_alert(self, alert: Alert) -> None:
        self.fs.collection("alerts").document(alert.id).set(alert.model_dump())

    async def get_active_alerts(self, limit: int = 20) -> List[Alert]:
        docs = self.fs.collection("alerts").where("is_read", "==", False).limit(limit).stream()
        return [Alert(**doc.to_dict()) for doc in docs]

    async def save_earnings(self, earnings: EarningsData) -> None:
        pass

    async def get_latest_earnings(self, symbol: str) -> Optional[EarningsData]:
        return None

    async def save_options_chain(self, chain: OptionsChain) -> None:
        pass

    async def get_latest_options_chain(self, symbol: str) -> Optional[OptionsChain]:
        return None

    async def save_feature_definition(self, definition: FeatureDefinition) -> None:
        # Operational Data -> PostgreSQL
        from backend.core.postgres import FeatureDefinitionDB
        db_def = self.pg.query(FeatureDefinitionDB).filter(FeatureDefinitionDB.name == definition.name).first()
        data = definition.model_dump()
        if db_def:
            for k, v in data.items():
                if hasattr(db_def, k): setattr(db_def, k, v)
        else:
            db_def = FeatureDefinitionDB(**data)
            self.pg.add(db_def)
        self.pg.commit()

    async def get_feature_definitions(self, category: Optional[str] = None) -> List[FeatureDefinition]:
        from backend.core.postgres import FeatureDefinitionDB
        query = self.pg.query(FeatureDefinitionDB)
        if category:
            query = query.filter(FeatureDefinitionDB.category == category)
        defs = query.all()
        return [FeatureDefinition(**{
            "name": d.name,
            "description": d.description,
            "category": d.category,
            "data_type": d.data_type,
            "min_value": d.min_value,
            "max_value": d.max_value,
            "version": d.version,
            "last_updated": d.last_updated
        }) for d in defs]

    async def save_strategy(self, strategy: UserStrategy) -> None:
        self.fs.collection("strategies").document(strategy.id).set(strategy.model_dump())

    async def get_user_strategies(self, user_id: str) -> List[UserStrategy]:
        docs = self.fs.collection("strategies").where("user_id", "==", user_id).stream()
        return [UserStrategy(**doc.to_dict()) for doc in docs]

    async def save_paper_order(self, order: PaperOrder) -> None:
        self.fs.collection("paper_orders").document(order.id).set(order.model_dump())

    async def get_virtual_portfolio(self, user_id: str) -> Optional[VirtualPortfolio]:
        doc = self.fs.collection("virtual_portfolios").document(user_id).get()
        return VirtualPortfolio(**doc.to_dict()) if doc.exists else None

    async def save_virtual_portfolio(self, portfolio: VirtualPortfolio) -> None:
        self.fs.collection("virtual_portfolios").document(portfolio.user_id).set(portfolio.model_dump())

    async def save_model_metadata(self, metadata: ModelMetadata) -> None:
        pass

    async def get_champion_model(self, symbol: str) -> Optional[ModelMetadata]:
        return None

    async def save_ml_dataset(self, dataset: MLDataset) -> None:
        pass

    async def get_features_by_range(self, symbol: str, start_date: datetime, end_date: datetime) -> List[FeatureVector]:
        df = self.duck.create_ml_dataset(symbol, start_date.isoformat(), end_date.isoformat())
        results = []
        for _, row in df.iterrows():
            results.append(FeatureVector(
                symbol=symbol,
                date=row['date'],
                version="v1.0.0",
                features={k: v for k, v in row.to_dict().items() if k != 'date'}
            ))
        return results

    async def register_device(self, user_id: str, device_info: Dict[str, Any]) -> None:
        self.fs.collection("devices").document(device_info['device_id']).set({**device_info, "user_id": user_id})

    async def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        docs = self.fs.collection("devices").where("user_id", "==", user_id).stream()
        return [doc.to_dict() for doc in docs]

class HybridIOSRepository(IIOSRepository):
    def __init__(self, pg_session: Session, firestore_db: Any):
        self.pg = pg_session
        self.fs = firestore_db

    async def save_workspace(self, workspace: WorkspaceState) -> None:
        self.fs.collection("workspaces").document(workspace.id).set(workspace.model_dump())

    async def get_user_workspaces(self, user_id: str) -> List[WorkspaceState]:
        docs = self.fs.collection("workspaces").where("user_id", "==", user_id).stream()
        return [WorkspaceState(**doc.to_dict()) for doc in docs]

    async def save_research_note(self, note: ResearchNote) -> None:
        self.fs.collection("research_notes").document(note.id).set(note.model_dump())

    async def get_stock_notes(self, user_id: str, symbol: str) -> List[ResearchNote]:
        docs = self.fs.collection("research_notes")\
            .where("user_id", "==", user_id)\
            .where("symbol", "==", symbol).stream()
        return [ResearchNote(**doc.to_dict()) for doc in docs]

    async def save_market_regime(self, regime: MarketRegime) -> None:
        db_regime = RegimeDB(
            date=regime.date,
            regime=regime.regime,
            risk_mode=regime.risk_mode,
            description=regime.description,
            volatility_index=regime.volatility_index
        )
        self.pg.add(db_regime)
        self.pg.commit()

    async def get_latest_regime(self) -> Optional[MarketRegime]:
        r = self.pg.query(RegimeDB).order_by(RegimeDB.date.desc()).first()
        if r:
            return MarketRegime(
                date=r.date, regime=r.regime, risk_mode=r.risk_mode,
                sentiment_score=0.5, volatility_index=r.volatility_index,
                description=r.description
            )
        return None

    async def save_opportunity(self, opportunity: MarketOpportunity) -> None:
        pass

    async def get_active_opportunities(self, limit: int = 20) -> List[MarketOpportunity]:
        return []

    async def save_intel_report(self, report: MarketIntelligenceReport) -> None:
        db_report = IntelReportDB(
            id=report.id, type=report.type, date=report.date,
            summary=report.summary, key_events=report.key_events, ai_bias=report.ai_bias
        )
        self.pg.add(db_report)
        self.pg.commit()

    async def get_latest_intel_report(self, report_type: str) -> Optional[MarketIntelligenceReport]:
        r = self.pg.query(IntelReportDB).filter(IntelReportDB.type == report_type).order_by(IntelReportDB.date.desc()).first()
        if r:
            return MarketIntelligenceReport(
                id=r.id, type=r.type, date=r.date, summary=r.summary,
                key_events=r.key_events, top_movers=[], sector_performance={}, ai_bias=r.ai_bias
            )
        return None

    async def save_trade_feedback(self, feedback: TradeFeedback) -> None:
        self.fs.collection("trade_journal").document(feedback.id).set(feedback.model_dump())

    async def get_user_trades(self, user_id: str) -> List[TradeFeedback]:
        docs = self.fs.collection("trade_journal").where("user_id", "==", user_id).stream()
        return [TradeFeedback(**doc.to_dict()) for doc in docs]
