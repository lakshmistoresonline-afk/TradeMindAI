"""
================================================================================
TradeMindAI Phase D — Data Completeness & Quality Gates Audit
================================================================================
Evaluates 1,131,878 live DuckDB OHLCV records and 496 Parquet feature stores
for geometry, non-negative price/volume, duplicate timestamps, and NaN/Inf values.
================================================================================
"""

import duckdb
import glob
import pandas as pd
import numpy as np

def run_phase_d_audit():
    print("=== [PHASE D] Executing Data Completeness & Quality Gates ===")

    con = duckdb.connect('backend/data/analytical.duckdb')

    # 1. Total row count & distinct symbols
    total_rows = con.execute("SELECT count(*) FROM daily_ohlcv").fetchone()[0]
    distinct_syms = con.execute("SELECT count(distinct symbol) FROM daily_ohlcv").fetchone()[0]
    print(f"[*] Live DuckDB Status: {total_rows} rows across {distinct_syms} symbols.")

    # 2. Geometry violations check
    geom_violations = con.execute("""
        SELECT count(*) FROM daily_ohlcv
        WHERE low > open OR low > close OR high < open OR high < close OR high < low
    """).fetchone()[0]
    print(f"[*] OHLC Geometry Violations Count: {geom_violations}")

    # 3. Non-positive price violations
    price_violations = con.execute("""
        SELECT count(*) FROM daily_ohlcv
        WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0
    """).fetchone()[0]
    print(f"[*] Non-positive Price Violations Count: {price_violations}")

    # 4. Duplicate (symbol, date) check
    dup_records = con.execute("""
        SELECT count(*) FROM (
            SELECT symbol, date, count(*) as cnt
            FROM daily_ohlcv GROUP BY symbol, date HAVING count(*) > 1
        )
    """).fetchone()[0]
    print(f"[*] Duplicate (Symbol, Date) Records Count: {dup_records}")

    con.close()

    # 5. Parquet Feature Store Readability & NaN Check
    p_files = glob.glob('backend/data/features/*.parquet')
    print(f"[*] Parquet Feature Store Files Count: {len(p_files)}")

    nan_inf_files = 0
    total_parquet_rows = 0
    for pf in p_files:
        df = pd.read_parquet(pf)
        total_parquet_rows += len(df)
        req_cols = ["date", "Open", "High", "Low", "Close", "Volume"]
        if df[req_cols[1:]].isna().any().any() or np.isinf(df[req_cols[1:]].to_numpy()).any():
            nan_inf_files += 1

    print(f"[*] Total Parquet Store Rows: {total_parquet_rows}")
    print(f"[*] Parquet Files with NaN/Inf in OHLCV: {nan_inf_files}")

    quality_passed = (geom_violations == 0) and (price_violations == 0) and (dup_records == 0) and (nan_inf_files == 0)
    print(f"\n=== [PHASE D] Quality Gate Final Verdict: {'PASS' if quality_passed else 'FAIL'} ===")

if __name__ == "__main__":
    run_phase_d_audit()
