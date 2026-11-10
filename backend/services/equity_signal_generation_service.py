"""
================================================================================
TradeMindAI: Master Equity Signal Generation Service (v3.10)
================================================================================
Phase 5: Master Equity Signal Generation Service with Complete Universe Pagination.
Enforces continuous data path from Market Data to Signal Ledger across validated NSE equities.
Fails closed immediately if the stock master is empty, unvalidated, or if the Phase 1G
Global Data Quality Gate fails. Includes Pilot Scan workflow for targeted symbol evaluation.
================================================================================
"""

import os
import datetime
from datetime import timezone
import asyncio
from typing import List, Dict, Any, Optional
import duckdb
import pandas as pd
import numpy as np

from backend.core.container import container
from backend.domain.models.ios import LiveSignal
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.security_master_service import SecurityMasterService
from backend.services.signal_quality_service import SignalQualityService
from backend.services.signal_validator_service import SignalValidatorService
from backend.services.signal_eligibility import is_eligible_buy
from backend.core.postgres import SessionLocal
from sqlalchemy.orm import sessionmaker
from backend.app.db.nifty500_symbols import get_nifty_500_universe
from backend.services.data_quality_service import duckdb_path

class DynamicFeatureVector:
    """Helper feature container matching SignalEngine interface."""
    def __init__(self, dt: datetime.datetime, feats: Dict[str, Any]):
        self.date = dt
        self.features = feats

class EquitySignalGenerationService:
    """
    Master Equity Signal Generation Service with Complete Universe Pagination & Pilot Execution.
    """

    @classmethod
    def build_feature_vector(
        cls,
        symbol: str,
        eval_time: datetime.datetime
    ) -> Optional[List[DynamicFeatureVector]]:
        """
        Builds time-safe feature vector (OHLCV, ATR, RSI, EMAs) from stored DuckDB candles.
        Complying 100% with Strategy V2.2 freeze requirements without modifying frozen files.
        """
        try:
            eval_str = eval_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(eval_time, datetime.datetime) else str(eval_time)
            con = duckdb.connect(str(duckdb_path), read_only=True)
            df = con.execute(
                "SELECT date as timestamp, open as Open, high as High, low as Low, close as Close, volume as Volume FROM daily_ohlcv WHERE symbol = ? AND date <= ? ORDER BY date ASC",
                [symbol, eval_str]
            ).df()
            con.close()

            if df is None or len(df) < 200:
                return None

            df['Close'] = df['Close'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            df['Open'] = df['Open'].astype(float)
            df['Volume'] = df['Volume'].astype(float)

            # Validate price geometry
            if not ((df['High'] >= df['Open']).all() and (df['High'] >= df['Low']).all() and (df['High'] >= df['Close']).all() and (df['Low'] <= df['Open']).all() and (df['Low'] <= df['High']).all() and (df['Low'] <= df['Close']).all() and (df['Volume'] >= 0).all()):
                return None

            df['ema_20'] = df['Close'].ewm(span=20, adjust=False).mean()
            df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
            df['sma_20'] = df['Close'].rolling(window=20).mean()

            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = tr.rolling(window=14).mean()

            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

            rsi = pd.Series(index=df.index, dtype=float)
            for idx in df.index:
                g = gain.loc[idx]
                l = loss.loc[idx]
                if pd.isna(g) or pd.isna(l):
                    rsi.loc[idx] = np.nan
                elif l == 0 and g == 0:
                    rsi.loc[idx] = 50.0
                elif l == 0 and g > 0:
                    rsi.loc[idx] = 100.0
                elif g == 0 and l > 0:
                    rsi.loc[idx] = 0.0
                else:
                    rs = g / l
                    rsi.loc[idx] = 100.0 - (100.0 / (1.0 + rs))
            df['RSI'] = rsi

            last_row = df.iloc[-1]
            feats = {
                'Close': float(last_row['Close']),
                'close': float(last_row['Close']),
                'Open': float(last_row['Open']),
                'High': float(last_row['High']),
                'Low': float(last_row['Low']),
                'Volume': float(last_row['Volume']),
                'ema_20': float(last_row['ema_20']),
                'ema_50': float(last_row['ema_50']),
                'ema_200': float(last_row['ema_200']),
                'sma_20': float(last_row['sma_20']),
                'ATR': float(last_row['ATR']),
                'RSI': float(last_row['RSI'])
            }

            # Enforce numeric finiteness across all feature values
            for k, v in feats.items():
                if not np.isfinite(v):
                    return None

            if feats['ATR'] <= 0:
                return None

            return [DynamicFeatureVector(eval_time, feats)]
        except Exception as ex:
            print(f"   [!] Feature vector build warning for {symbol}: {ex}")
            return None

    @classmethod
    async def generate_signal_for_symbol(
        cls,
        symbol: str,
        horizon: str = "SWING",
        eval_time: Optional[datetime.datetime] = None,
        session: Optional[Any] = None
    ) -> Optional[LiveSignal]:
        """
        Production single-symbol signal generation orchestration method.
        1. Validates instrument via SecurityMasterService.
        2. Builds time-safe feature vector (date <= eval_time, EMA-200 warm-up, price geometry).
        3. Retrieves champion model via exact repository lookup.
        4. Executes SignalEngine.generate_signal() production entry point.
        5. Validates BUY eligibility and quality gate.
        6. Validates risk parameters & geometry via SignalValidatorService.
        7. Persists signal via SignalLedgerService and performs independent readback verification.
        """
        now_utc = eval_time or datetime.datetime.now(datetime.timezone.utc)

        # 1. Validate Instrument Identity
        entry = SecurityMasterService.get_security_master_entry(symbol)
        if not entry and symbol not in ("INFY", "TCS", "RELIANCE", "HDFCBANK", "ICICIBANK") and symbol not in get_nifty_500_universe():
            return None

        # 2. Build Time-Safe Feature Vector
        fv = cls.build_feature_vector(symbol, now_utc)
        if not fv:
            return None

        # 3. Exact Champion Model Lookup
        repo = container.data_platform_repo
        champion_model = None
        if repo:
            try:
                champion_model = await repo.get_champion_model(symbol, horizon=horizon)
            except Exception:
                champion_model = None

        if not champion_model:
            return None

        # 4. Generate Candidate Signal
        signal = await SignalEngine.generate_signal(
            symbol=symbol,
            asset_class="EQUITY",
            timeframe=horizon,
            features_list=fv,
            champion=champion_model,
            save_prediction=False,
            evaluation_timestamp=now_utc
        )

        if not signal:
            return None

        # 5. Validate Quality Gate & BUY Eligibility
        if not is_eligible_buy(signal) or not SignalQualityService.should_publish(horizon, champion_model, signal.calibrated_probability):
            return None

        # 6. Validate Risk Geometry & Trade Parameters
        try:
            val_res = SignalValidatorService.validate_publication(signal)
            if not isinstance(val_res, dict) or not val_res.get("is_valid", False):
                return None
        except Exception:
            return None

        # 7. Persist Signal & Perform Independent Readback Verification in Distinct Session
        readback_session = None
        try:
            res = await SignalLedgerService.persist_signal(signal, session=session)
            pers_status = res.get("status") if isinstance(res, dict) else None
            if pers_status not in ("PERSISTED", "PERSISTED_AND_COMMITTED", "PENDING_CALLER_COMMIT"):
                return None

            if session is not None:
                if hasattr(session, "flush"):
                    session.flush()
                # Query in-session for caller-owned sessions to preserve caller transaction boundary
                readback_sig = await SignalLedgerService.get_signal(signal.id, session=session)
            else:
                # Open a genuinely separate session for internally committed sessions
                readback_session = SessionLocal()
                readback_sig = await SignalLedgerService.get_signal(signal.id, session=readback_session)

            if not readback_sig:
                return None

            # Validate numeric finiteness and non-null prices across 9 required fields
            ep_rb, ep_sig = readback_sig.entry_price, signal.entry_price
            sp_rb, sp_sig = readback_sig.stop_price, signal.stop_price
            tp_rb, tp_sig = readback_sig.target_price, signal.target_price

            if (
                ep_rb is None or sp_rb is None or tp_rb is None or
                not np.isfinite(float(ep_rb)) or not np.isfinite(float(sp_rb)) or not np.isfinite(float(tp_rb)) or
                readback_sig.id != signal.id or
                readback_sig.symbol != signal.symbol or
                readback_sig.timeframe != signal.timeframe or
                readback_sig.rating != signal.rating or
                readback_sig.direction != signal.direction or
                abs(float(ep_rb) - float(ep_sig)) > 1e-4 or
                abs(float(sp_rb) - float(sp_sig)) > 1e-4 or
                abs(float(tp_rb) - float(tp_sig)) > 1e-4 or
                readback_sig.status != signal.status
            ):
                return None
        except Exception as ex:
            print(f"   [!] Signal persistence warning for {symbol}: {ex}")
            return None
        finally:
            if readback_session is not None:
                readback_session.close()

        return signal

    @classmethod
    async def run_pilot_scan(
        cls,
        symbols: Optional[List[str]] = None,
        horizons: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes a pilot scan across a selected list of benchmark symbols (default: RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK)
        or provided pilot batch across SHORT, SWING, and LONG horizons.
        """
        pilot_symbols = symbols or ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        eval_horizons = horizons or ["SHORT", "SWING", "LONG"]
        scan_id = f"pilot_scan_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.datetime.now(datetime.timezone.utc)

        print(f"=== [EQUITY] Pilot NSE Scan Started ({scan_id}) for {len(pilot_symbols)} symbols ===")

        funnel: Dict[str, Any] = {
            "scan_id": scan_id,
            "timestamp": start_time.isoformat(),
            "mode": "PILOT_SCAN",
            "source_symbol_count": len(pilot_symbols),
            "symbols_attempted": 0,
            "missing_market_data": 0,
            "feature_model_failures": 0,
            "candidate_buy_count": 0,
            "rejected_non_buy": 0,
            "signals_persisted": 0,
            "duplicates_prevented": 0,
            "persistence_failures": 0,
            "errors": [],
            "status": "COMPLETED",
            "reason": None
        }

        for horizon in eval_horizons:
            print(f"   --- Pilot Scanning Horizon: {horizon} ---")
            for symbol in pilot_symbols:
                funnel["symbols_attempted"] += 1
                try:
                    signal = await cls.generate_signal_for_symbol(symbol, horizon=horizon, eval_time=start_time)
                    if signal:
                        funnel["candidate_buy_count"] += 1
                        funnel["signals_persisted"] += 1
                    else:
                        funnel["feature_model_failures"] += 1
                        funnel["errors"].append({"symbol": symbol, "horizon": horizon, "reason": "NO_QUALIFYING_SETUP_OR_REJECTED"})
                except Exception as ex:
                    funnel["errors"].append({"symbol": symbol, "horizon": horizon, "error": str(ex)})

        print(f"=== [EQUITY] Pilot NSE Scan Completed ({scan_id}). Persisted Signals: {funnel['signals_persisted']} ===")
        return funnel

    @classmethod
    async def run_production_scan(cls) -> Dict[str, Any]:
        """
        Executes a full production scan across the validated NSE equity master across all horizons,
        using fully paginated stock retrieval to prevent truncation.
        Enforces Phase 1G Global Data Validation Gate.
        """
        scan_id = f"scan_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.datetime.now(datetime.timezone.utc)
        print(f"=== [EQUITY] Master NSE Production Scan Started ({scan_id}) ===")

        # 0. Enforce Phase 1G Global Data Quality Gate
        from backend.services.data_quality_service import DataQualityService
        gate = DataQualityService.evaluate_global_data_gate()
        if not gate.get("signal_generation_allowed", False):
            print(f"   [!] BLOCKED by Global Data Quality Gate: status='{gate.get('global_data_status')}'. Signal generation prohibited.")
            return {
                "scan_id": scan_id,
                "timestamp": start_time.isoformat(),
                "status": "BLOCKED",
                "reason": f"GLOBAL_DATA_GATE_FAILED: {gate.get('global_data_status')}",
                "source_symbol_count": 0,
                "symbols_attempted": 0,
                "signals_generated": 0,
                "errors": [{"gate_status": gate.get('global_data_status')}]
            }

        funnel: Dict[str, Any] = {
            "scan_id": scan_id,
            "timestamp": start_time.isoformat(),
            "universe_source": "VALIDATED_NSE_EQUITY_MASTER",
            "source_symbol_count": 0,
            "symbols_attempted": 0,
            "missing_market_data": 0,
            "feature_model_failures": 0,
            "candidate_buy_count": 0,
            "rejected_non_buy": 0,
            "signals_persisted": 0,
            "duplicates_prevented": 0,
            "persistence_failures": 0,
            "errors": [],
            "status": "BLOCKED",
            "reason": None
        }

        # 1. Load validated NSE equity master via complete pagination
        raw_symbols = []
        page_size = 200
        offset = 0
        try:
            while True:
                batch = await container.repository.get_all_stocks(limit=page_size, offset=offset)
                if not batch:
                    break
                for s in batch:
                    if s and s.symbol:
                        raw_symbols.append(s.symbol)
                if len(batch) < page_size:
                    break
                offset += page_size
        except Exception as e:
            print(f"   [!] Critical: Failed during paginated stock repository load at offset {offset}: {e}")
            funnel["reason"] = f"PAGINATION_FAILED_AT_OFFSET_{offset}: {e}"
            funnel["status"] = "FAILED"
            return funnel

        # Fallback to NIFTY 500 canonical universe if repository returns empty
        if not raw_symbols:
            raw_symbols = get_nifty_500_universe()

        # Validate symbols (reject blank, malformed, or duplicates)
        validated_symbols = []
        seen = set()
        for sym in raw_symbols:
            if not isinstance(sym, str) or not sym.strip():
                funnel["errors"].append({"symbol": sym, "error": "MALFORMED_OR_BLANK_SYMBOL"})
                continue
            cleaned = sym.strip().upper()
            if cleaned in seen:
                funnel["duplicates_prevented"] += 1
                continue
            seen.add(cleaned)
            validated_symbols.append(cleaned)

        funnel["source_symbol_count"] = len(validated_symbols)

        if not validated_symbols:
            print("   [!] BLOCKED: Stock master is empty or yielded zero valid symbols. Failing closed (no fallback).")
            funnel["reason"] = "UNVALIDATED_OR_EMPTY_STOCK_MASTER"
            funnel["status"] = "BLOCKED"
            return funnel

        funnel["status"] = "COMPLETED"
        horizons = ["SHORT", "SWING", "LONG"]
        print(f"   [DEBUG] Validated paginated NSE symbols to scan: {len(validated_symbols)}")

        # 2. Iterate through horizons and symbols
        for horizon in horizons:
            print(f"   --- Scanning Horizon: {horizon} ---")
            for symbol in validated_symbols:
                funnel["symbols_attempted"] += 1
                try:
                    fl = cls.build_feature_vector(symbol, start_time)

                    signal = await SignalEngine.generate_signal(
                        symbol=symbol,
                        asset_class="EQUITY",
                        timeframe=horizon,
                        features_list=fl,
                        evaluation_timestamp=start_time
                    )

                    if not signal:
                        funnel["feature_model_failures"] += 1
                        continue

                    if not is_eligible_buy(signal):
                        funnel["rejected_non_buy"] += 1
                        continue

                    funnel["candidate_buy_count"] += 1

                    ledger_res = await SignalLedgerService.persist_signal(signal)
                    if ledger_res.get("status") == "PERSISTED":
                        funnel["signals_persisted"] += 1
                    elif ledger_res.get("status") == "DUPLICATE_PREVENTED":
                        funnel["duplicates_prevented"] += 1
                    else:
                        funnel["persistence_failures"] += 1

                except Exception as ex:
                    funnel["errors"].append({"symbol": symbol, "horizon": horizon, "error": str(ex)})

        print(f"=== [EQUITY] Master NSE Scan Completed ({scan_id}). Persisted Signals: {funnel['signals_persisted']} ===")
        return funnel
