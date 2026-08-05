from typing import List, Optional, Dict, Any
from google.cloud import firestore
from backend.domain.models.ios import WorkspaceState, ResearchNote, MarketRegime, MarketOpportunity, MarketIntelligenceReport
from backend.domain.interfaces.ios_repository import IIOSRepository
import datetime

class FirestoreIOSRepository(IIOSRepository):
    def __init__(self, db: firestore.Client):
        self.db = db

    async def save_workspace(self, workspace: WorkspaceState) -> None:
        self.db.collection("workspaces").document(workspace.id).set(workspace.model_dump())

    async def get_user_workspaces(self, user_id: str) -> List[WorkspaceState]:
        docs = self.db.collection("workspaces").where("user_id", "==", user_id).stream()
        return [WorkspaceState(**doc.to_dict()) for doc in docs]

    async def save_research_note(self, note: ResearchNote) -> None:
        self.db.collection("research_notes").document(note.id).set(note.model_dump())

    async def get_stock_notes(self, user_id: str, symbol: str) -> List[ResearchNote]:
        docs = self.db.collection("research_notes")\
            .where("user_id", "==", user_id)\
            .where("symbol", "==", symbol)\
            .order_by("created_at", direction=firestore.Query.DESCENDING).stream()
        return [ResearchNote(**doc.to_dict()) for doc in docs]

    async def save_market_regime(self, regime: MarketRegime) -> None:
        date_id = regime.date.strftime("%Y-%m-%d")
        self.db.collection("market_regimes").document(date_id).set(regime.model_dump())

    async def get_latest_regime(self) -> Optional[MarketRegime]:
        docs = self.db.collection("market_regimes").order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs:
            return MarketRegime(**doc.to_dict())
        return None

    async def save_opportunity(self, opportunity: MarketOpportunity) -> None:
        self.db.collection("opportunities").document(opportunity.id).set(opportunity.model_dump())

    async def get_active_opportunities(self, limit: int = 20) -> List[MarketOpportunity]:
        docs = self.db.collection("opportunities").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [MarketOpportunity(**doc.to_dict()) for doc in docs]

    async def save_intel_report(self, report: MarketIntelligenceReport) -> None:
        self.db.collection("intel_reports").document(report.id).set(report.model_dump())

    async def get_latest_intel_report(self, report_type: str) -> Optional[MarketIntelligenceReport]:
        docs = self.db.collection("intel_reports")\
            .where("type", "==", report_type)\
            .order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        for doc in docs:
            return MarketIntelligenceReport(**doc.to_dict())
        return None
