from typing import List, Dict, Any
import datetime
from datetime import timezone
from backend.domain.models.ios import LiveSignal
from backend.domain.interfaces.ios_repository import IIOSRepository
from backend.services.outcome_service import OutcomeService
from backend.core.container import container

class SignalAuditor:
    """
    Forensic Signal Auditor (V2.3 Hardened).
    Authoritatively resolves signal outcomes using verified price action.
    """
    def __init__(self, repo: IIOSRepository):
        self.repo = repo

    async def audit_active_signals(self):
        """
        Scans non-terminal signals and synchronizes state with market reality.
        """
        all_signals = await self.repo.get_all_live_signals()
        non_terminal = [s for s in all_signals if s.status not in OutcomeService.TERMINAL_STATES]

        for signal in non_terminal:
            try:
                await self._audit_single_signal(signal)
            except Exception as e:
                print(f"[Auditor] Failed to audit {signal.id} ({signal.symbol}): {e}")

    async def _audit_single_signal(self, signal: LiveSignal):
        # 1. Fetch Authoritative History
        provider = container.provider
        # Fetch from signal start until now
        df = await provider.get_history(signal.symbol, start_date=signal.timestamp)

        if df.empty:
            return

        # 2. Forensic Outcome Resolution
        outcome = OutcomeService.evaluate_signal_outcome(signal, df)

        # 3. Apply State Transition
        if outcome["status"] != signal.status:
            from backend.services.signal_lifecycle_service import SignalLifecycleService
            await SignalLifecycleService.transition_signal(signal.id, outcome["status"], outcome)
            print(f"[Auditor] {signal.symbol} Transitioned: {signal.status} -> {outcome['status']}")
