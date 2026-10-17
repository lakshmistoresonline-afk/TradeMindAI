"""
================================================================================
TradeMindAI: Centralized Signal BUY Eligibility Service (v2.3)
================================================================================
Defines the canonical BUY-only eligibility predicate.
Enforces that signals must be LONG and rated BUY or STRONG_BUY, rejecting SELL,
SHORT, missing, malformed, or conflicting directional attributes.
"""

from typing import Any

def is_eligible_buy(obj: Any) -> bool:
    """
    Canonical BUY eligibility predicate.
    Validates direction, rating, and signal_rating independently.
    Rejects missing, unknown, conflicting, SELL, or SHORT values.
    """
    if not obj:
        return False

    direction = getattr(obj, "direction", None) or (obj.get("direction") if isinstance(obj, dict) else None)
    rating = getattr(obj, "rating", None) or (obj.get("rating") if isinstance(obj, dict) else None)
    signal_rating = getattr(obj, "signal_rating", None) or (obj.get("signal_rating") if isinstance(obj, dict) else None)

    if not direction:
        return False

    dir_upper = str(direction).upper()
    if dir_upper != "LONG":
        return False

    ratings_to_check = []
    if rating is not None:
        ratings_to_check.append(str(rating).upper())
    if signal_rating is not None:
        ratings_to_check.append(str(signal_rating).upper())

    if not ratings_to_check:
        return False

    for r in ratings_to_check:
        if "SELL" in r or "SHORT" in r or r not in ("BUY", "STRONG_BUY"):
            return False

    return True
