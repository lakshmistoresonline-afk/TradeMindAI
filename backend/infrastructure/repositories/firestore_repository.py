from typing import List, Optional, Dict, Any
from google.cloud import firestore
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.models.data_platform import NewsArticle, InstitutionalFlow, FeatureVector, Prediction, FeatureDefinition, ModelMetadata, MLDataset, PortfolioHealth, Alert
from backend.domain.models.strategy import UserStrategy, PaperOrder, VirtualPortfolio
from backend.domain.interfaces.repository import IStockRepository, IDataPlatformRepository
import datetime

class FirestoreStockRepository(IStockRepository):
    def __init__(self, db: firestore.Client):
        self.db = db

    async def get_all_stocks(self, limit: int = 50, offset: int = 0) -> List[Stock]:
        stocks_ref = self.db.collection("stocks")
        # Firestore offset pagination is inefficient; using simple limit/stream for now.
        # Professional implementation would use cursor-based pagination.
        docs = stocks_ref.order_by("symbol").limit(limit).offset(offset).stream()
        return [Stock(**doc.to_dict()) for doc in docs]

    async def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        doc_ref = self.db.collection("stocks").document(symbol)
        doc = doc_ref.get()
        if doc.exists:
            return Stock(**doc.to_dict())
        return None

    async def save_stock(self, stock: Stock) -> None:
        stock_ref = self.db.collection("stocks").document(stock.symbol)
        stock_ref.set(stock.to_dict(), merge=True)

    async def save_historical_prices(self, symbol: str, prices: List[StockPrice]) -> None:
        stock_ref = self.db.collection("stocks").document(symbol)
        prices_ref = stock_ref.collection("prices")

        batch = self.db.batch()
        for price in prices:
            date_id = price.date.strftime("%Y-%m-%d")
            doc_ref = prices_ref.document(date_id)
            batch.set(doc_ref, price.model_dump())
        batch.commit()

    async def get_recent_prices(self, symbol: str, limit: int = 250) -> List[StockPrice]:
        prices_ref = self.db.collection("stocks").document(symbol).collection("prices")
        # Get last N days by date ID descending
        docs = prices_ref.order_by("date", direction=firestore.Query.DESCENDING).limit(limit).stream()

        results = []
        for doc in docs:
            results.append(StockPrice(**doc.to_dict()))

        # Reverse to get chronological order
        return sorted(results, key=lambda x: x.date)

    async def update_analysis(self, symbol: str, analysis: Dict[str, Any]) -> None:
        self.db.collection("stocks").document(symbol).update({
            "analysis": analysis,
            "updated_at": datetime.datetime.utcnow()
        })

class FirestoreDataPlatformRepository(IDataPlatformRepository):
    def __init__(self, db: firestore.Client):
        self.db = db

    async def save_news(self, articles: List[NewsArticle]) -> None:
        batch = self.db.batch()
        for article in articles:
            doc_ref = self.db.collection("news").document(article.id)
            batch.set(doc_ref, article.model_dump())
        batch.commit()

    async def get_latest_news(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        docs = self.db.collection("news")\
            .where("symbol", "==", symbol)\
            .order_by("published_at", direction=firestore.Query.DESCENDING)\
            .limit(limit)\
            .stream()
        return [NewsArticle(**doc.to_dict()) for doc in docs]

    async def save_institutional_flow(self, flow: InstitutionalFlow) -> None:
        date_id = flow.date.strftime("%Y-%m-%d")
        self.db.collection("institutional_flow").document(date_id).set(flow.model_dump())

    async def get_latest_institutional_flow(self) -> Optional[InstitutionalFlow]:
        docs = self.db.collection("institutional_flow")\
            .order_by("date", direction=firestore.Query.DESCENDING)\
            .limit(1)\
            .stream()
        for doc in docs:
            return InstitutionalFlow(**doc.to_dict())
        return None

    async def save_feature_vector(self, vector: FeatureVector) -> None:
        date_id = vector.date.strftime("%Y-%m-%d")
        doc_id = f"{vector.symbol}_{date_id}_{vector.version}"
        self.db.collection("feature_store").document(doc_id).set(vector.model_dump())

    async def save_prediction(self, prediction: Prediction) -> None:
        date_id = prediction.date.strftime("%Y-%m-%d")
        doc_id = f"{prediction.symbol}_{date_id}_{prediction.model_version}"
        self.db.collection("predictions").document(doc_id).set(prediction.model_dump())

    async def save_portfolio_health(self, health: PortfolioHealth) -> None:
        self.db.collection("portfolio_health").document(health.user_id).set(health.model_dump())

    async def get_portfolio_health(self, user_id: str) -> Optional[PortfolioHealth]:
        doc = self.db.collection("portfolio_health").document(user_id).get()
        if doc.exists:
            return PortfolioHealth(**doc.to_dict())
        return None

    async def save_alert(self, alert: Alert) -> None:
        self.db.collection("alerts").document(alert.id).set(alert.model_dump())

    async def get_active_alerts(self, limit: int = 20) -> List[Alert]:
        docs = self.db.collection("alerts")\
            .where("is_read", "==", False)\
            .order_by("created_at", direction=firestore.Query.DESCENDING)\
            .limit(limit).stream()
        return [Alert(**doc.to_dict()) for doc in docs]

    async def save_earnings(self, earnings: EarningsData) -> None:
        doc_id = f"{earnings.symbol}_{earnings.date.strftime('%Y-%m-%d')}"
        self.db.collection("earnings").document(doc_id).set(earnings.model_dump())

    async def get_latest_earnings(self, symbol: str) -> Optional[EarningsData]:
        docs = self.db.collection("earnings")\
            .where("symbol", "==", symbol)\
            .order_by("date", direction=firestore.Query.DESCENDING)\
            .limit(1).stream()
        for doc in docs:
            return EarningsData(**doc.to_dict())
        return None

    async def save_options_chain(self, chain: OptionsChain) -> None:
        self.db.collection("options_chains").document(chain.symbol).set(chain.model_dump())

    async def get_latest_options_chain(self, symbol: str) -> Optional[OptionsChain]:
        doc = self.db.collection("options_chains").document(symbol).get()
        if doc.exists:
            return OptionsChain(**doc.to_dict())
        return None

    async def save_model_metadata(self, metadata: ModelMetadata) -> None:
        doc_id = f"{metadata.symbol}_{metadata.version}"
        self.db.collection("model_registry").document(doc_id).set(metadata.model_dump())

    async def get_champion_model(self, symbol: str) -> Optional[ModelMetadata]:
        docs = self.db.collection("model_registry")\
            .where("symbol", "==", symbol)\
            .where("is_champion", "==", True)\
            .limit(1).stream()
        for doc in docs:
            return ModelMetadata(**doc.to_dict())
        return None

    async def save_ml_dataset(self, dataset: MLDataset) -> None:
        self.db.collection("ml_datasets").document(dataset.id).set(dataset.model_dump())

    async def get_features_by_range(self, symbol: str, start_date: datetime, end_date: datetime) -> List[FeatureVector]:
        docs = self.db.collection("feature_store")\
            .where("symbol", "==", symbol)\
            .where("date", ">=", start_date)\
            .where("date", "<=", end_date)\
            .order_by("date").stream()
        return [FeatureVector(**doc.to_dict()) for doc in docs]

    async def register_device(self, user_id: str, device_info: Dict[str, Any]) -> None:
        doc_id = f"{user_id}_{device_info['device_id']}"
        self.db.collection("devices").document(doc_id).set({
            **device_info,
            "user_id": user_id,
            "last_active": datetime.datetime.utcnow()
        })

    async def get_user_devices(self, user_id: str) -> List[Dict[str, Any]]:
        docs = self.db.collection("devices").where("user_id", "==", user_id).stream()
        return [doc.to_dict() for doc in docs]

    async def save_feature_definition(self, definition: FeatureDefinition) -> None:
        doc_id = f"{definition.name}_{definition.version}"
        self.db.collection("feature_definitions").document(doc_id).set(definition.model_dump())

    async def get_feature_definitions(self, category: Optional[str] = None) -> List[FeatureDefinition]:
        query = self.db.collection("feature_definitions")
        if category:
            query = query.where("category", "==", category)
        docs = query.stream()
        return [FeatureDefinition(**doc.to_dict()) for doc in docs]

    async def save_strategy(self, strategy: UserStrategy) -> None:
        self.db.collection("strategies").document(strategy.id).set(strategy.model_dump())

    async def get_user_strategies(self, user_id: str) -> List[UserStrategy]:
        docs = self.db.collection("strategies").where("user_id", "==", user_id).stream()
        return [UserStrategy(**doc.to_dict()) for doc in docs]

    async def save_paper_order(self, order: PaperOrder) -> None:
        self.db.collection("paper_orders").document(order.id).set(order.model_dump())

    async def get_virtual_portfolio(self, user_id: str) -> Optional[VirtualPortfolio]:
        doc = self.db.collection("virtual_portfolios").document(user_id).get()
        if doc.exists:
            return VirtualPortfolio(**doc.to_dict())
        return None

    async def save_virtual_portfolio(self, portfolio: VirtualPortfolio) -> None:
        self.db.collection("virtual_portfolios").document(portfolio.user_id).set(portfolio.model_dump())
