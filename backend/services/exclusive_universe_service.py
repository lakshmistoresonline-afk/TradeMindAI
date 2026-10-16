"""
================================================================================
TradeMindAI: Four Exclusive NIFTY Stock Universes Service (v2.3)
================================================================================
Implements mutually exclusive stock partitions for:
1. NIFTY 50 (U50)
2. NIFTY 100 — Exclusive (U100 = N100 - U50)
3. NIFTY 200 — Exclusive (U200 = N200 - (U50 ∪ U100))
4. NIFTY 500 — Exclusive (U500 = N500 - (U50 ∪ U100 ∪ U200))
Enforces mandatory mathematical invariants (zero pairwise intersection) and
explicit source validation with UNVERIFIED provenance status for static snapshots.
Detects and rejects duplicate entries, blank symbols, and malformed types explicitly.
"""

from typing import List, Dict, Any, Set
from backend.app.db.nifty500_symbols import get_nifty_500_universe
from scripts.nifty100 import NIFTY_100_SYMBOLS
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

NIFTY_50_SYMBOLS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "HINDUNILVR",
    "LT", "AXISBANK", "ASIANPAINT", "HCLTECH", "MARUTI", "SUNPHARMA", "TITAN", "BAJFINANCE", "TATASTEEL", "NTPC",
    "POWERGRID", "M&M", "ADANIENT", "TATAMOTORS", "BAJAJFINSV", "WIPRO", "ULTRACEMCO", "GRASIM", "INDUSINDBK", "TECHM",
    "HDFCLIFE", "SBILIFE", "DIVISLAB", "BPCL", "ONGC", "COALINDIA", "CIPLA", "EICHERMOT", "HINDALCO", "TATACONSUM",
    "BRITANNIA", "DRREDDY", "APOLLOHOSP", "BAJAJ-AUTO", "TRENT", "BEL", "JIOFIN", "JSWSTEEL", "ADANIPORTS", "HINDZINC"
]

class ExclusiveUniverseService:
    @staticmethod
    def compute_partitions(n50: List[str], n100: List[str], n200: List[str], n500: List[str]) -> Dict[str, List[str]]:
        """
        Computes exclusive partitions from provided raw constituent lists with strict input validation.
        Explicitly rejects invalid types, blank symbols, and duplicate entries within lists.
        Invariants:
        - U50 = N50
        - U100 = N100 - U50
        - U200 = N200 - (U50 ∪ U100)
        - U500 = N500 - (U50 ∪ U100 ∪ U200)
        """
        for lst_name, lst in [("N50", n50), ("N100", n100), ("N200", n200), ("N500", n500)]:
            if not isinstance(lst, list):
                raise ValueError(f"Source list '{lst_name}' must be a list, got {type(lst)}")
            seen_in_list = set()
            for item in lst:
                if not isinstance(item, str):
                    raise ValueError(f"Source list '{lst_name}' contains non-string item: {item}")
                cleaned = item.strip().upper()
                if not cleaned:
                    raise ValueError(f"Source list '{lst_name}' contains blank symbol.")
                if cleaned in seen_in_list:
                    raise ValueError(f"Source list '{lst_name}' contains duplicate entry: {cleaned}")
                seen_in_list.add(cleaned)

        set_n50: Set[str] = set(s.strip().upper() for s in n50)
        set_n100: Set[str] = set(s.strip().upper() for s in n100)
        set_n200: Set[str] = set(s.strip().upper() for s in n200)
        set_n500: Set[str] = set(s.strip().upper() for s in n500)

        u50 = sorted(list(set_n50))
        u100 = sorted(list(set_n100 - set_n50))
        u200 = sorted(list(set_n200 - (set_n50 | set_n100)))
        u500 = sorted(list(set_n500 - (set_n50 | set_n100 | set_n200)))

        # Explicit validation raising ValueError on invariant violations
        s_u50, s_u100, s_u200, s_u500 = set(u50), set(u100), set(u200), set(u500)
        if len(s_u50 & s_u100) > 0:
            raise ValueError("Invariant violation: U50 and U100 intersect.")
        if len(s_u50 & s_u200) > 0:
            raise ValueError("Invariant violation: U50 and U200 intersect.")
        if len(s_u50 & s_u500) > 0:
            raise ValueError("Invariant violation: U50 and U500 intersect.")
        if len(s_u100 & s_u200) > 0:
            raise ValueError("Invariant violation: U100 and U200 intersect.")
        if len(s_u100 & s_u500) > 0:
            raise ValueError("Invariant violation: U100 and U500 intersect.")
        if len(s_u200 & s_u500) > 0:
            raise ValueError("Invariant violation: U200 and U500 intersect.")

        return {
            "NIFTY_50": u50,
            "NIFTY_100_EXCL": u100,
            "NIFTY_200_EXCL": u200,
            "NIFTY_500_EXCL": u500
        }

    @staticmethod
    def get_exclusive_partitions() -> Dict[str, List[str]]:
        return ExclusiveUniverseService.compute_partitions(
            NIFTY_50_SYMBOLS,
            NIFTY_100_SYMBOLS,
            NIFTY_200_CONSTITUENTS,
            list(get_nifty_500_universe().keys())
        )

    @classmethod
    def get_universe_metadata(cls) -> List[Dict[str, Any]]:
        parts = cls.get_exclusive_partitions()

        meta = [
            {
                "id": "NIFTY_50",
                "label": "NIFTY 50",
                "description": "The benchmark 50 stock index representing major economic sectors.",
                "count": len(parts["NIFTY_50"]),
                "source": "STATIC_SNAPSHOT_N50",
                "status": "UNVERIFIED"
            },
            {
                "id": "NIFTY_100_EXCL",
                "label": "NIFTY 100 — Exclusive",
                "description": "NIFTY 100 constituents excluding NIFTY 50.",
                "count": len(parts["NIFTY_100_EXCL"]),
                "source": "STATIC_SNAPSHOT_N100",
                "status": "UNVERIFIED"
            },
            {
                "id": "NIFTY_200_EXCL",
                "label": "NIFTY 200 — Exclusive",
                "description": "NIFTY 200 constituents excluding NIFTY 50 and NIFTY 100.",
                "count": len(parts["NIFTY_200_EXCL"]),
                "source": "STATIC_SNAPSHOT_N200",
                "status": "UNVERIFIED"
            },
            {
                "id": "NIFTY_500_EXCL",
                "label": "NIFTY 500 — Exclusive",
                "description": "Broad market NIFTY 500 constituents excluding all higher-priority index tiers.",
                "count": len(parts["NIFTY_500_EXCL"]),
                "source": "STATIC_SNAPSHOT_N500",
                "status": "UNVERIFIED"
            }
        ]
        return meta
