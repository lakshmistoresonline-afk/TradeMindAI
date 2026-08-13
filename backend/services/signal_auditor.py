from typing import List, Dict, Any
import datetime
import yfinance as yf
from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.domain.interfaces.ios_repository import IIOSRepository

class SignalAuditor:
    def __init__(self, repo: IIOSRepository):
        self.repo = repo

    async def audit_active_signals(self):
        """
        Scans all ACTIVE or WAITING live signals and updates their outcome based on price action.
        """
        active_signals = await self.repo.get_active_live_signals()

        # Also need to fetch WAITING_FOR_ENTRY signals
        # The existing get_active_live_signals only gets "ACTIVE" status
        # I should probably update the repo to get all "non-terminal" signals
        # For now, let's assume get_active_live_signals returns all non-terminal ones if we update it.
        # But wait, get_active_live_signals in hybrid_repository is:
        # pg.query(LiveSignalDB).filter(LiveSignalDB.status == "ACTIVE").all()

        # Let's update SignalAuditor to fetch all non-terminal signals manually if repo doesn't support it.
        # Or better, use get_all_live_signals if it exists or add a new method.
        # get_all_live_signals was added in previous tasks.

        all_signals = await self.repo.get_all_live_signals()
        non_terminal = [s for s in all_signals if s.status in ["WAITING_FOR_ENTRY", "ENTRY_TRIGGERED", "ACTIVE"]]

        for signal in non_terminal:
            await self._audit_single_signal(signal)

    async def _audit_single_signal(self, signal: LiveSignal):
        # 1. Fetch Price Action since signal timestamp
        ticker = yf.Ticker(f"{signal.symbol}.NS")
        df = ticker.history(start=signal.timestamp.date())

        if df.empty:
            return

        # 2. Setup Parameters
        entry = signal.entry_price
        target = signal.target_price
        stop = signal.stop_loss_price
        direction = getattr(signal, 'direction', 'LONG')

        # 3. Handle Timezones for comparison
        import pytz
        sig_ts = signal.timestamp
        if sig_ts.tzinfo is None:
            sig_ts = pytz.UTC.localize(sig_ts)

        # Filter for data after the signal timestamp
        # Ensure df index is comparable
        df.index = df.index.tz_convert(pytz.UTC)
        future_df = df[df.index >= sig_ts]
        if future_df.empty: return

        current_status = signal.status
        current_mfe = signal.mfe
        current_mae = signal.mae

        outcome_date = None
        profit_pct = None

        events = list(signal.events) if signal.events else []

        for date, row in future_df.iterrows():
            high = row["High"]
            low = row["Low"]
            close = row["Close"]

            # A. ENTRY MONITORING
            if current_status == "WAITING_FOR_ENTRY":
                triggered = False
                trigger_price = 0.0
                if direction == "LONG" and low <= entry:
                    triggered = True
                    trigger_price = min(entry, high) # Heuristic for trigger price
                elif direction == "SHORT" and high >= entry:
                    triggered = True
                    trigger_price = max(entry, low)

                if triggered:
                    current_status = "ENTRY_TRIGGERED"
                    signal.triggered_at = date.to_pydatetime()
                    signal.trigger_price = trigger_price
                    signal.trigger_condition = "Price Action Trigger"
                    events.append(SignalEvent(
                        type="ENTRY_TRIGGERED",
                        timestamp=date.to_pydatetime(),
                        price=trigger_price,
                        message=f"Price hit entry zone at ₹{trigger_price:,.2f}"
                    ))
                    # Continue loop to check for outcome in the same bar if necessary, or next bar
                    # For simplicity, move to ACTIVE state
                    current_status = "ACTIVE"
                    events.append(SignalEvent(
                        type="POSITION_ACTIVE",
                        timestamp=date.to_pydatetime(),
                        message="Position is now being monitored for target/stop."
                    ))

            # B. OUTCOME MONITORING (Only if ACTIVE)
            if current_status == "ACTIVE":
                # Directional Calculation
                if direction == "LONG":
                    mfe_val = ((high - entry) / entry) * 100
                    mae_val = ((low - entry) / entry) * 100

                    if target and high >= target:
                        current_status = "TARGET_HIT"
                        signal.outcome_date = date.to_pydatetime()
                        signal.profit_pct = ((target - entry) / entry) * 100
                        events.append(SignalEvent(type="TARGET_HIT", timestamp=date.to_pydatetime(), price=target, message="Profit target achieved."))
                        break
                    if stop and low <= stop:
                        current_status = "STOP_LOSS"
                        signal.outcome_date = date.to_pydatetime()
                        signal.profit_pct = ((stop - entry) / entry) * 100
                        events.append(SignalEvent(type="STOP_LOSS", timestamp=date.to_pydatetime(), price=stop, message="Stop loss triggered."))
                        break
                else: # SHORT
                    mfe_val = ((entry - low) / entry) * 100
                    mae_val = ((entry - high) / entry) * 100

                    if target and low <= target:
                        current_status = "TARGET_HIT"
                        signal.outcome_date = date.to_pydatetime()
                        signal.profit_pct = ((entry - target) / entry) * 100
                        events.append(SignalEvent(type="TARGET_HIT", timestamp=date.to_pydatetime(), price=target, message="Profit target achieved."))
                        break
                    if stop and high >= stop:
                        current_status = "STOP_LOSS"
                        signal.outcome_date = date.to_pydatetime()
                        signal.profit_pct = ((entry - stop) / entry) * 100
                        events.append(SignalEvent(type="STOP_LOSS", timestamp=date.to_pydatetime(), price=stop, message="Stop loss triggered."))
                        break

                # Update Running MFE/MAE
                if mfe_val > current_mfe: current_mfe = mfe_val
                if mae_val < current_mae: current_mae = mae_val

            # C. EXPIRY MONITORING
            age = (datetime.datetime.now(pytz.UTC) - sig_ts).days
            if current_status in ["WAITING_FOR_ENTRY", "ACTIVE"]:
                if (signal.timeframe == "INTRADAY" and date.date() > sig_ts.date()) or age > 30:
                    current_status = "EXPIRED"
                    signal.outcome_date = date.to_pydatetime()
                    if signal.trigger_price:
                         signal.profit_pct = ((close - entry) / entry) * 100 if direction == "LONG" else ((entry - close) / entry) * 100

                    events.append(SignalEvent(
                        type="EXPIRED",
                        timestamp=date.to_pydatetime(),
                        price=close,
                        message="Signal reached its time-to-live limit."
                    ))
                    break

        # 5. Finalize Snapshot
        signal.status = current_status
        signal.mfe = float(current_mfe)
        signal.mae = float(current_mae)
        signal.events = events

        if outcome_date:
            signal.outcome_date = outcome_date
            signal.profit_pct = float(profit_pct) if profit_pct is not None else None

        await self.repo.save_live_signal(signal)
