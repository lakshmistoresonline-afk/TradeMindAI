"""
================================================================================
TradeMindAI: Date-Set Session Coverage Engine (v2.7-STRICT-PROVENANCE)
================================================================================
Evaluates historical session coverage by set comparison between verified expected
trading dates and observed persisted dates.
Zero tolerance for row-count approximations, missing dates, unverified provenance,
or hardcoded verification defaults.
================================================================================
"""

from typing import Set, Dict, Any, List, Optional
import pandas as pd

MUTUALLY_EXCLUSIVE_STATUSES = [
    "COMPLETE_HISTORICAL_COVERAGE",
    "COMPLETE_POST_LISTING_COVERAGE",
    "PARTIAL_HISTORY_MISSING_EARLY_WINDOW",
    "PARTIAL_HISTORY",
    "MISSING_NO_PARQUET_FILE",
    "EMPTY_PARQUET_FILE",
    "CORRUPT_PARQUET_FILE",
    "INVALID_OHLCV_GEOMETRY",
    "DUPLICATE_TIMESTAMPS_DETECTED",
    "INVALID_DATES_DETECTED",
    "SESSION_CALENDAR_UNVERIFIED",
    "LISTING_DATE_UNVERIFIED"
]

def evaluate_symbol_date_set_coverage(
    canonical_symbol: str,
    company_name: str,
    observed_dates_list: List[str],
    expected_dates_set: Set[str],
    calendar_verified: bool,
    listing_verified: bool,
    verified_listing_date: str,
    is_parquet_present: bool = True,
    is_parquet_corrupt: bool = False,
    geometry_error_count: int = 0,
    provenance_source: str = "YFINANCE_PARQUET_STORE"
) -> Dict[str, Any]:
    """
    Evaluates date-set coverage semantics for a canonical equity symbol.
    Requires explicit, evidence-backed verification flags (no defaults).
    """
    if not is_parquet_present:
        return {
            "canonical_symbol": canonical_symbol,
            "company_name": company_name,
            "verified_listing_date": verified_listing_date,
            "listing_verified": listing_verified,
            "calendar_verified": calendar_verified,
            "expected_session_count": len(expected_dates_set),
            "observed_session_count": 0,
            "missing_session_count": len(expected_dates_set),
            "unexpected_session_count": 0,
            "duplicate_timestamp_count": 0,
            "invalid_date_count": 0,
            "session_coverage_pct": 0.0,
            "persisted_row_count": 0,
            "earliest_persisted_date": "N/A",
            "latest_persisted_date": "N/A",
            "coverage_status": "MISSING_NO_PARQUET_FILE",
            "provenance_source": "UNINGESTED",
            "requires_backfill": True
        }

    if is_parquet_corrupt:
        return {
            "canonical_symbol": canonical_symbol,
            "company_name": company_name,
            "verified_listing_date": verified_listing_date,
            "listing_verified": listing_verified,
            "calendar_verified": calendar_verified,
            "expected_session_count": len(expected_dates_set),
            "observed_session_count": 0,
            "missing_session_count": len(expected_dates_set),
            "unexpected_session_count": 0,
            "duplicate_timestamp_count": 0,
            "invalid_date_count": 0,
            "session_coverage_pct": 0.0,
            "persisted_row_count": 0,
            "earliest_persisted_date": "N/A",
            "latest_persisted_date": "N/A",
            "coverage_status": "CORRUPT_PARQUET_FILE",
            "provenance_source": provenance_source,
            "requires_backfill": True
        }

    if not observed_dates_list:
        return {
            "canonical_symbol": canonical_symbol,
            "company_name": company_name,
            "verified_listing_date": verified_listing_date,
            "listing_verified": listing_verified,
            "calendar_verified": calendar_verified,
            "expected_session_count": len(expected_dates_set),
            "observed_session_count": 0,
            "missing_session_count": len(expected_dates_set),
            "unexpected_session_count": 0,
            "duplicate_timestamp_count": 0,
            "invalid_date_count": 0,
            "session_coverage_pct": 0.0,
            "persisted_row_count": 0,
            "earliest_persisted_date": "N/A",
            "latest_persisted_date": "N/A",
            "coverage_status": "EMPTY_PARQUET_FILE",
            "provenance_source": provenance_source,
            "requires_backfill": True
        }

    # Explicit Date Normalization & Parse Failure Audit
    parsed_s = pd.to_datetime(pd.Series(observed_dates_list), errors="coerce")
    invalid_date_count = int(parsed_s.isna().sum())
    valid_dates_s = parsed_s.dropna().dt.strftime("%Y-%m-%d")

    normalized_observed = list(valid_dates_s)
    duplicate_count = len(normalized_observed) - len(set(normalized_observed))
    observed_set = set(normalized_observed)

    missing_dates = expected_dates_set - observed_set
    unexpected_dates = observed_set - expected_dates_set

    earliest_observed = min(normalized_observed) if normalized_observed else "N/A"
    latest_observed = max(normalized_observed) if normalized_observed else "N/A"

    expected_count = len(expected_dates_set)
    observed_count = len(observed_set)
    missing_count = len(missing_dates)
    unexpected_count = len(unexpected_dates)

    coverage_pct = round((len(observed_set & expected_dates_set) / expected_count) * 100.0, 1) if expected_count > 0 else 0.0

    # Strict Fail-Closed Status Classification
    if not calendar_verified:
        status = "SESSION_CALENDAR_UNVERIFIED"
    elif not listing_verified:
        status = "LISTING_DATE_UNVERIFIED"
    elif invalid_date_count > 0:
        status = "INVALID_DATES_DETECTED"
    elif geometry_error_count > 0:
        status = "INVALID_OHLCV_GEOMETRY"
    elif duplicate_count > 0:
        status = "DUPLICATE_TIMESTAMPS_DETECTED"
    elif missing_count == 0 and unexpected_count == 0:
        if verified_listing_date > "2015-01-01":
            status = "COMPLETE_POST_LISTING_COVERAGE"
        else:
            status = "COMPLETE_HISTORICAL_COVERAGE"
    elif earliest_observed > verified_listing_date and earliest_observed > "2015-01-05":
        status = "PARTIAL_HISTORY_MISSING_EARLY_WINDOW"
    else:
        status = "PARTIAL_HISTORY"

    return {
        "canonical_symbol": canonical_symbol,
        "company_name": company_name,
        "verified_listing_date": verified_listing_date,
        "listing_verified": listing_verified,
        "calendar_verified": calendar_verified,
        "expected_session_count": expected_count,
        "observed_session_count": observed_count,
        "missing_session_count": missing_count,
        "unexpected_session_count": unexpected_count,
        "duplicate_timestamp_count": duplicate_count,
        "invalid_date_count": invalid_date_count,
        "session_coverage_pct": coverage_pct,
        "persisted_row_count": len(normalized_observed),
        "earliest_persisted_date": earliest_observed,
        "latest_persisted_date": latest_observed,
        "coverage_status": status,
        "provenance_source": provenance_source,
        "requires_backfill": True if status not in ["COMPLETE_HISTORICAL_COVERAGE", "COMPLETE_POST_LISTING_COVERAGE"] else False
    }
