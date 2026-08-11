from typing import List, Dict, Any
import datetime
import yfinance as yf
from backend.domain.models.ios import LiveSignal
from backend.infrastructure.repositories.firestore_ios_repository import FirestoreIOSRepository

class SignalAuditor:
    def __init__(self, repo: FirestoreIOSRepository):
        self.repo = repo

    async def audit_active_signals(self):
        """
        Scans all ACTIVE live signals and updates their outcome based on price action.
        """
        active_signals = await self.repo.get_active_live_signals()

        for signal in active_signals:
            await self._audit_single_signal(signal)

    async def _audit_single_signal(self, signal: LiveSignal):
        # 1. Fetch Price Action since signal timestamp
        ticker = yf.Ticker(f"{signal.symbol}.NS")
        # Get enough data to cover from signal timestamp to now
        df = ticker.history(start=signal.timestamp.date())

        if df.empty:
            return

        # 2. Setup Directional Parameters
        entry = signal.entry_price
        target = signal.target_price
        stop = signal.stop_loss_price
        direction = getattr(signal, 'direction', 'LONG') # Fallback to LONG for legacy records

        # Filter for data after the signal timestamp
        future_df = df[df.index >= signal.timestamp]

        if future_df.empty:
            return

        current_mfe = signal.mfe
        current_mae = signal.mae

        new_status = "ACTIVE"
        outcome_date = None
        profit_pct = None

        for date, row in future_df.iterrows():
            high = row["High"]
            low = row["Low"]
            close = row["Close"]

            # 3. Directional Calculation Logic (Vision 2.2)
            if direction == "LONG":
                mfe_val = ((high - entry) / entry) * 100
                mae_val = ((low - entry) / entry) * 100

                # Check Outcome
                if target and high >= target:
                    new_status = "TARGET_HIT"
                    outcome_date = date
                    profit_pct = ((target - entry) / entry) * 100
                    break
                if stop and low <= stop:
                    new_status = "STOP_LOSS"
                    outcome_date = date
                    profit_pct = ((stop - entry) / entry) * 100
                    break
            else: # SHORT
                mfe_val = ((entry - low) / entry) * 100
                mae_val = ((entry - high) / entry) * 100

                # Check Outcome
                if target and low <= target:
                    new_status = "TARGET_HIT"
                    outcome_date = date
                    profit_pct = ((entry - target) / entry) * 100
                    break
                if stop and high >= stop:
                    new_status = "STOP_LOSS"
                    outcome_date = date
                    profit_pct = ((entry - stop) / entry) * 100
                    break

            # Update Running MFE/MAE
            if mfe_val > current_mfe: current_mfe = mfe_val
            if mae_val < current_mae: current_mae = mae_val

            # 4. Check Expiry (Intraday: end of day, Swing: 30 days)
            age = (datetime.datetime.utcnow() - signal.timestamp).days
            if signal.timeframe == "INTRADAY" and date.date() > signal.timestamp.date():
                new_status = "EXPIRED"
                outcome_date = date
                profit_pct = ((close - entry) / entry) * 100 if direction == "LONG" else ((entry - close) / entry) * 100
                break
            elif age > 30:
                new_status = "EXPIRED"
                outcome_date = date
                profit_pct = ((close - entry) / entry) * 100 if direction == "LONG" else ((entry - close) / entry) * 100
                break

        # 5. Finalize Snapshot
        signal.mfe = current_mfe
        signal.mae = current_mae
        signal.status = new_status
        if outcome_date:
            signal.outcome_date = outcome_date
            signal.profit_pct = profit_pct

        await self.repo.save_live_signal(signal)
