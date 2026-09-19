from typing import List, Optional, Dict, Any, Callable
from sqlalchemy.orm import Session
from datetime import datetime
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.interfaces.repository import IStockRepository, IDataPlatformRepository
from backend.core.postgres import StockDB, PriceDB, RegimeDB, PredictionDB, IntelReportDB, FeatureDefinitionDB, LiveSignalDB, ModelMetadataDB, ShadowSignalDB, ShadowProvenanceDB
from backend.core.duckdb_engine import analytical_engine
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow, FeatureVector, Prediction, FeatureDefinition, ModelMetadata, MLDataset, Alert, EarningsData, OptionsChain
from backend.domain.models.ios import MarketRegime, MarketOpportunity, LiveSignal, WorkspaceState, ResearchNote, TradeFeedback, MarketIntelligenceReport
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
            filtered_data = {k: v for k, v in data.items() if k in db_columns}
            for k in json_cols:
                if k in filtered_data:
                    filtered_data[k] = json.dumps(json_serializable(filtered_data[k])) if filtered_data[k] is not None else None
            if db_stock:
                for key, value in filtered_data.items(): setattr(db_stock, key, value)
            else:
                pg.add(StockDB(**filtered_data))
            pg.commit()

    async def save_historical_prices(self, symbol: str, prices: List[StockPrice]) -> None:
        if not prices: return
        def clean_indicators(indicators):
            if not indicators: return None
            import math
            return {k: (None if isinstance(v, float) and (math.isnan(v) or math.isinf(v)) else v) for k, v in indicators.items()}

        with self.session_factory() as pg:
            existing_dates = {d[0].date() if hasattr(d[0], 'date') else d[0] for d in pg.query(PriceDB.date).filter(PriceDB.symbol == symbol).all()}
            to_add = []
            for p in prices:
                p_date = p.date.date() if hasattr(p.date, 'date') else p.date
                if p_date not in existing_dates:
                    to_add.append(PriceDB(
                        symbol=symbol, date=p.date, open=p.open, high=p.high, low=p.low, close=p.close,
                        volume=p.volume, open_interest=p.open_interest, source=p.source,
                        indicators=json.dumps(clean_indicators(p.indicators)) if p.indicators else None
                    ))
            if to_add: pg.bulk_save_objects(to_add)
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
            pg.query(StockDB).filter(StockDB.symbol == symbol).update({"analysis": json.dumps(analysis), "updated_at": datetime.utcnow()})
            pg.commit()

    async def save_instruments(self, instruments: List[Dict[str, Any]]) -> None:
        from backend.core.postgres import InstrumentDB
        with self.session_factory() as pg:
            for inst_data in instruments:
                inst_id = inst_data.get('id')
                if not inst_id: continue
                db_inst = pg.query(InstrumentDB).filter(InstrumentDB.id == inst_id).first()
                if db_inst:
                    for k, v in inst_data.items(): setattr(db_inst, k, v)
                else:
                    pg.add(InstrumentDB(**inst_data))
            pg.commit()

    async def get_instruments(self, underlying_symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        from backend.core.postgres import InstrumentDB
        with self.session_factory() as pg:
            query = pg.query(InstrumentDB)
            if underlying_symbol: query = query.filter(InstrumentDB.underlying_symbol == underlying_symbol)
            res = query.all()
            return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in res]

    def _map_db_to_stock(self, db_obj: StockDB) -> Stock:
        try:
            data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
            json_cols = {"analysis", "structured_consensus", "health_metrics", "confidence_metrics", "options_data", "financial_history"}
            for col in json_cols:
                if data.get(col) and isinstance(data[col], str):
                    try: data[col] = json.loads(data[col])
                    except: data[col] = None
            if data.get('market_cap'): data['market_cap'] = float(data['market_cap'])
            return Stock(**data)
        except Exception as e:
            return Stock(symbol=getattr(db_obj, 'symbol', 'ERROR'), name="Data Corrupted")

class HybridDataPlatformRepository(IDataPlatformRepository):
    def __init__(self, session_factory: Callable[[], Session], firestore_db: Any):
        self.session_factory = session_factory
        self.fs = firestore_db
        self.duck = analytical_engine

    async def save_news(self, articles: List[NewsArticle]) -> None:
        from backend.core.postgres import NewsDB
        with self.session_factory() as pg:
            for art in articles:
                if not pg.query(NewsDB).filter(NewsDB.id == art.id).first(): pg.add(NewsDB(**art.model_dump()))
            pg.commit()

    async def get_latest_news(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        from backend.core.postgres import NewsDB
        with self.session_factory() as pg:
            res = pg.query(NewsDB).filter(NewsDB.symbol == symbol).order_by(NewsDB.published_at.desc()).limit(limit).all()
            return [NewsArticle(**{c.name: getattr(r, c.name) for c in r.__table__.columns}) for r in res]

    async def save_institutional_flow(self, flow: InstitutionalFlow) -> None:
        self.fs.collection("institutional_flow").document(flow.date.strftime("%Y-%m-%d")).set(flow.model_dump())

    async def get_latest_institutional_flow(self) -> Optional[InstitutionalFlow]:
        from google.cloud import firestore
        docs = self.fs.collection("institutional_flow").order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs: return InstitutionalFlow(**doc.to_dict())
        return None

    async def save_feature_vector(self, vector: FeatureVector) -> None:
        df = pd.DataFrame([{"date": vector.date, **vector.features, "target": vector.target}])
        self.duck.ingest_features(vector.symbol, df)

    async def save_prediction(self, prediction: Prediction) -> None:
        from backend.core.postgres import PredictionDB
        with self.session_factory() as pg:
            pg.add(PredictionDB(
                id=prediction.id, symbol=prediction.symbol, timestamp=prediction.timestamp, model_version=prediction.model_version,
                feature_version=prediction.feature_version, prediction=prediction.prediction, probability=prediction.probability,
                expected_value=prediction.expected_value, direction=prediction.direction, confidence=prediction.confidence,
                regime=prediction.regime, metadata_json=json.dumps(prediction.metadata) if prediction.metadata else None,
                created_at=prediction.created_at
            ))
            pg.commit()

    async def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        from backend.core.postgres import PredictionDB
        with self.session_factory() as pg:
            res = pg.query(PredictionDB).filter(PredictionDB.id == prediction_id).first()
            return self._map_db_to_prediction(res) if res else None

    async def get_predictions(self, symbol: Optional[str] = None, limit: int = 100) -> List[Prediction]:
        from backend.core.postgres import PredictionDB
        with self.session_factory() as pg:
            query = pg.query(PredictionDB)
            if symbol: query = query.filter(PredictionDB.symbol == symbol)
            res = query.order_by(PredictionDB.timestamp.desc()).limit(limit).all()
            return [self._map_db_to_prediction(r) for r in res]

    def _map_db_to_prediction(self, db_obj: Any) -> Prediction:
        data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        if data.get('metadata_json'): data['metadata'] = json.loads(data['metadata_json'])
        if 'date' in data: data['timestamp'] = data['date']
        return Prediction(**data)

    async def save_alert(self, alert: Alert) -> None: self.fs.collection("alerts").document(alert.id).set(alert.model_dump())
    async def get_active_alerts(self, limit: int = 20) -> List[Alert]:
        docs = self.fs.collection("alerts").where("is_read", "==", False).limit(limit).stream()
        return [Alert(**doc.to_dict()) for doc in docs]

    async def save_earnings(self, earnings: EarningsData) -> None:
        from backend.core.postgres import EarningsDB
        with self.session_factory() as pg:
            doc_id = f"{earnings.symbol}_{earnings.date.strftime('%Y-%m-%d')}"
            if not pg.query(EarningsDB).filter(EarningsDB.id == doc_id).first(): pg.add(EarningsDB(id=doc_id, **earnings.model_dump()))
            pg.commit()

    async def get_latest_earnings(self, symbol: str) -> Optional[EarningsData]:
        from backend.core.postgres import EarningsDB
        with self.session_factory() as pg:
            res = pg.query(EarningsDB).filter(EarningsDB.symbol == symbol).order_by(EarningsDB.date.desc()).first()
            return EarningsData(**{c.name: getattr(res, c.name) for c in res.__table__.columns}) if res else None

    async def save_options_chain(self, chain: OptionsChain) -> None:
        from backend.core.postgres import OptionsChainDB
        with self.session_factory() as pg:
            doc_id = f"{chain.symbol}_{chain.expiry.strftime('%Y-%m-%d')}"
            db_obj = pg.query(OptionsChainDB).filter(OptionsChainDB.id == doc_id).first()
            data = chain.model_dump()
            data['greeks_aggregate'] = json.dumps(data['greeks_aggregate'])
            if db_obj:
                for k, v in data.items(): setattr(db_obj, k, v)
            else: pg.add(OptionsChainDB(id=doc_id, **data))
            pg.commit()

    async def get_latest_options_chain(self, symbol: str) -> Optional[OptionsChain]:
        from backend.core.postgres import OptionsChainDB
        with self.session_factory() as pg:
            res = pg.query(OptionsChainDB).filter(OptionsChainDB.symbol == symbol).order_by(OptionsChainDB.last_updated.desc()).first()
            if not res: return None
            data = {c.name: getattr(res, c.name) for c in res.__table__.columns}
            if data.get('greeks_aggregate'): data['greeks_aggregate'] = json.loads(data['greeks_aggregate'])
            return OptionsChain(**data)

    async def save_feature_definition(self, definition: FeatureDefinition) -> None:
        with self.session_factory() as pg:
            db_def = pg.query(FeatureDefinitionDB).filter(FeatureDefinitionDB.name == definition.name).first()
            data = definition.model_dump()
            for col in ["dependencies", "lineage"]:
                if data.get(col): data[col] = json.dumps(data[col])
            if db_def:
                for k, v in data.items():
                    if hasattr(db_def, k): setattr(db_def, k, v)
            else: pg.add(FeatureDefinitionDB(**data))
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

    async def save_model_metadata(self, metadata: ModelMetadata) -> None:
        from backend.core.postgres import ModelMetadataDB
        with self.session_factory() as pg:
            db_obj = pg.query(ModelMetadataDB).filter(ModelMetadataDB.name == metadata.name).first()
            data = metadata.model_dump()
            for col in ["hyperparameters", "feature_importances", "calibration_metadata"]:
                if data.get(col): data[col] = json.dumps(data[col])
            db_columns = {c.name for c in ModelMetadataDB.__table__.columns}
            filtered_data = {k: v for k, v in data.items() if k in db_columns}

            # If this is a new champion, demote old ones
            if metadata.is_champion:
                pg.query(ModelMetadataDB).filter(
                    ModelMetadataDB.symbol == metadata.symbol,
                    ModelMetadataDB.horizon == (metadata.horizon or "SWING")
                ).update({"is_champion": False})

            if db_obj:
                for k, v in filtered_data.items(): setattr(db_obj, k, v)
            else: pg.add(ModelMetadataDB(**filtered_data))
            pg.commit()

    async def get_champion_model(self, symbol: str, horizon: str = "SWING") -> Optional[ModelMetadata]:
        from backend.core.postgres import ModelMetadataDB
        with self.session_factory() as pg:
            r = pg.query(ModelMetadataDB).filter(
                ModelMetadataDB.symbol == symbol,
                ModelMetadataDB.is_champion == True,
                ModelMetadataDB.horizon == horizon
            ).order_by(ModelMetadataDB.last_trained.desc()).first()
            return self._map_db_to_model_metadata(r) if r else None

    async def get_model_history(self, symbol: str, limit: int = 10) -> List[ModelMetadata]:
        from backend.core.postgres import ModelMetadataDB
        with self.session_factory() as pg:
            res = pg.query(ModelMetadataDB).filter(ModelMetadataDB.symbol == symbol).order_by(ModelMetadataDB.last_trained.desc()).limit(limit).all()
            return [self._map_db_to_model_metadata(r) for r in res]

    async def get_all_champion_models(self) -> List[ModelMetadata]:
        from backend.core.postgres import ModelMetadataDB
        with self.session_factory() as pg:
            res = pg.query(ModelMetadataDB).filter(ModelMetadataDB.is_champion == True).all()
            return [self._map_db_to_model_metadata(r) for r in res]

    def _map_db_to_model_metadata(self, db_obj: ModelMetadataDB) -> ModelMetadata:
        data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
        for col in ["hyperparameters", "feature_importances", "calibration_metadata"]:
            if data.get(col) and isinstance(data[col], str):
                try: data[col] = json.loads(data[col])
                except: pass
        return ModelMetadata(**data)

    async def save_ml_dataset(self, dataset: MLDataset) -> None:
        from backend.core.postgres import MLDatasetDB
        with self.session_factory() as pg:
            data = dataset.model_dump()
            data['features_included'] = json.dumps(data['features_included'])
            pg.add(MLDatasetDB(**data))
            pg.commit()

    async def get_features_by_range(self, symbol: str, start_date: datetime, end_date: datetime, horizon: str = "SWING") -> List[FeatureVector]:
        df = self.duck.create_ml_dataset(symbol, start_date.isoformat(), end_date.isoformat())
        results = []
        target_col = f"target_{horizon.lower()}"
        target_cols = [f"target_{h.lower()}" for h in ["SHORT", "SWING", "LONG"]]
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            target = row_dict.get(target_col)
            date = row_dict.pop('date')
            for col in target_cols: row_dict.pop(col, None)
            row_dict.pop('target', None)
            results.append(FeatureVector(
                symbol=symbol, date=date, version="v1.0.0",
                features={k: v for k, v in row_dict.items() if isinstance(v, (int, float, bool))},
                target=target
            ))
        return results

class HybridIOSRepository(IIOSRepository):
    def __init__(self, session_factory: Callable[[], Session], firestore_db: Any):
        self.session_factory = session_factory
        self.fs = firestore_db

    async def save_market_regime(self, regime: MarketRegime) -> None:
        with self.session_factory() as pg:
            db_regime = RegimeDB(date=regime.date, regime=regime.regime, risk_mode=regime.risk_mode, sentiment_score=regime.sentiment_score, description=regime.description, volatility_index=regime.volatility_index)
            pg.add(db_regime)
            pg.commit()

    async def get_latest_regime(self) -> Optional[MarketRegime]:
        with self.session_factory() as pg:
            r = pg.query(RegimeDB).order_by(RegimeDB.date.desc()).first()
            if r: return MarketRegime(date=r.date, regime=r.regime, risk_mode=r.risk_mode, sentiment_score=r.sentiment_score or 0.5, volatility_index=r.volatility_index, description=r.description)
            return None

    async def save_opportunity(self, opportunity: MarketOpportunity) -> None:
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
                    results.append(MarketOpportunity(id=str(data.get('id', uuid.uuid4())), symbol=str(data.get('symbol', 'UNKNOWN')), type=str(data.get('type', 'BREAKOUT')), conviction_score=float(data.get('conviction_score', 0.0)), ai_thesis=str(data.get('ai_thesis', 'Analysis pending.')), indicators=data.get('indicators') if isinstance(data.get('indicators'), list) else [], timestamp=data.get('timestamp', datetime.utcnow())))
                return results
            except: return []

    async def save_live_signal(self, signal: LiveSignal) -> None:
        with self.session_factory() as pg:
            db_sig = pg.query(LiveSignalDB).filter(LiveSignalDB.id == signal.id).first()
            data = signal.model_dump()
            for col in ['events', 'provenance']:
                if data.get(col) is not None: data[col] = json.dumps(data[col], default=str)
            db_columns = {c.name for c in LiveSignalDB.__table__.columns}
            filtered_data = {k: v for k, v in data.items() if k in db_columns}
            if db_sig:
                for k, v in filtered_data.items(): setattr(db_sig, k, v)
            else: pg.add(LiveSignalDB(**filtered_data))
            pg.commit()

    async def get_active_live_signals(self) -> List[LiveSignal]:
        with self.session_factory() as pg:
            res = pg.query(LiveSignalDB).filter(LiveSignalDB.status.in_(["ACTIVE", "WAITING_FOR_ENTRY", "ENTRY_TRIGGERED"])).order_by(LiveSignalDB.timestamp.desc()).all()
            return [self._map_db_to_live_signal(r) for r in res]

    async def get_all_live_signals(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[LiveSignal]:
        with self.session_factory() as pg:
            query = pg.query(LiveSignalDB)
            if start_date: query = query.filter(LiveSignalDB.timestamp >= start_date)
            if end_date: query = query.filter(LiveSignalDB.timestamp <= end_date)
            res = query.order_by(LiveSignalDB.timestamp.desc()).all()
            return [self._map_db_to_live_signal(r) for r in res]

    def _map_db_to_live_signal(self, db_obj: Any) -> LiveSignal:
        try:
            data = {c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns}
            for col in ['events', 'provenance']:
                if data.get(col) and isinstance(data[col], str):
                    try: data[col] = json.loads(data[col])
                    except: data[col] = [] if col == 'events' else {}
                if data.get(col) is None: data[col] = [] if col == 'events' else {}
            numeric_fields = ['entry_price', 'target_price', 'stop_price', 'conviction', 'profit_pct', 'mfe', 'mae', 'trigger_price', 'strike', 'outcome_price']
            import math
            for field in numeric_fields:
                val = data.get(field)
                if val is None or (isinstance(val, float) and not math.isfinite(val)):
                    if field == 'conviction': data[field] = 50.0
                    elif field == 'entry_price': data[field] = 0.0
                    elif field in ['mfe', 'mae']: data[field] = 0.0
                    elif field == 'profit_pct': data[field] = 0.0
                    else: data[field] = None
            return LiveSignal(**data)
        except: return LiveSignal(id=str(uuid.uuid4()), symbol="ERROR", direction="LONG", conviction=0, entry_price=0, status="ERROR")

    async def get_signal_by_id(self, signal_id: str) -> Optional[LiveSignal]:
        with self.session_factory() as pg:
            res = pg.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal_id).first()
            return self._map_db_to_live_signal(res) if res else None

    async def get_signal_provenance(self, signal_id: str) -> Optional[Dict[str, Any]]:
        with self.session_factory() as pg:
            res = pg.query(ShadowProvenanceDB).filter(ShadowProvenanceDB.signal_id == signal_id).first()
            return {c.name: getattr(res, c.name) for c in res.__table__.columns} if res else None

    async def save_shadow_signal(self, signal: LiveSignal) -> None:
        with self.session_factory() as pg:
            db_sig = pg.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal.id).first()
            data = signal.model_dump()
            db_columns = {c.name for c in ShadowSignalDB.__table__.columns}
            filtered = {k: v for k, v in data.items() if k in db_columns}
            if db_sig:
                for k, v in filtered.items(): setattr(db_sig, k, v)
            else: pg.add(ShadowSignalDB(**filtered))
            pg.commit()

    async def get_active_shadow_signals(self) -> List[LiveSignal]:
        with self.session_factory() as pg:
            res = pg.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()
            return [self._map_db_to_live_signal(r) for r in res]

    async def get_verified_shadow_signals(self) -> List[LiveSignal]:
        with self.session_factory() as pg:
            res = pg.query(ShadowSignalDB).filter(ShadowSignalDB.outcome_verified == True).all()
            return [self._map_db_to_live_signal(r) for r in res]

    # --- RESTORING ABSENT CANONICAL IIOSREPOSITORY CONFLICT INTERFACES ---
    async def save_workspace(self, workspace: WorkspaceState) -> None:
        self.fs.collection("workspaces").document(workspace.id).set(workspace.model_dump())

    async def get_user_workspaces(self, user_id: str) -> List[WorkspaceState]:
        docs = self.fs.collection("workspaces").where("user_id", "==", user_id).stream()
        return [WorkspaceState(**doc.to_dict()) for doc in docs]

    async def save_research_note(self, note: ResearchNote) -> None:
        self.fs.collection("research_notes").document(note.id).set(note.model_dump())

    async def get_stock_notes(self, user_id: str, symbol: str) -> List[ResearchNote]:
        docs = self.fs.collection("research_notes").where("user_id", "==", user_id).where("symbol", "==", symbol).stream()
        return [ResearchNote(**doc.to_dict()) for doc in docs]

    async def save_intel_report(self, report: MarketIntelligenceReport) -> None:
        self.fs.collection("intel_reports").document(report.id).set(report.model_dump())

    async def get_latest_intel_report(self, report_type: str) -> Optional[MarketIntelligenceReport]:
        from google.cloud import firestore
        docs = self.fs.collection("intel_reports").where("type", "==", report_type).order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs: return MarketIntelligenceReport(**doc.to_dict())
        return None

    async def save_trade_feedback(self, feedback: TradeFeedback) -> None:
        self.fs.collection("trade_journal").document(feedback.id).set(feedback.model_dump())

    async def get_user_trades(self, user_id: str) -> List[TradeFeedback]:
        docs = self.fs.collection("trade_journal").where("user_id", "==", user_id).stream()
        return [TradeFeedback(**doc.to_dict()) for doc in docs]

