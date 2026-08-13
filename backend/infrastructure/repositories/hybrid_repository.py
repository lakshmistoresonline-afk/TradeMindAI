from typing import List, Optional, Dict, Any, Callable
from sqlalchemy.orm import Session
from datetime import datetime
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.interfaces.repository import IStockRepository, IDataPlatformRepository
from backend.core.postgres import StockDB, PriceDB, RegimeDB, PredictionDB, IntelReportDB, FeatureDefinitionDB, LiveSignalDB, WorkspaceDB, ResearchNoteDB, TradeJournalDB
from backend.core.duckdb_engine import analytical_engine
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow, FeatureVector, Prediction, FeatureDefinition, ModelMetadata, MLDataset, PortfolioHealth, Alert, EarningsData, OptionsChain
from backend.domain.models.strategy import UserStrategy, PaperOrder, VirtualPortfolio
from backend.domain.models.ios import WorkspaceState, ResearchNote, MarketRegime, MarketOpportunity, MarketIntelligenceReport, TradeFeedback, LiveSignal
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
            json_cols = {"analysis", "structured_consensus", "health_metrics", "confidence_metrics", "options_data", "financial_history"}

            filtered_data = {}
            for k, v in data.items():
                if k in db_columns:
                    if k in json_cols:
                        filtered_data[k] = json.dumps(json_serializable(v)) if v is not None else None
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
                        open_interest=p.open_interest,
                        source=p.source,
                        indicators=json.dumps(clean_indicators(p.indicators)) if p.indicators else None
                    ))

            # 2. Bulk insert new records
            if to_add:
                pg.bulk_save_objects(to_add)

            pg.commit()

    async def get_recent_prices(self, symbol: str, limit: int = 250) -> List[StockPrice]:
        with self.session_factory() as pg:
            prices = pg.query(PriceDB).filter(PriceDB.symbol == symbol).order_by(PriceDB.date.desc()).limit(limit).all()

            results = []
            for p in prices:
                p_data = {c.name: getattr(p, c.name) for c in p.__table__.columns}
                if p_data.get('indicators') and isinstance(p_data['indicators'], str):
                    try: p_data['indicators'] = json.loads(p_data['indicators'])
                    except: pass
                results.append(StockPrice(**p_data))

            return sorted(results, key=lambda x: x.date)

    async def update_analysis(self, symbol: str, analysis: Dict[str, Any]) -> None:
        with self.session_factory() as pg:
            pg.query(StockDB).filter(StockDB.symbol == symbol).update({"analysis": analysis, "updated_at": datetime.utcnow()})
            pg.commit()

    async def get_instrument_by_symbol(self, symbol: str, source: str) -> Optional[Dict[str, Any]]:
        from backend.core.postgres import InstrumentDB
        with self.session_factory() as pg:
            res = pg.query(InstrumentDB).filter(InstrumentDB.trading_symbol == symbol, InstrumentDB.source == source).first()
            if res:
                return {c.name: getattr(res, c.name) for c in res.__table__.columns}
            return None

    def _map_db_to_stock(self, db_obj: StockDB) -> Stock:
        data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}

        json_cols = {"analysis", "structured_consensus", "health_metrics", "confidence_metrics", "options_data", "financial_history"}
        for col in json_cols:
            if data.get(col) and isinstance(data[col], str):
                try: data[col] = json.loads(data[col])
                except: pass

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

            # Manual Serialize
            for col in ["dependencies", "lineage"]:
                if data.get(col): data[col] = json.dumps(data[col])

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

            results = []
            for d in query.all():
                d_data = {c.name: getattr(d, c.name) for c in d.__table__.columns}
                for col in ["dependencies", "lineage"]:
                    if d_data.get(col) and isinstance(d_data[col], str):
                        try: d_data[col] = json.loads(d_data[col])
                        except: pass
                results.append(FeatureDefinition(**d_data))
            return results

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

    async def save_workspace(self, workspace: WorkspaceState) -> None:
        with self.session_factory() as pg:
            db_ws = pg.query(WorkspaceDB).filter(WorkspaceDB.id == workspace.id).first()
            data = workspace.model_dump()

            # Manual Serialize
            for col in ["layout_config", "active_stocks", "saved_indicators"]:
                if data.get(col): data[col] = json.dumps(data[col])

            if db_ws:
                for k, v in data.items(): setattr(db_ws, k, v)
            else:
                pg.add(WorkspaceDB(**data))
            pg.commit()

    async def get_user_workspaces(self, user_id: str) -> List[WorkspaceState]:
        with self.session_factory() as pg:
            res = pg.query(WorkspaceDB).filter(WorkspaceDB.user_id == user_id).all()

            results = []
            for r in res:
                data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
                for col in ["layout_config", "active_stocks", "saved_indicators"]:
                    if data.get(col) and isinstance(data[col], str):
                        try: data[col] = json.loads(data[col])
                        except: pass
                results.append(WorkspaceState(**data))
            return results

    async def save_research_note(self, note: ResearchNote) -> None:
        with self.session_factory() as pg:
            db_note = pg.query(ResearchNoteDB).filter(ResearchNoteDB.id == note.id).first()
            data = note.model_dump()

            # Manual Serialize
            for col in ["tags", "attachments"]:
                if data.get(col): data[col] = json.dumps(data[col])

            if db_note:
                for k, v in data.items(): setattr(db_note, k, v)
            else:
                pg.add(ResearchNoteDB(**data))
            pg.commit()

    async def get_stock_notes(self, user_id: str, symbol: str) -> List[ResearchNote]:
        with self.session_factory() as pg:
            res = pg.query(ResearchNoteDB).filter(ResearchNoteDB.user_id == user_id, ResearchNoteDB.symbol == symbol).all()

            results = []
            for r in res:
                data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
                for col in ["tags", "attachments"]:
                    if data.get(col) and isinstance(data[col], str):
                        try: data[col] = json.loads(data[col])
                        except: pass
                results.append(ResearchNote(**data))
            return results

    async def save_market_regime(self, regime: MarketRegime) -> None:
        from backend.core.postgres import RegimeDB
        with self.session_factory() as pg:
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
            data = opportunity.model_dump()
            if data.get('indicators'): data['indicators'] = json.dumps(data['indicators'])
            pg.add(OpportunityDB(**data))
            pg.commit()

    async def get_active_opportunities(self, limit: int = 20) -> List[MarketOpportunity]:
        from backend.core.postgres import OpportunityDB
        with self.session_factory() as pg:
            try:
                res = pg.query(OpportunityDB).order_by(OpportunityDB.timestamp.desc()).limit(limit).all()

                results = []
                for r in res:
                    data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
                    if data.get('indicators') and isinstance(data['indicators'], str):
                        try: data['indicators'] = json.loads(data['indicators'])
                        except: data['indicators'] = []

                    results.append(MarketOpportunity(
                        id=str(data.get('id', uuid.uuid4())),
                        symbol=str(data.get('symbol', 'UNKNOWN')),
                        type=str(data.get('type', 'BREAKOUT')),
                        conviction_score=float(data.get('conviction_score', 0.0)),
                        ai_thesis=str(data.get('ai_thesis', 'Analysis pending.')),
                        indicators=data.get('indicators') if isinstance(data.get('indicators'), list) else [],
                        timestamp=data.get('timestamp', datetime.utcnow())
                    ))
                return results
            except Exception as e:
                print(f"Error fetching opportunities: {e}")
                return []

    async def save_live_signal(self, signal: LiveSignal) -> None:
        def json_serializable(data):
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
            db_sig = pg.query(LiveSignalDB).filter(LiveSignalDB.id == signal.id).first()
            data = signal.model_dump()
            if data.get('events'):
                # Deep serialize events to handle nested datetimes
                data['events'] = json.dumps(json_serializable(data['events']))

            if db_sig:
                for k, v in data.items(): setattr(db_sig, k, v)
            else:
                pg.add(LiveSignalDB(**data))
            pg.commit()

    async def get_active_live_signals(self) -> List[LiveSignal]:
        with self.session_factory() as pg:
            res = pg.query(LiveSignalDB).filter(LiveSignalDB.status == "ACTIVE").all()
            return [self._map_db_to_live_signal(r) for r in res]

    async def get_all_live_signals(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[LiveSignal]:
        with self.session_factory() as pg:
            query = pg.query(LiveSignalDB)
            if start_date:
                query = query.filter(LiveSignalDB.timestamp >= start_date)
            if end_date:
                query = query.filter(LiveSignalDB.timestamp <= end_date)
            res = query.order_by(LiveSignalDB.timestamp.desc()).all()
            return [self._map_db_to_live_signal(r) for r in res]

    def _map_db_to_live_signal(self, db_obj: LiveSignalDB) -> LiveSignal:
        data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        if data.get('events') and isinstance(data['events'], str):
            try: data['events'] = json.loads(data['events'])
            except: data['events'] = []

        if not data.get('events'): data['events'] = []
        if data.get('mfe') is None: data['mfe'] = 0.0
        if data.get('mae') is None: data['mae'] = 0.0
        return LiveSignal(**data)

    async def save_intel_report(self, report: MarketIntelligenceReport) -> None:
        from backend.core.postgres import IntelReportDB
        with self.session_factory() as pg:
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

    async def save_trade_feedback(self, feedback: TradeFeedback) -> None:
        with self.session_factory() as pg:
            db_trade = pg.query(TradeJournalDB).filter(TradeJournalDB.id == feedback.id).first()
            data = feedback.model_dump()

            # Manual Serialize
            for col in ["mistakes", "lessons"]:
                if data.get(col): data[col] = json.dumps(data[col])

            if db_trade:
                for k, v in data.items(): setattr(db_trade, k, v)
            else:
                pg.add(TradeJournalDB(**data))
            pg.commit()

    async def get_user_trades(self, user_id: str) -> List[TradeFeedback]:
        with self.session_factory() as pg:
            res = pg.query(TradeJournalDB).filter(TradeJournalDB.user_id == user_id).all()

            results = []
            for r in res:
                data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
                for col in ["mistakes", "lessons"]:
                    if data.get(col) and isinstance(data[col], str):
                        try: data[col] = json.loads(data[col])
                        except: pass
                results.append(TradeFeedback(**data))
            return results
