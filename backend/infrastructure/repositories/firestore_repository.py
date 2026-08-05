from typing import List, Optional, Dict, Any
from google.cloud import firestore
from backend.domain.models.stock import Stock, StockPrice
from backend.domain.interfaces.repository import IStockRepository
import datetime

class FirestoreStockRepository(IStockRepository):
    def __init__(self, db: firestore.Client):
        self.db = db

    async def get_all_stocks(self) -> List[Stock]:
        stocks_ref = self.db.collection("stocks")
        docs = stocks_ref.stream()
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

    async def update_analysis(self, symbol: str, analysis: Dict[str, Any]) -> None:
        self.db.collection("stocks").document(symbol).update({
            "analysis": analysis,
            "updated_at": datetime.datetime.utcnow()
        })
