from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.domain.models.ios import WorkspaceState, ResearchNote, MarketRegime, MarketOpportunity, MarketIntelligenceReport, TradeFeedback, LiveSignal

class IIOSRepository(ABC):
    @abstractmethod
    async def save_workspace(self, workspace: WorkspaceState) -> None:
        pass

    @abstractmethod
    async def get_user_workspaces(self, user_id: str) -> List[WorkspaceState]:
        pass

    @abstractmethod
    async def save_research_note(self, note: ResearchNote) -> None:
        pass

    @abstractmethod
    async def get_stock_notes(self, user_id: str, symbol: str) -> List[ResearchNote]:
        pass

    @abstractmethod
    async def save_market_regime(self, regime: MarketRegime) -> None:
        pass

    @abstractmethod
    async def get_latest_regime(self) -> Optional[MarketRegime]:
        pass

    @abstractmethod
    async def save_opportunity(self, opportunity: MarketOpportunity) -> None:
        pass

    @abstractmethod
    async def get_active_opportunities(self, limit: int = 20) -> List[MarketOpportunity]:
        pass

    @abstractmethod
    async def save_live_signal(self, signal: LiveSignal) -> None:
        pass

    @abstractmethod
    async def get_active_live_signals(self) -> List[LiveSignal]:
        pass

    @abstractmethod
    async def get_all_live_signals(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[LiveSignal]:
        pass

    @abstractmethod
    async def save_intel_report(self, report: MarketIntelligenceReport) -> None:
        pass

    @abstractmethod
    async def get_latest_intel_report(self, report_type: str) -> Optional[MarketIntelligenceReport]:
        pass

    @abstractmethod
    async def save_trade_feedback(self, feedback: TradeFeedback) -> None:
        pass

    @abstractmethod
    async def get_user_trades(self, user_id: str) -> List[TradeFeedback]:
        pass
