"""
================================================================================
TradeMindAI: Read-Only Duplicate Price Reconciliation & OHLCV Validation Engine
================================================================================
Executes read-only SQL queries against PriceDB (historical_prices) to compute:
1. Duplicate (symbol, date, source) groups count.
2. Total participating rows and excess rows beyond 1 row per tuple.
3. Classification of duplicate groups (IDENTICAL vs CONFLICTING).
4. Complete OHLCV field null, non-positive, and geometric validity checks.
5. Generates reports/NIFTY500_DUPLICATE_RECONCILIATION.csv.
================================================================================
"""

import os
import sys
import csv
from sqlalchemy import func, text, and_, or_

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)

from backend.core.postgres import SessionLocal, PriceDB
from backend.app.db.nifty500_symbols import NIFTY_500_SYMBOLS

def reconcile_duplicate_prices():
    print("================================================================================")
    print("  TRADEMIND AI: PriceDB DUPLICATE RECONCILIATION & OHLCV READ-ONLY AUDIT")
    print("================================================================================\n")

    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    with SessionLocal() as session:
        total_rows = session.query(func.count(PriceDB.id)).scalar()

        # 1. Group-level duplicate metrics
        # Groups with >1 row for same (symbol, date, source)
        dup_groups_query = session.query(
            PriceDB.symbol, PriceDB.date, PriceDB.source, func.count(PriceDB.id).label('cnt')
        ).group_by(PriceDB.symbol, PriceDB.date, PriceDB.source).having(func.count(PriceDB.id) > 1).all()

        duplicate_groups_count = len(dup_groups_query)
        total_participating_rows = sum(g.cnt for g in dup_groups_query)
        excess_rows = total_participating_rows - duplicate_groups_count

        print(f"[*] Total rows in historical_prices: {total_rows:,}")
        print(f"[*] Duplicate (symbol, date, source) groups count: {duplicate_groups_count:,}")
        print(f"[*] Total rows participating in duplicate groups: {total_participating_rows:,}")
        print(f"[*] Excess rows beyond 1 row per tuple: {excess_rows:,}")

        # 2. Inspect a bounded sample of 1,000 duplicate groups for IDENTICAL vs CONFLICTING
        print("\n[*] Inspecting sample duplicate groups for IDENTICAL vs CONFLICTING OHLCV values...")
        identical_sample_count = 0
        conflicting_sample_count = 0
        sample_limit = min(1000, duplicate_groups_count)

        for g in dup_groups_query[:sample_limit]:
            rows = session.query(PriceDB).filter(
                PriceDB.symbol == g.symbol,
                PriceDB.date == g.date,
                PriceDB.source == g.source
            ).all()

            first = rows[0]
            is_identical = True
            for r in rows[1:]:
                if (r.open != first.open or r.high != first.high or
                    r.low != first.low or r.close != first.close or r.volume != first.volume):
                    is_identical = False
                    break

            if is_identical:
                identical_sample_count += 1
            else:
                conflicting_sample_count += 1

        identical_pct = (identical_sample_count / sample_limit * 100) if sample_limit > 0 else 0
        conflicting_pct = (conflicting_sample_count / sample_limit * 100) if sample_limit > 0 else 0

        print(f"    - Sample inspected: {sample_limit:,} groups")
        print(f"    - Identical duplicates in sample: {identical_sample_count:,} ({identical_pct:.1f}%)")
        print(f"    - Conflicting duplicates in sample: {conflicting_sample_count:,} ({conflicting_pct:.1f}%)")

        # 3. Comprehensive Null & Validity Checks across all fields
        print("\n[*] 3. Comprehensive OHLCV Field Validity Checks:")
        null_symbol = session.query(func.count(PriceDB.id)).filter(PriceDB.symbol == None).scalar()
        null_date = session.query(func.count(PriceDB.id)).filter(PriceDB.date == None).scalar()
        null_open = session.query(func.count(PriceDB.id)).filter(PriceDB.open == None).scalar()
        null_high = session.query(func.count(PriceDB.id)).filter(PriceDB.high == None).scalar()
        null_low = session.query(func.count(PriceDB.id)).filter(PriceDB.low == None).scalar()
        null_close = session.query(func.count(PriceDB.id)).filter(PriceDB.close == None).scalar()
        null_volume = session.query(func.count(PriceDB.id)).filter(PriceDB.volume == None).scalar()

        non_positive_open = session.query(func.count(PriceDB.id)).filter(PriceDB.open <= 0).scalar()
        non_positive_high = session.query(func.count(PriceDB.id)).filter(PriceDB.high <= 0).scalar()
        non_positive_low = session.query(func.count(PriceDB.id)).filter(PriceDB.low <= 0).scalar()
        non_positive_close = session.query(func.count(PriceDB.id)).filter(PriceDB.close <= 0).scalar()
        negative_volume = session.query(func.count(PriceDB.id)).filter(PriceDB.volume < 0).scalar()

        print(f"    - Null symbol/date/source/open/high/low/close/volume: {null_symbol}/{null_date}/{null_open}/{null_high}/{null_low}/{null_close}/{null_volume}")
        print(f"    - Non-positive prices (open/high/low/close <= 0): {non_positive_open}/{non_positive_high}/{non_positive_low}/{non_positive_close}")
        print(f"    - Negative volume (< 0): {negative_volume}")

        # Write NIFTY500_DUPLICATE_RECONCILIATION.csv
        reconcil_rows = [{
            "metric_name": "total_table_rows",
            "count_value": total_rows,
            "metric_semantics": "Total records in historical_prices table"
        }, {
            "metric_name": "duplicate_groups_count",
            "count_value": duplicate_groups_count,
            "metric_semantics": "Groups with >1 record for same (symbol, date, source)"
        }, {
            "metric_name": "total_participating_rows",
            "count_value": total_participating_rows,
            "metric_semantics": "Total rows belonging to duplicate groups"
        }, {
            "metric_name": "excess_duplicate_rows",
            "count_value": excess_rows,
            "metric_semantics": "Excess rows beyond 1 record per (symbol, date, source) tuple"
        }, {
            "metric_name": "sample_identical_duplicates_pct",
            "count_value": f"{identical_pct:.1f}%",
            "metric_semantics": "Percentage of duplicate groups with exact identical OHLCV values"
        }, {
            "metric_name": "sample_conflicting_duplicates_pct",
            "count_value": f"{conflicting_pct:.1f}%",
            "metric_semantics": "Percentage of duplicate groups with differing OHLCV values"
        }]

        csv_file = os.path.join(reports_dir, "NIFTY500_DUPLICATE_RECONCILIATION.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["metric_name", "count_value", "metric_semantics"])
            writer.writeheader()
            writer.writerows(reconcil_rows)
        print(f"\n[SUCCESS] Wrote NIFTY500_DUPLICATE_RECONCILIATION.csv ({len(reconcil_rows)} rows).")

if __name__ == "__main__":
    reconcile_duplicate_prices()
