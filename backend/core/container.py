from backend.core.database import db_client
from backend.infrastructure.repositories.firestore_repository import FirestoreStockRepository
from backend.infrastructure.repositories.yfinance_provider import YFinanceProvider
from backend.infrastructure.repositories.groq_provider import GroqAIProvider
from backend.services.stock_service import StockService

# Simple Singleton Container for Service Injection
class Container:
    def __init__(self):
        self.repository = FirestoreStockRepository(db_client)
        self.provider = YFinanceProvider()
        self.ai_provider = GroqAIProvider()
        self.stock_service = StockService(self.repository, self.provider)

container = Container()

def get_stock_service():
    return container.stock_service

def get_ai_provider():
    return container.ai_provider
