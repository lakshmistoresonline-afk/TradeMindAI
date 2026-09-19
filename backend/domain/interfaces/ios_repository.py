from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.domain.models.ios import MarketRegime, MarketOpportunity, MarketIntelligenceReport, LiveSignal

class IIOSRepository(ABC):
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
    async def get_signal_by_id(self, signal_id: str) -> Optional[LiveSignal]:
        pass

    @abstractmethod
    async def get_signal_provenance(self, signal_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def save_shadow_signal(self, signal: LiveSignal) -> None:
        pass

    @abstractmethod
    async def get_active_shadow_signals(self) -> List[LiveSignal]:
        pass

    @abstractmethod
    async def get_verified_shadow_signals(self) -> List[LiveSignal]:
        pass

    @abstractmethod
    async def save_intel_report(self, report: MarketIntelligenceReport) -> None:
        pass

    @abstractmethod
    async def get_latest_intel_report(self, report_type: str) -> Optional[MarketIntelligenceReport]:
        pass
