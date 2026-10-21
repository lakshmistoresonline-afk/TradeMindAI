"""
================================================================================
TradeMindAI: Phase 9.4.76 Evidence-Based Audit CSV Generator & Readiness Engine
================================================================================
Generates:
1. READINESS_AUDIT.csv (All 6 V2.2 indicators finite & verified per symbol)
2. DUPLICATE_RECONCILIATION.csv (Direct SQL distinct key count)
3. CROSS_SOURCE_RECONCILIATION.csv (Dynamic cross-source duplicate reconciliation)
4. OHLCV_QUALITY_AUDIT.csv (Dynamic PASSED/FAILED/UNVERIFIED)
5. SYMBOL_RESOLUTION_AUDIT.csv (Canonical symbol resolution)
6. NIFTY500_SCAN_ACCOUNTING_TEMPLATE.csv & NIFTY500_SCAN_ACCOUNTING.csv (NOT_RUN)
7. AUDIT_REPORT_MANIFEST.json & ACTIVE_REPORT_SET.json (Atomic report-set manifest)
================================================================================
"""

import os
import sys
import csv
import json
import math
import shutil
import tempfile
import hashlib
import datetime
import pandas as pd
from datetime import datetime, timezone
from sqlalchemy import func, text, or_

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS
from backend.app.services.indicator_service import LocalIndicatorService

CANONICAL_SYMBOL_ALIASES = {
    "AZAD": " Azad Engineering"
}

def resolve_stored_symbol_aliases(symbol: str) -> list:
    """Centralized symbol alias resolver for stored database variations."""
    aliases = [symbol]
    if symbol in CANONICAL_SYMBOL_ALIASES:
        aliases.append(CANONICAL_SYMBOL_ALIASES[symbol])
    return aliases

def is_finite_number(val) -> bool:
    """Robust finite number validator checking for non-null, finite float or int."""
    if val is None or pd.isna(val):
        return False
    try:
        f_val = float(val)
        return math.isfinite(f_val)
    except (ValueError, TypeError):
        return False

def prepare_reconciled_daily_bars(db_bars: list) -> tuple:
    """
    Production-path daily-bar reconciliation function preserving source identity.
    Groups raw price bars by trading date and provider source, identifies identical duplicates,
    detects cross-source agreement or conflicts, flags invalid OHLCV or missing provenance,
    and returns a chronologically sorted usable daily bar list and metric stats.
    """
    if not db_bars:
        return [], {
            "raw_records": 0,
            "distinct_dates": 0,
            "usable_bars": 0,
            "identical_duplicates_collapsed": 0,
            "conflicting_dates": 0,
            "unverified_provenance_dates": 0,
            "invalid_ohlcv_dates": 0,
            "single_source_dates": 0,
            "cross_source_agreements": 0
        }

    raw_records = len(db_bars)
    distinct_dates = len(set(b.date for b in db_bars))

    bars_by_date = {}
    for b in db_bars:
        dt = b.date
        if dt not in bars_by_date:
            bars_by_date[dt] = []
        bars_by_date[dt].append(b)

    reconciled_bars = []
    identical_collapsed = 0
    conflicting_dates = 0
    unverified_provenance_dates = 0
    invalid_ohlcv_dates = 0
    single_source_dates = 0
    cross_source_agreements = 0

    for dt in sorted(bars_by_date.keys()):
        group = bars_by_date[dt]

        # 1. Full OHLCV Geometry, Non-null, Finite, Positive Price, & Non-negative Volume Checks
        has_invalid_geometry = False
        has_unverified_provenance = False

        for b in group:
            if (b.open is None or b.high is None or b.low is None or b.close is None or
                not is_finite_number(b.open) or not is_finite_number(b.high) or
                not is_finite_number(b.low) or not is_finite_number(b.close) or
                b.open <= 0 or b.high <= 0 or b.low <= 0 or b.close <= 0 or
                b.high < b.low or
                (b.volume is not None and (not is_finite_number(b.volume) or b.volume < 0))):
                has_invalid_geometry = True

            if b.source is None or str(b.source).strip() == "":
                has_unverified_provenance = True

        if has_invalid_geometry:
            invalid_ohlcv_dates += 1
            continue

        if has_unverified_provenance:
            unverified_provenance_dates += 1
            continue

        # 2. Group by distinct source
        by_source = {}
        for b in group:
            src = str(b.source).strip()
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(b)

        # Handle same-source duplicates
        source_bars = []
        same_source_conflict = False
        for src, src_rows in by_source.items():
            if len(src_rows) == 1:
                source_bars.append(src_rows[0])
            else:
                first = src_rows[0]
                is_ident = all(
                    r.open == first.open and r.high == first.high and
                    r.low == first.low and r.close == first.close and
                    r.volume == first.volume
                    for r in src_rows[1:]
                )
                if is_ident:
                    identical_collapsed += (len(src_rows) - 1)
                    source_bars.append(first)
                else:
                    same_source_conflict = True

        if same_source_conflict:
            conflicting_dates += 1
            continue

        # 3. Cross-source evaluation
        if len(source_bars) == 1:
            single_source_dates += 1
            reconciled_bars.append(source_bars[0])
        else:
            first = source_bars[0]
            is_cross_agree = all(
                r.open == first.open and r.high == first.high and
                r.low == first.low and r.close == first.close and
                r.volume == first.volume
                for r in source_bars[1:]
            )
            if is_cross_agree:
                cross_source_agreements += 1
                identical_collapsed += (len(source_bars) - 1)
                reconciled_bars.append(first)
            else:
                conflicting_dates += 1

    metrics = {
        "raw_records": raw_records,
        "distinct_dates": distinct_dates,
        "usable_bars": len(reconciled_bars),
        "identical_duplicates_collapsed": identical_collapsed,
        "conflicting_dates": conflicting_dates,
        "unverified_provenance_dates": unverified_provenance_dates,
        "invalid_ohlcv_dates": invalid_ohlcv_dates,
        "single_source_dates": single_source_dates,
        "cross_source_agreements": cross_source_agreements
    }

    return reconciled_bars, metrics

def evaluate_symbol_v22_readiness(session, symbol: str) -> dict:
    """
    Reusable V2.2 readiness evaluator that prepares reconciled daily bars,
    invokes LocalIndicatorService.calculate_indicators, and validates finite indicator domain values.
    Assigns exactly ONE mutually exclusive primary disposition per symbol.
    """
    sym_aliases = resolve_stored_symbol_aliases(symbol)
    db_bars = session.query(PriceDB).filter(PriceDB.symbol.in_(sym_aliases)).order_by(PriceDB.date.asc()).all()

    reconciled_bars, recon_metrics = prepare_reconciled_daily_bars(db_bars)
    usable_bars_cnt = len(reconciled_bars)

    if recon_metrics["conflicting_dates"] > 0:
        return {
            "symbol": symbol,
            "resolved_aliases": sym_aliases,
            "raw_stored_records": recon_metrics["raw_records"],
            "distinct_observation_dates": recon_metrics["distinct_dates"],
            "usable_observation_records": usable_bars_cnt,
            "identical_duplicates_collapsed": recon_metrics["identical_duplicates_collapsed"],
            "conflicting_dates": recon_metrics["conflicting_dates"],
            "unverified_provenance_dates": recon_metrics["unverified_provenance_dates"],
            "invalid_ohlcv_dates": recon_metrics["invalid_ohlcv_dates"],
            "duplicate_quality_disposition": "CONFLICTING_DAILY_BARS_BLOCKED",
            "calc_status": "BLOCKED_DUPLICATE_CONFLICT",
            "ema200_valid": False, "ema50_valid": False, "ema20_valid": False,
            "sma20_valid": False, "atr14_valid": False, "rsi14_valid": False,
            "v22_readiness": "BLOCKED_DUPLICATE_CONFLICT",
            "reason": f"Conflicting duplicate bars detected on {recon_metrics['conflicting_dates']} dates"
        }

    if recon_metrics["unverified_provenance_dates"] > 0:
        return {
            "symbol": symbol,
            "resolved_aliases": sym_aliases,
            "raw_stored_records": recon_metrics["raw_records"],
            "distinct_observation_dates": recon_metrics["distinct_dates"],
            "usable_observation_records": usable_bars_cnt,
            "identical_duplicates_collapsed": recon_metrics["identical_duplicates_collapsed"],
            "conflicting_dates": 0,
            "unverified_provenance_dates": recon_metrics["unverified_provenance_dates"],
            "invalid_ohlcv_dates": recon_metrics["invalid_ohlcv_dates"],
            "duplicate_quality_disposition": "UNVERIFIED_PROVENANCE_BLOCKED",
            "calc_status": "BLOCKED_UNVERIFIED_PROVENANCE",
            "ema200_valid": False, "ema50_valid": False, "ema20_valid": False,
            "sma20_valid": False, "atr14_valid": False, "rsi14_valid": False,
            "v22_readiness": "BLOCKED_UNVERIFIED_PROVENANCE",
            "reason": f"Unverified or missing source provenance detected on {recon_metrics['unverified_provenance_dates']} dates"
        }

    if recon_metrics["invalid_ohlcv_dates"] > 0:
        return {
            "symbol": symbol,
            "resolved_aliases": sym_aliases,
            "raw_stored_records": recon_metrics["raw_records"],
            "distinct_observation_dates": recon_metrics["distinct_dates"],
            "usable_observation_records": usable_bars_cnt,
            "identical_duplicates_collapsed": recon_metrics["identical_duplicates_collapsed"],
            "conflicting_dates": 0,
            "unverified_provenance_dates": 0,
            "invalid_ohlcv_dates": recon_metrics["invalid_ohlcv_dates"],
            "duplicate_quality_disposition": "INVALID_OHLCV_GEOMETRY_BLOCKED",
            "calc_status": "BLOCKED_INVALID_OHLCV",
            "ema200_valid": False, "ema50_valid": False, "ema20_valid": False,
            "sma20_valid": False, "atr14_valid": False, "rsi14_valid": False,
            "v22_readiness": "BLOCKED_INVALID_OHLCV",
            "reason": f"Invalid OHLCV geometry detected on {recon_metrics['invalid_ohlcv_dates']} dates"
        }

    if usable_bars_cnt == 0:
        return {
            "symbol": symbol,
            "resolved_aliases": sym_aliases,
            "raw_stored_records": recon_metrics["raw_records"],
            "distinct_observation_dates": recon_metrics["distinct_dates"],
            "usable_observation_records": 0,
            "identical_duplicates_collapsed": 0,
            "conflicting_dates": 0,
            "unverified_provenance_dates": 0,
            "invalid_ohlcv_dates": 0,
            "duplicate_quality_disposition": "NO_DATA",
            "calc_status": "NO_DATA",
            "ema200_valid": False, "ema50_valid": False, "ema20_valid": False,
            "sma20_valid": False, "atr14_valid": False, "rsi14_valid": False,
            "v22_readiness": "BLOCKED_NO_DATA",
            "reason": "No price records found in PriceDB"
        }

    first_date_str = reconciled_bars[0].date.strftime("%Y-%m-%d") if hasattr(reconciled_bars[0].date, "strftime") else str(reconciled_bars[0].date)[:10]
    last_date_str = reconciled_bars[-1].date.strftime("%Y-%m-%d") if hasattr(reconciled_bars[-1].date, "strftime") else str(reconciled_bars[-1].date)[:10]

    df = pd.DataFrame([{
        "open": b.open, "high": b.high, "low": b.low, "close": b.close, "volume": b.volume
    } for b in reconciled_bars])

    try:
        df_ind = LocalIndicatorService.calculate_indicators(df)
        ema200_val = df_ind["ema_200"].iloc[-1] if "ema_200" in df_ind.columns else None
        ema50_val = df_ind["ema_50"].iloc[-1] if "ema_50" in df_ind.columns else None
        ema20_val = df_ind["ema_20"].iloc[-1] if "ema_20" in df_ind.columns else None
        sma20_val = df_ind["sma_20"].iloc[-1] if "sma_20" in df_ind.columns else None
        atr14_val = df_ind["atr_14"].iloc[-1] if "atr_14" in df_ind.columns else None
        rsi14_val = df_ind["rsi_14"].iloc[-1] if "rsi_14" in df_ind.columns else None

        ema200_valid = is_finite_number(ema200_val) and float(ema200_val) > 0
        ema50_valid = is_finite_number(ema50_val) and float(ema50_val) > 0
        ema20_valid = is_finite_number(ema20_val) and float(ema20_val) > 0
        sma20_valid = is_finite_number(sma20_val) and float(sma20_val) > 0
        atr14_valid = is_finite_number(atr14_val) and float(atr14_val) > 0
        rsi14_valid = is_finite_number(rsi14_val) and (0.0 <= float(rsi14_val) <= 100.0)

        all_indicators_valid = (ema200_valid and ema50_valid and ema20_valid and
                               sma20_valid and atr14_valid and rsi14_valid)
        calc_status = "INDICATOR_CALCULATION_PASSED" if all_indicators_valid else "BLOCKED_INDICATOR_OUTPUT"
    except Exception as e:
        ema200_valid = False; ema50_valid = False; ema20_valid = False
        sma20_valid = False; atr14_valid = False; rsi14_valid = False
        calc_status = f"CALCULATION_EXCEPTION: {str(e)}"

    is_ready = usable_bars_cnt >= 200 and calc_status == "INDICATOR_CALCULATION_PASSED"
    readiness = "V22_INPUT_REQUIREMENTS_PASSED" if is_ready else "BLOCKED_INSUFFICIENT_HISTORY"
    readiness_reason = "All 6 indicators (EMA200, EMA50, EMA20, SMA20, ATR14, RSI14) pass finite-value checks on 200+ usable bars" if is_ready else "Insufficient usable bars or calculation failure"

    dup_disposition = "EXHAUSTIVE_IDENTICAL_DUPLICATES_COLLAPSED" if recon_metrics["identical_duplicates_collapsed"] > 0 else "NO_DUPLICATES_FOUND"

    return {
        "symbol": symbol,
        "resolved_aliases": sym_aliases,
        "first_observation_date": first_date_str,
        "last_observation_date": last_date_str,
        "raw_stored_records": recon_metrics["raw_records"],
        "distinct_observation_dates": recon_metrics["distinct_dates"],
        "usable_observation_records": usable_bars_cnt,
        "identical_duplicates_collapsed": recon_metrics["identical_duplicates_collapsed"],
        "conflicting_dates": 0,
        "unverified_provenance_dates": 0,
        "invalid_ohlcv_dates": 0,
        "duplicate_quality_disposition": dup_disposition,
        "calc_status": calc_status,
        "ema200_valid": ema200_valid,
        "ema50_valid": ema50_valid,
        "ema20_valid": ema20_valid,
        "sma20_valid": sma20_valid,
        "atr14_valid": atr14_valid,
        "rsi14_valid": rsi14_valid,
        "v22_readiness": readiness,
        "reason": readiness_reason
    }

def classify_duplicate_groups(session):
    """
    Shared null-safe SQL aggregate classifier for duplicate (symbol, date, source) groups.
    Directly queries distinct composite keys and categorizes each duplicate group.
    """
    distinct_keys_sql = text("SELECT COUNT(*) FROM (SELECT DISTINCT symbol, date, source FROM historical_prices) t")
    direct_sql_distinct_keys = session.execute(distinct_keys_sql).scalar() or 0

    dup_stats_sql = text('''
        SELECT
            COUNT(*) as total_dup_groups,
            SUM(cnt) as total_participating_rows,
            SUM(cnt - 1) as excess_rows,
            SUM(CASE WHEN null_cnt = 0 AND max_open = min_open AND max_high = min_high AND max_low = min_low AND max_close = min_close AND max_vol = min_vol THEN 1 ELSE 0 END) as identical_groups,
            SUM(CASE WHEN null_cnt = 0 AND (max_open <> min_open OR max_high <> min_high OR max_low <> min_low OR max_close <> min_close OR max_vol <> min_vol) THEN 1 ELSE 0 END) as conflicting_groups,
            SUM(CASE WHEN null_cnt > 0 THEN 1 ELSE 0 END) as indeterminate_groups
        FROM (
            SELECT
                symbol, date, source,
                COUNT(*) as cnt,
                (COUNT(*) * 5) - (COUNT(open) + COUNT(high) + COUNT(low) + COUNT(close) + COUNT(volume)) as null_cnt,
                MAX(open) as max_open, MIN(open) as min_open,
                MAX(high) as max_high, MIN(high) as min_high,
                MAX(low) as max_low, MIN(low) as min_low,
                MAX(close) as max_close, MIN(close) as min_close,
                MAX(volume) as max_vol, MIN(volume) as min_vol
            FROM historical_prices
            GROUP BY symbol, date, source
            HAVING COUNT(*) > 1
        ) dup_summary
    ''')
    res_dup = session.execute(dup_stats_sql).fetchone()
    total_rows = session.query(func.count(PriceDB.id)).scalar() or 0

    dup_groups_count = (res_dup[0] if res_dup and res_dup[0] is not None else 0)
    total_participating = (res_dup[1] if res_dup and res_dup[1] is not None else 0)
    excess_rows = (res_dup[2] if res_dup and res_dup[2] is not None else 0)
    identical_groups = (res_dup[3] if res_dup and res_dup[3] is not None else 0)
    conflicting_groups = (res_dup[4] if res_dup and res_dup[4] is not None else 0)
    indeterminate_groups = (res_dup[5] if res_dup and res_dup[5] is not None else 0)
    math_unique_keys = total_rows - excess_rows

    return {
        "total_table_rows": total_rows,
        "direct_sql_distinct_keys": direct_sql_distinct_keys,
        "math_unique_keys": math_unique_keys,
        "duplicate_groups_count": dup_groups_count,
        "total_participating": total_participating,
        "excess_rows": excess_rows,
        "identical_groups": identical_groups,
        "conflicting_groups": conflicting_groups,
        "indeterminate_groups": indeterminate_groups
    }

def file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def generate_audit_csvs_isolated(session, symbols: list, output_dir: str):
    """
    Explicitly injected isolated audit generator entry point with atomic staging & publication.
    Requires explicit session, symbol universe, and output_dir dependencies.
    Raises ValueError immediately if dependencies are missing, preventing any production fallback.
    """
    if session is None or symbols is None or output_dir is None:
        raise ValueError(
            "CRITICAL ISOLATION GUARD: Isolated test execution requires explicitly injected "
            "session, symbols list, and output_dir parameters. Fallback to operational defaults is forbidden."
        )

    if not symbols:
        return False

    now_utc = datetime.now(timezone.utc)

    # Task 4: Generate into a unique temporary staging directory first
    staging_dir = tempfile.mkdtemp(prefix="trademind_audit_staging_")

    try:
        coverage_rows = []
        readiness_rows = []
        resolution_rows = []

        for idx, sym in enumerate(symbols, 1):
            eval_res = evaluate_symbol_v22_readiness(session, sym)
            sym_aliases = eval_res["resolved_aliases"]
            total_bars = eval_res["raw_stored_records"]
            distinct_dates = eval_res["distinct_observation_dates"]
            usable_bars = eval_res["usable_observation_records"]
            resolution_status = "RESOLVED_ALIAS" if len(sym_aliases) > 1 else "EXACT_MATCH"

            resolution_rows.append({
                "canonical_symbol": sym,
                "resolved_db_symbols": "|".join(sym_aliases),
                "resolution_status": resolution_status,
                "total_resolved_price_bars": total_bars,
                "distinct_observation_dates": distinct_dates
            })

            coverage_rows.append({
                "symbol": sym,
                "index_membership": "CANONICAL",
                "first_observation_date": eval_res.get("first_observation_date", "UNAVAILABLE"),
                "last_observation_date": eval_res.get("last_observation_date", "UNAVAILABLE"),
                "total_stored_records": total_bars,
                "distinct_observation_dates": distinct_dates,
                "data_granularity": "MULTI_SOURCE_HISTORICAL_BARS" if total_bars > 0 else "UNKNOWN",
                "data_freshness_status": "HISTORICAL_COVERAGE_PRESENT" if total_bars > 0 else "NO_DATA",
                "indicator_readiness": eval_res["v22_readiness"],
                "process_ingestion_label": "SOURCE_LABEL_IDENTIFIED",
                "data_source_provenance": "UNVERIFIED_PROVIDER_SIGNATURE",
                "ingestion_timestamp": "UNRECORDED_IN_SCHEMA",
                "verification_status": "EVIDENCE_UNVERIFIED_SOURCE_STRING_ONLY"
            })

            readiness_rows.append({
                "symbol": sym,
                "resolved_db_symbols": "|".join(sym_aliases),
                "first_observation_date": eval_res.get("first_observation_date", "UNAVAILABLE"),
                "last_observation_date": eval_res.get("last_observation_date", "UNAVAILABLE"),
                "raw_stored_records": total_bars,
                "distinct_observation_dates": distinct_dates,
                "usable_observation_records": usable_bars,
                "identical_duplicates_collapsed": eval_res.get("identical_duplicates_collapsed", 0),
                "conflicting_dates": eval_res.get("conflicting_dates", 0),
                "unverified_provenance_dates": eval_res.get("unverified_provenance_dates", 0),
                "invalid_ohlcv_dates": eval_res.get("invalid_ohlcv_dates", 0),
                "duplicate_quality_disposition": eval_res.get("duplicate_quality_disposition", "EXHAUSTIVE_IDENTICAL_DUPLICATES_COLLAPSED"),
                "indicator_calc_status": eval_res["calc_status"],
                "ema200_valid": eval_res["ema200_valid"],
                "ema50_valid": eval_res["ema50_valid"],
                "ema20_valid": eval_res["ema20_valid"],
                "sma20_valid": eval_res["sma20_valid"],
                "atr14_valid": eval_res["atr14_valid"],
                "rsi14_valid": eval_res["rsi14_valid"],
                "v22_input_readiness": eval_res["v22_readiness"],
                "readiness_reason": eval_res["reason"],
                "verification_method": "RECONCILED_PRODUCTION_PATH_VALIDATION"
            })

        dup_metrics = classify_duplicate_groups(session)

        dup_csv_rows = [
            {"metric_name": "total_table_rows", "count_value": dup_metrics["total_table_rows"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Total records in historical_prices table"},
            {"metric_name": "direct_sql_distinct_keys", "count_value": dup_metrics["direct_sql_distinct_keys"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Direct SELECT COUNT(*) FROM (SELECT DISTINCT) SQL query"},
            {"metric_name": "math_crosscheck_unique_keys", "count_value": dup_metrics["math_unique_keys"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Arithmetic cross-check: total_rows - excess_rows"},
            {"metric_name": "duplicate_key_groups_count", "count_value": dup_metrics["duplicate_groups_count"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Groups with >1 row for same key"},
            {"metric_name": "total_participating_rows", "count_value": dup_metrics["total_participating"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Total rows in duplicate groups"},
            {"metric_name": "excess_duplicate_rows", "count_value": dup_metrics["excess_rows"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Excess rows beyond 1 record per key"},
            {"metric_name": "exhaustive_identical_groups", "count_value": dup_metrics["identical_groups"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Duplicate groups with exact identical OHLCV values"},
            {"metric_name": "exhaustive_conflicting_groups", "count_value": dup_metrics["conflicting_groups"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Duplicate groups with differing OHLCV values"},
            {"metric_name": "exhaustive_indeterminate_groups", "count_value": dup_metrics["indeterminate_groups"], "audit_scope": "FULL_TABLE_100_PCT", "metric_semantics": "Duplicate groups containing nulls/precision errors"}
        ]

        # Task 1 & Task 3: Distinct, Independently Defined Statuses & Metrics
        total_eval_cnt = len(symbols)
        symbols_with_data_cnt = sum(1 for r in readiness_rows if int(r["raw_stored_records"]) > 0)
        symbols_no_data_cnt = sum(1 for r in readiness_rows if r["v22_input_readiness"] == "BLOCKED_NO_DATA")

        symbols_reconciled_clean_cnt = sum(1 for r in readiness_rows if int(r.get("conflicting_dates", 0)) == 0 and int(r.get("unverified_provenance_dates", 0)) == 0 and int(r.get("invalid_ohlcv_dates", 0)) == 0 and int(r["raw_stored_records"]) > 0)
        symbols_conflict_cnt = sum(1 for r in readiness_rows if r["v22_input_readiness"] == "BLOCKED_DUPLICATE_CONFLICT")
        symbols_unverified_cnt = sum(1 for r in readiness_rows if r["v22_input_readiness"] == "BLOCKED_UNVERIFIED_PROVENANCE")
        symbols_invalid_ohlcv_cnt = sum(1 for r in readiness_rows if r["v22_input_readiness"] == "BLOCKED_INVALID_OHLCV")
        symbols_insufficient_hist_cnt = sum(1 for r in readiness_rows if r["v22_input_readiness"] == "BLOCKED_INSUFFICIENT_HISTORY")
        symbols_v22_ready_cnt = sum(1 for r in readiness_rows if r["v22_input_readiness"] == "V22_INPUT_REQUIREMENTS_PASSED")

        overall_recon_status = "ALL_SYMBOLS_RECONCILED_CLEAN" if symbols_reconciled_clean_cnt == symbols_with_data_cnt and symbols_with_data_cnt > 0 else "RECONCILIATION_ISSUES_DETECTED"
        overall_ohlcv_status = "ALL_OHLCV_GEOMETRY_PASSED" if symbols_invalid_ohlcv_cnt == 0 else "OHLCV_GEOMETRY_ERRORS_DETECTED"
        overall_provenance_status = "ALL_PROVENANCE_IDENTIFIED" if symbols_unverified_cnt == 0 and symbols_with_data_cnt > 0 else "UNVERIFIED_PROVENANCE_DETECTED"
        overall_readiness_status = "ALL_SYMBOLS_V22_READY" if symbols_v22_ready_cnt == total_eval_cnt else "READINESS_ISSUES_DETECTED"

        cross_source_rows = [
            {"metric_key": "total_symbols_evaluated", "count_value": total_eval_cnt, "description": "Total canonical symbols evaluated in audit run"},
            {"metric_key": "symbols_with_data", "count_value": symbols_with_data_cnt, "description": "Symbols with >=1 price observation in database"},
            {"metric_key": "symbols_no_data", "count_value": symbols_no_data_cnt, "description": "Symbols with 0 price observations"},
            {"metric_key": "symbols_reconciled_clean", "count_value": symbols_reconciled_clean_cnt, "description": "Symbols with clean reconciled data (no conflicts, unverified provenance, or invalid OHLCV)"},
            {"metric_key": "symbols_with_duplicate_conflicts", "count_value": symbols_conflict_cnt, "description": "Symbols blocked due to conflicting duplicate price observations"},
            {"metric_key": "symbols_with_unverified_provenance", "count_value": symbols_unverified_cnt, "description": "Symbols blocked due to missing or null provider source identity"},
            {"metric_key": "symbols_with_invalid_ohlcv", "count_value": symbols_invalid_ohlcv_cnt, "description": "Symbols blocked due to invalid OHLCV geometry or non-finite values"},
            {"metric_key": "symbols_insufficient_history", "count_value": symbols_insufficient_hist_cnt, "description": "Symbols with clean data but <200 usable daily bars"},
            {"metric_key": "symbols_v22_ready", "count_value": symbols_v22_ready_cnt, "description": "Symbols passing all V2.2 input requirements (200+ usable bars & 6 valid indicators)"},
            {"metric_key": "overall_reconciliation_status", "count_value": overall_recon_status, "description": "Overall audit report set reconciliation status string"},
            {"metric_key": "overall_ohlcv_quality_status", "count_value": overall_ohlcv_status, "description": "Overall audit report set OHLCV quality status string"},
            {"metric_key": "overall_provenance_status", "count_value": overall_provenance_status, "description": "Overall audit report set provenance status string"},
            {"metric_key": "overall_v22_readiness_status", "count_value": overall_readiness_status, "description": "Overall audit report set V2.2 strategy readiness status string"}
        ]

        checks = [
            ("null_symbol_count", PriceDB.symbol == None),
            ("null_date_count", PriceDB.date == None),
            ("null_open_count", PriceDB.open == None),
            ("null_high_count", PriceDB.high == None),
            ("null_low_count", PriceDB.low == None),
            ("null_close_count", PriceDB.close == None),
            ("null_volume_count", PriceDB.volume == None),
            ("geometric_high_low_errors", PriceDB.high < PriceDB.low),
            ("geometric_high_open_errors", PriceDB.high < PriceDB.open),
            ("geometric_high_close_errors", PriceDB.high < PriceDB.close),
            ("geometric_low_open_errors", PriceDB.low > PriceDB.open),
            ("geometric_low_close_errors", PriceDB.low > PriceDB.close),
            ("non_positive_price_errors", or_(PriceDB.close <= 0, PriceDB.open <= 0, PriceDB.high <= 0, PriceDB.low <= 0)),
            ("negative_volume_errors", PriceDB.volume < 0)
        ]

        ohlcv_csv_rows = []
        for check_name, condition in checks:
            try:
                err_cnt = session.query(func.count(PriceDB.id)).filter(condition).scalar() or 0
                status_str = "PASSED" if err_cnt == 0 else "FAILED"
            except Exception:
                err_cnt = -1
                status_str = "UNVERIFIED"

            ohlcv_csv_rows.append({
                "validation_check": check_name,
                "error_count": err_cnt,
                "status": status_str
            })

        # Write files into staging_dir
        stg_cov_file = os.path.join(staging_dir, "READINESS_AUDIT.csv")
        with open(stg_cov_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(readiness_rows[0].keys()))
            writer.writeheader()
            writer.writerows(readiness_rows)

        stg_res_file = os.path.join(staging_dir, "SYMBOL_RESOLUTION_AUDIT.csv")
        with open(stg_res_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(resolution_rows[0].keys()))
            writer.writeheader()
            writer.writerows(resolution_rows)

        stg_dup_file = os.path.join(staging_dir, "DUPLICATE_RECONCILIATION.csv")
        with open(stg_dup_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["metric_name", "count_value", "audit_scope", "metric_semantics"])
            writer.writeheader()
            writer.writerows(dup_csv_rows)

        stg_cross_file = os.path.join(staging_dir, "CROSS_SOURCE_RECONCILIATION.csv")
        with open(stg_cross_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["metric_key", "count_value", "description"])
            writer.writeheader()
            writer.writerows(cross_source_rows)

        stg_ohlcv_file = os.path.join(staging_dir, "OHLCV_QUALITY_AUDIT.csv")
        with open(stg_ohlcv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["validation_check", "error_count", "status"])
            writer.writeheader()
            writer.writerows(ohlcv_csv_rows)

        # Atomic Manifest Creation in Staging
        report_set_id = f"SET_{int(now_utc.timestamp())}"
        manifest_data = {
            "report_set_id": report_set_id,
            "schema_version": "v2.2-ISO",
            "generated_at": now_utc.isoformat(),
            "total_symbols_evaluated": total_eval_cnt,
            "symbols_v22_ready": symbols_v22_ready_cnt,
            "symbols_reconciled_clean": symbols_reconciled_clean_cnt,
            "symbols_insufficient_history": symbols_insufficient_hist_cnt,
            "symbols_duplicate_conflicts": symbols_conflict_cnt,
            "symbols_unverified_provenance": symbols_unverified_cnt,
            "symbols_invalid_ohlcv": symbols_invalid_ohlcv_cnt,
            "symbols_no_data": symbols_no_data_cnt,
            "overall_reconciliation_status": overall_recon_status,
            "overall_ohlcv_quality_status": overall_ohlcv_status,
            "overall_provenance_status": overall_provenance_status,
            "overall_v22_readiness_status": overall_readiness_status,
            "files": {
                "READINESS_AUDIT.csv": file_sha256(stg_cov_file),
                "SYMBOL_RESOLUTION_AUDIT.csv": file_sha256(stg_res_file),
                "DUPLICATE_RECONCILIATION.csv": file_sha256(stg_dup_file),
                "CROSS_SOURCE_RECONCILIATION.csv": file_sha256(stg_cross_file),
                "OHLCV_QUALITY_AUDIT.csv": file_sha256(stg_ohlcv_file),
            }
        }
        stg_manifest_path = os.path.join(staging_dir, "AUDIT_REPORT_MANIFEST.json")
        with open(stg_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        # Phase 2: Atomic Report Set Publication Architecture
        # 1. Create an immutable versioned report set directory inside output_dir
        versioned_set_dir = os.path.join(output_dir, report_set_id)
        os.makedirs(versioned_set_dir, exist_ok=True)

        for fname in ["READINESS_AUDIT.csv", "SYMBOL_RESOLUTION_AUDIT.csv", "DUPLICATE_RECONCILIATION.csv", "CROSS_SOURCE_RECONCILIATION.csv", "OHLCV_QUALITY_AUDIT.csv", "AUDIT_REPORT_MANIFEST.json"]:
            s_path = os.path.join(staging_dir, fname)
            v_path = os.path.join(versioned_set_dir, fname)
            shutil.copy2(s_path, v_path)

        # 2. Write active report set pointer
        active_pointer_data = {
            "active_report_set_id": report_set_id,
            "schema_version": "v2.2-ISO",
            "published_at": now_utc.isoformat(),
            "manifest_file": os.path.join(report_set_id, "AUDIT_REPORT_MANIFEST.json")
        }
        ptr_tmp = os.path.join(output_dir, "ACTIVE_REPORT_SET.json.tmp")
        ptr_final = os.path.join(output_dir, "ACTIVE_REPORT_SET.json")
        with open(ptr_tmp, "w", encoding="utf-8") as f:
            json.dump(active_pointer_data, f, indent=2)
        os.replace(ptr_tmp, ptr_final)

        # 3. Update top-level CSV files atomically via temporary file replacement
        for fname in ["READINESS_AUDIT.csv", "SYMBOL_RESOLUTION_AUDIT.csv", "DUPLICATE_RECONCILIATION.csv", "CROSS_SOURCE_RECONCILIATION.csv", "OHLCV_QUALITY_AUDIT.csv", "AUDIT_REPORT_MANIFEST.json"]:
            s_path = os.path.join(staging_dir, fname)
            tmp_target = os.path.join(output_dir, f"{fname}.tmp")
            final_target = os.path.join(output_dir, fname)
            shutil.copy2(s_path, tmp_target)
            os.replace(tmp_target, final_target)

        return True
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)

def generate_phase_9_4_76_audit_csvs(scan_execution_log=None):
    """Default entry point for canonical production environment."""
    reports_dir = os.path.join(base_dir, "reports")
    with SessionLocal() as session:
        generate_audit_csvs_isolated(
            session=session,
            symbols=NIFTY_500_SYMBOLS,
            output_dir=reports_dir
        )

# Backward-compatible function alias exports
generate_phase_9_4_11_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_12_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_13_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_15_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_18_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_19_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_20_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_21_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_22_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_23_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_24_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_25_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_26_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_27_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_28_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_29_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_30_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_31_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_32_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_33_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_34_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_35_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_36_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_37_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_38_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_39_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_40_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_41_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_42_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_43_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_44_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_45_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_46_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_47_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_48_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_49_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_50_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_51_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_52_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_53_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_54_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_55_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_56_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_57_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_58_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_59_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_60_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_61_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_62_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_63_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_64_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_65_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_66_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_67_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_68_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_69_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_70_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_71_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_72_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_73_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_74_audit_csvs = generate_phase_9_4_76_audit_csvs
generate_phase_9_4_75_audit_csvs = generate_phase_9_4_76_audit_csvs

if __name__ == "__main__":
    generate_phase_9_4_76_audit_csvs()
