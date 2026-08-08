from typing import List, Optional, Dict, Any, Callable
from sqlalchemy.orm import Session
from datetime import datetime
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.interfaces.repository import IStockRepository, IDataPlatformRepository
from backend.core.postgres import StockDB, PriceDB, RegimeDB, PredictionDB, IntelReportDB, FeatureDefinitionDB
from backend.core.duckdb_engine import analytical_engine
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow, FeatureVector, Prediction, FeatureDefinition, ModelMetadata, MLDataset, PortfolioHealth, Alert, EarningsData, OptionsChain
from backend.domain.models.strategy import UserStrategy, PaperOrder, VirtualPortfolio
from backend.domain.models.ios import WorkspaceState, ResearchNote, MarketRegime, MarketOpportunity, MarketIntelligenceReport, TradeFeedback
from backend.domain.interfaces.ios_repository import IIOSRepository
import pandas as pd
import json
import uuid

class HybridStockRepository(IStockRepository):
    def __init__(self, session_factory: Callable[[], Session], firestore_db: Any):
        self.session_factory = session_factory
        self.fs = firestore_db

    @property
    def db(self):
        """Compatibility property for legacy Firestore access in workers."""
        return self.fs

    async def get_all_stocks(self, limit: int = 50, offset: int = 0) -> List[Stock]:
        with self.session_factory() as pg:
            stocks = pg.query(StockDB).order_by(StockDB.symbol).limit(limit).offset(offset).all()
            return [self._map_db_to_stock(s) for s in stocks]

    async def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        with self.session_factory() as pg:
            s = pg.query(StockDB).filter(StockDB.symbol == symbol).first()
            return self._map_db_to_stock(s) if s else None

    async def save_stock(self, stock: Stock) -> None:
        def json_serializable(data):
            """Recursively convert datetimes and NaNs to serializable formats."""
            import math
            if isinstance(data, dict):
                return {k: json_serializable(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [json_serializable(i) for i in data]
            elif isinstance(data, datetime):
                return data.isoformat()
            elif isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
                return None
            return data

        with self.session_factory() as pg:
            db_stock = pg.query(StockDB).filter(StockDB.symbol == stock.symbol).first()
            data = stock.model_dump()

            db_columns = {c.name for c in StockDB.__table__.columns}
            json_cols = {"analysis", "structured_consensus", "health_metrics", "confidence_metrics"}

            filtered_data = {}
            for k, v in data.items():
                if k in db_columns:
                    if k in json_cols:
                        filtered_data[k] = json_serializable(v)
                    else:
                        filtered_data[k] = v

            if db_stock:
                for key, value in filtered_data.items():
                    setattr(db_stock, key, value)
            else:
                db_stock = StockDB(**filtered_data)
                pg.add(db_stock)
            pg.commit()

    async def save_historical_prices(self, symbol: str, prices: List[StockPrice]) -> None:
        """
        RC-4: HIGH-SPEED BATCH UPSERT
        Reduces network round-trips from 2,500 down to 1.
        """
        if not prices: return

        def clean_indicators(indicators):
            if not indicators: return None
            import math
            cleaned = {}
            for k, v in indicators.items():
                if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    cleaned[k] = None
                else:
                    cleaned[k] = v
            return cleaned

        with self.session_factory() as pg:
            # 1. Fetch all existing dates for this symbol in one go
            existing_dates = {
                d[0].date() if hasattr(d[0], 'date') else d[0]
                for d in pg.query(PriceDB.date).filter(PriceDB.symbol == symbol).all()
            }

            to_add = []
            for p in prices:
                p_date = p.date.date() if hasattr(p.date, 'date') else p.date
                if p_date not in existing_dates:
                    to_add.append(PriceDB(
                        symbol=symbol,
                        date=p.date,
                        open=p.open,
                        high=p.high,
                        low=p.low,
                        close=p.close,
                        volume=p.volume,
                        indicators=clean_indicators(p.indicators)
                    ))

            # 2. Bulk insert new records
            if to_add:
                pg.bulk_save_objects(to_add)

            pg.commit()

    async def get_recent_prices(self, symbol: str, limit: int = 250) -> List[StockPrice]:
        with self.session_factory() as pg:
            prices = pg.query(PriceDB).filter(PriceDB.symbol == symbol).order_by(PriceDB.date.desc()).limit(limit).all()
            results = [StockPrice(**{c.name: getattr(p, c.name) for c in p.__table__.columns}) for p in prices]
            return sorted(results, key=lambda x: x.date)

    async def update_analysis(self, symbol: str, analysis: Dict[str, Any]) -> None:
        with self.session_factory() as pg:
            pg.query(StockDB).filter(StockDB.symbol == symbol).update({"analysis": analysis, "updated_at": datetime.utcnow()})
            pg.commit()

    def _map_db_to_stock(self, db_obj: StockDB) -> Stock:
        data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        # Ensure BigInt market_cap fits into float
        if data.get('market_cap'):
            data['market_cap'] = float(data['market_cap'])
        return Stock(**data)

class HybridDataPlatformRepository(IDataPlatformRepository):
    def __init__(self, session_factory: Callable[[], Session], firestore_db: Any):
        self.session_factory = session_factory
        self.fs = firestore_db
        self.duck = analytical_engine

    async def save_news(self, articles: List[NewsArticle]) -> None:
        from backend.core.postgres import NewsDB
        with self.session_factory() as pg:
            for art in articles:
                existing = pg.query(NewsDB).filter(NewsDB.id == art.id).first()
                if not existing:
                    pg.add(NewsDB(**art.model_dump()))
            pg.commit()

    async def get_latest_news(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        from backend.core.postgres import NewsDB
        with self.session_factory() as pg:
            res = pg.query(NewsDB).filter(NewsDB.symbol == symbol).order_by(NewsDB.published_at.desc()).limit(limit).all()
            return [NewsArticle(**{c.name: getattr(r, c.name) for c in r.__table__.columns}) for r in res]

    async def save_institutional_flow(self, flow: InstitutionalFlow) -> None:
        from google.cloud import firestore
        # User Heuristic tier - kept in Firestore for real-time reactivity
        self.fs.collection("institutional_flow").document(flow.date.strftime("%Y-%m-%d")).set(flow.model_dump())

    async def get_latest_institutional_flow(self) -> Optional[InstitutionalFlow]:
        from google.cloud import firestore
        docs = self.fs.collection("institutional_flow").order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs: return InstitutionalFlow(**doc.to_dict())
        return None

    async def save_feature_vector(self, vector: FeatureVector) -> None:
        df = pd.DataFrame([{"date": vector.date, **vector.features}])
        self.duck.ingest_features(vector.symbol, df)

    async def save_prediction(self, prediction: Prediction) -> None:
        with self.session_factory() as pg:
            pg.add(PredictionDB(symbol=prediction.symbol, date=prediction.date, model_version=prediction.model_version, prediction=prediction.prediction, confidence=prediction.confidence, metadata_json=prediction.metadata))
            pg.commit()

    async def save_portfolio_health(self, health: PortfolioHealth) -> None: self.fs.collection("portfolio_health").document(health.user_id).set(health.model_dump())
    async def get_portfolio_health(self, user_id: str) -> Optional[PortfolioHealth]:
        doc = self.fs.collection("portfolio_health").document(user_id).get()
        return PortfolioHealth(**doc.to_dict()) if doc.exists else None

    async def save_alert(self, alert: Alert) -> None: self.fs.collection("alerts").document(alert.id).set(alert.model_dump())
    async def get_active_alerts(self, limit: int = 20) -> List[Alert]:
        docs = self.fs.collection("alerts").where("is_read", "==", False).limit(limit).stream()
        return [Alert(**doc.to_dict()) for doc in docs]

    async def save_earnings(self, earnings: EarningsData) -> None:
        from backend.core.postgres import EarningsDB
        with self.session_factory() as pg:
            doc_id = f"{earnings.symbol}_{earnings.date.strftime('%Y-%m-%d')}"
            existing = pg.query(EarningsDB).filter(EarningsDB.id == doc_id).first()
            if not existing:
                pg.add(EarningsDB(id=doc_id, **earnings.model_dump()))
            pg.commit()

    async def get_latest_earnings(self, symbol: str) -> Optional[EarningsData]:
        from backend.core.postgres import EarningsDB
        with self.session_factory() as pg:
            res = pg.query(EarningsDB).filter(EarningsDB.symbol == symbol).order_by(EarningsDB.date.desc()).first()
            return EarningsData(**{c.name: getattr(res, c.name) for c in res.__table__.columns}) if res else None
    async def save_options_chain(self, chain: OptionsChain) -> None: pass
    async def get_latest_options_chain(self, symbol: str) -> Optional[OptionsChain]: return None

    async def save_feature_definition(self, definition: FeatureDefinition) -> None:
        with self.session_factory() as pg:
            db_def = pg.query(FeatureDefinitionDB).filter(FeatureDefinitionDB.name == definition.name).first()
            data = definition.model_dump()
            if db_def:
                for k, v in data.items():
                    if hasattr(db_def, k): setattr(db_def, k, v)
            else:
                pg.add(FeatureDefinitionDB(**data))
            pg.commit()

    async def get_feature_definitions(self, category: Optional[str] = None) -> List[FeatureDefinition]:
        with self.session_factory() as pg:
            query = pg.query(FeatureDefinitionDB)
            if category: query = query.filter(FeatureDefinitionDB.category == category)
            return [FeatureDefinition(**{c.name: getattr(d, c.name) for c in d.__table__.columns}) for d in query.all()]

    async def save_strategy(self, strategy: UserStrategy) -> None: self.fs.collection("strategies").document(strategy.id).set(strategy.model_dump())
    async def get_user_strategies(self, user_id: str) -> List[UserStrategy]:
        docs = self.fs.collection("strategies").where("user_id", "==", user_id).stream()
        return [UserStrategy(**doc.to_dict()) for doc in docs]

    async def save_paper_order(self, order: PaperOrder) -> None: self.fs.collection("paper_orders").document(order.id).set(order.model_dump())
    async def get_virtual_portfolio(self, user_id: str) -> Optional[VirtualPortfolio]:
        doc = self.fs.collection("virtual_portfolios").document(user_id).get()
        return VirtualPortfolio(**doc.to_dict()) if doc.exists else None

    async def save_virtual_portfolio(self, portfolio: VirtualPortfolio) -> None: self.fs.collection("virtual_portfolios").document(portfolio.user_id).set(portfolio.model_dump())
    async def save_model_metadata(self, metadata: ModelMetadata) -> None: pass
    async def get_champion_model(self, symbol: str) -> Optional[ModelMetadata]: return None
    async def save_ml_dataset(self, dataset: MLDataset) -> None: pass

    async def get_features_by_range(self, symbol: str, start_date: datetime, end_date: datetime) -> List[FeatureVector]:
        df = self.duck.create_ml_dataset(symbol, start_date.isoformat(), end_date.isoformat())
        return [FeatureVector(symbol=symbol, date=row['date'], version="v1.0.0", features={k: v for k, v in row.to_dict().items() if k != 'date'}) for _, row in df.iterrows()]

    async def register_device(self, user_id: str, device_info: Dict[str, Any]) -> None: self.fs.collection("devices").document(device_info['device_id']).set({**device_info, "user_id": user_id})
    async def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        docs = self.fs.collection("devices").where("user_id", "==", user_id).stream()
        return [doc.to_dict() for doc in docs]

class HybridIOSRepository(IIOSRepository):
    def __init__(self, session_factory: Callable[[], Session], firestore_db: Any):
        self.session_factory = session_factory
        self.fs = firestore_db

    async def save_workspace(self, workspace: WorkspaceState) -> None: self.fs.collection("workspaces").document(workspace.id).set(workspace.model_dump())
    async def get_user_workspaces(self, user_id: str) -> List[WorkspaceState]:
        docs = self.fs.collection("workspaces").where("user_id", "==", user_id).stream()
        return [WorkspaceState(**doc.to_dict()) for doc in docs]

    async def save_research_note(self, note: ResearchNote) -> None: self.fs.collection("research_notes").document(note.id).set(note.model_dump())
    async def get_stock_notes(self, user_id: str, symbol: str) -> List[ResearchNote]:
        docs = self.fs.collection("research_notes").where("user_id", "==", user_id).where("symbol", "==", symbol).stream()
        return [ResearchNote(**doc.to_dict()) for doc in docs]

    async def save_market_regime(self, regime: MarketRegime) -> None:
        from backend.core.postgres import RegimeDB
        with self.session_factory() as pg:
            print(f"[HYBRID] Saving Market Regime to SQL...")
            db_regime = RegimeDB(
                date=regime.date,
                regime=regime.regime,
                risk_mode=regime.risk_mode,
                sentiment_score=regime.sentiment_score,
                description=regime.description,
                volatility_index=regime.volatility_index
            )
            pg.add(db_regime)
            pg.commit()
            print(f"[HYBRID] Market Regime saved successfully.")

    async def get_latest_regime(self) -> Optional[MarketRegime]:
        with self.session_factory() as pg:
            r = pg.query(RegimeDB).order_by(RegimeDB.date.desc()).first()
            if r:
                return MarketRegime(
                    date=r.date,
                    regime=r.regime,
                    risk_mode=r.risk_mode,
                    sentiment_score=r.sentiment_score or 0.5,
                    volatility_index=r.volatility_index,
                    description=r.description
                )
            return None

    async def save_opportunity(self, opportunity: MarketOpportunity) -> None:
        from backend.core.postgres import OpportunityDB
        with self.session_factory() as pg:
            pg.add(OpportunityDB(**opportunity.model_dump()))
            pg.commit()

    async def get_active_opportunities(self, limit: int = 20) -> List[MarketOpportunity]:
        from backend.core.postgres import OpportunityDB
        with self.session_factory() as pg:
            res = pg.query(OpportunityDB).order_by(OpportunityDB.timestamp.desc()).limit(limit).all()
            return [MarketOpportunity(**{c.name: getattr(r, c.name) for c in r.__table__.columns if c.name != 'indicators'}) for r in res]

    async def save_intel_report(self, report: MarketIntelligenceReport) -> None:
        from backend.core.postgres import IntelReportDB
        with self.session_factory() as pg:
            print(f"[HYBRID] Saving Intel Report ({report.type}) to SQL...")
            db_report = IntelReportDB(
                id=report.id,
                type=report.type,
                date=report.date,
                summary=report.summary,
                key_events=report.key_events,
                ai_bias=report.ai_bias
            )
            pg.add(db_report)
            pg.commit()
            print(f"[HYBRID] Intel Report saved successfully.")

    async def get_latest_intel_report(self, report_type: str) -> Optional[MarketIntelligenceReport]:
        with self.session_factory() as pg:
            r = pg.query(IntelReportDB).filter(IntelReportDB.type == report_type).order_by(IntelReportDB.date.desc()).first()
            if r:
                return MarketIntelligenceReport(
                    id=r.id,
                    type=r.type,
                    date=r.date,
                    summary=r.summary,
                    key_events=r.key_events or [],
                    top_movers=[],
                    sector_performance={},
                    ai_bias=r.ai_bias or "NEUTRAL"
                )
            return None

    async def save_trade_feedback(self, feedback: TradeFeedback) -> None: self.fs.collection("trade_journal").document(feedback.id).set(feedback.model_dump())
    async def get_user_trades(self, user_id: str) -> List[TradeFeedback]:
        docs = self.fs.collection("trade_journal").where("user_id", "==", user_id).stream()
        return [TradeFeedback(**doc.to_dict()) for doc in docs]
