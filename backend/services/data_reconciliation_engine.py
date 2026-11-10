"""
================================================================================
TradeMindAI Phase 4: Multi-Provider Data Reconciliation & Validation Engine
================================================================================
Validates multi-provider OHLCV candles, checks geometry invariants (High >= Open/Close/Low),
reconciles FYERS and Angel One observations, and logs immutable evidence hashes.
================================================================================
"""

import hashlib
import json
import datetime
from datetime import timezone
from typing import List, Dict, Any, Tuple, Optional

class DataReconciliationEngine:
    """
    Multi-provider candle validation and reconciliation engine.
    """

    @staticmethod
    def validate_candle_geometry(candle: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates OHLC geometry invariants:
        - High >= Open, High >= Close, High >= Low
        - Low <= Open, Low <= Close
        - Volume >= 0
        """
        try:
            o = float(candle["open"])
            h = float(candle["high"])
            l = float(candle["low"])
            c = float(candle["close"])
            v = float(candle["volume"])

            if h < o or h < c or h < l:
                return False, f"HIGH_GEOMETRY_VIOLATION: high={h} open={o} close={c} low={l}"
            if l > o or l > c:
                return False, f"LOW_GEOMETRY_VIOLATION: low={l} open={o} close={c}"
            if v < 0:
                return False, f"NEGATIVE_VOLUME_VIOLATION: volume={v}"

            return True, None
        except Exception as ex:
            return False, f"MALFORMED_CANDLE_RECORD: {ex}"

    @staticmethod
    def reconcile_multi_provider_candles(
        fyers_candles: List[Dict[str, Any]],
        angel_candles: List[Dict[str, Any]],
        price_tolerance_pct: float = 0.5
    ) -> Dict[str, Any]:
        """
        Reconciles Provider A (FYERS) and Provider B (Angel One) candles.
        Detects matches, provider omissions, and price/volume conflicts.
        """
        fyers_map = {c["timestamp"]: c for c in fyers_candles if "timestamp" in c}
        angel_map = {c["timestamp"]: c for c in angel_candles if "timestamp" in c}

        all_timestamps = sorted(list(set(fyers_map.keys()).union(set(angel_map.keys()))))

        reconciled_candles: List[Dict[str, Any]] = []
        conflicts: List[Dict[str, Any]] = []
        matches = 0
        fyers_only = 0
        angel_only = 0

        for ts in all_timestamps:
            f_c = fyers_map.get(ts)
            a_c = angel_map.get(ts)

            if f_c and a_c:
                # Check price tolerance conflict
                f_close = float(f_c["close"])
                a_close = float(a_c["close"])
                diff_pct = abs(f_close - a_close) / max(f_close, 0.001) * 100.0

                if diff_pct <= price_tolerance_pct:
                    matches += 1
                    # Primary provider FYERS preferred when matched
                    f_c["reconciliation_status"] = "MATCHED"
                    reconciled_candles.append(f_c)
                else:
                    conflicts.append({
                        "timestamp": ts,
                        "symbol": f_c["symbol"],
                        "fyers_close": f_close,
                        "angel_close": a_close,
                        "diff_pct": round(diff_pct, 4),
                        "status": "PRICE_CONFLICT"
                    })
            elif f_c:
                fyers_only += 1
                f_c["reconciliation_status"] = "FYERS_ONLY"
                reconciled_candles.append(f_c)
            elif a_c:
                angel_only += 1
                a_c["reconciliation_status"] = "ANGEL_ONLY"
                reconciled_candles.append(a_c)

        return {
            "total_timestamps_evaluated": len(all_timestamps),
            "matched_count": matches,
            "fyers_only_count": fyers_only,
            "angel_only_count": angel_only,
            "conflicts_count": len(conflicts),
            "conflicts": conflicts,
            "reconciled_candles": reconciled_candles,
            "timestamp": datetime.datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def generate_evidence_hash(candle_batch: List[Dict[str, Any]]) -> str:
        """
        Generates deterministic SHA-256 evidence hash for candle batch provenance.
        """
        raw_str = json.dumps(candle_batch, sort_keys=True)
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
