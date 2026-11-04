import datetime
import asyncio
from typing import List, Dict, Any, Optional
from backend.core.container import container
from backend.services.signal_engine import SignalEngine
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_eligibility import is_eligible_buy
from backend.app.db.nifty500_symbols import get_nifty_500_universe

class EquitySignalGenerationService:
    """
    Phase 5: Master Equity Signal Generation Service with Complete Universe Pagination.
    Enforces continuous data path from Market Data to Signal Ledger across validated NSE equities.
    Fails closed immediately if the stock master is empty, unvalidated, or if the Phase 1G
    Global Data Quality Gate fails.
    """

    @staticmethod
    async def run_production_scan() -> Dict[str, Any]:
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
                    # Data -> Features -> Model -> V2.2 -> Signal
                    signal = await SignalEngine.generate_signal(
                        symbol=symbol,
                        asset_class="EQUITY",
                        horizon=horizon,
                        as_of_timestamp=start_time
                    )

                    if not signal:
                        funnel["feature_model_failures"] += 1
                        continue

                    # Filter non-buy / non-eligible candidate signals
                    if not is_eligible_buy(signal):
                        funnel["rejected_non_buy"] += 1
                        continue

                    funnel["candidate_buy_count"] += 1

                    # Persist signal to ledger
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
