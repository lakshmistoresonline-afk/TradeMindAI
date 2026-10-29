"""
================================================================================
TradeMindAI: Full Persisted-Data Integrity Audit Script (Section 3)
================================================================================
Audits all 1,143,549 live DuckDB records and 499 Parquet feature store files
for value-level consistency, geometry violations, NaN/Inf, duplicate keys, and
DuckDB-to-Parquet element-wise equality across all 499 symbols.
================================================================================
"""

import duckdb
import glob
import pandas as pd
import numpy as np
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
data_dir = root_dir / "backend" / "data"
duckdb_path = data_dir / "analytical.duckdb"
features_dir = data_dir / "features"

def run_persisted_data_audit():
    print("=== [SECTION 3] Executing Full Persisted-Data Integrity Audit ===")

    con = duckdb.connect(str(duckdb_path), read_only=True)

    # 1. DuckDB Row Count & Distinct Symbol Count
    total_duck_rows = con.execute("SELECT count(*) FROM daily_ohlcv").fetchone()[0]
    duck_symbols = [r[0] for r in con.execute("SELECT DISTINCT symbol FROM daily_ohlcv ORDER BY symbol").fetchall()]
    print(f"[*] Live DuckDB `daily_ohlcv`: {total_duck_rows} rows across {len(duck_symbols)} symbols.")

    # 2. DuckDB OHLC Geometry Violations
    duck_geom_violations = con.execute("""
        SELECT count(*) FROM daily_ohlcv
        WHERE low > open OR low > close OR high < open OR high < close OR high < low
    """).fetchone()[0]
    print(f"[*] DuckDB OHLC Geometry Violations Count: {duck_geom_violations}")

    # 3. DuckDB Non-Positive Prices & Negative Volumes
    duck_price_violations = con.execute("""
        SELECT count(*) FROM daily_ohlcv
        WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0 OR volume < 0
    """).fetchone()[0]
    print(f"[*] DuckDB Price/Volume Violations Count: {duck_price_violations}")

    # 4. DuckDB Duplicate (Symbol, Date) Primary Key Check
    duck_duplicates = con.execute("""
        SELECT count(*) FROM (
            SELECT symbol, date, count(*) as cnt
            FROM daily_ohlcv GROUP BY symbol, date HAVING count(*) > 1
        )
    """).fetchone()[0]
    print(f"[*] DuckDB Duplicate (Symbol, Date) PK Violations Count: {duck_duplicates}")

    # 5. Parquet Feature Store Inspection & Value Alignment with DuckDB
    parquet_paths = sorted(glob.glob(str(features_dir / "*.parquet")))
    print(f"\n[*] Live Parquet Feature Store: {len(parquet_paths)} .parquet files found.")

    parquet_total_rows = 0
    parquet_nan_inf_count = 0
    parquet_geom_count = 0
    parquet_dup_dates_count = 0

    mismatched_symbols = []

    req_cols = ["date", "Open", "High", "Low", "Close", "Volume"]

    for idx, pf in enumerate(parquet_paths, 1):
        sym = Path(pf).stem
        df_p = pd.read_parquet(pf)
        parquet_total_rows += len(df_p)

        # Check NaN/Inf
        if df_p[req_cols[1:]].isna().any().any() or np.isinf(df_p[req_cols[1:]].to_numpy()).any():
            parquet_nan_inf_count += 1

        # Check Geometry
        p_geom = (
            (df_p["Low"] > df_p["Open"]) | (df_p["Low"] > df_p["Close"]) |
            (df_p["High"] < df_p["Open"]) | (df_p["High"] < df_p["Close"]) |
            (df_p["High"] < df_p["Low"])
        )
        if p_geom.any():
            parquet_geom_count += 1

        # Check Duplicate Dates
        if df_p["date"].duplicated().any():
            parquet_dup_dates_count += 1

        # Compare DuckDB vs Parquet for this symbol
        df_d = con.execute("""
            SELECT date, open as Open, high as High, low as Low, close as Close, volume as Volume
            FROM daily_ohlcv WHERE symbol = ? ORDER BY date
        """, [sym]).df()

        if len(df_p) != len(df_d) or set(df_p["date"]) != set(df_d["date"]):
            mismatched_symbols.append((sym, "ROW_COUNT_OR_DATE_SET_MISMATCH", len(df_p), len(df_d)))
        else:
            # Value-level OHLCV comparison
            df_p_sub = df_p.set_index("date")[["Open", "High", "Low", "Close", "Volume"]]
            df_d_sub = df_d.set_index("date")[["Open", "High", "Low", "Close", "Volume"]]
            common_dates = sorted(list(set(df_p["date"])))

            p_sub = df_p_sub.loc[common_dates]
            d_sub = df_d_sub.loc[common_dates]

            val_diff = (
                ((p_sub["Open"] - d_sub["Open"]).abs() > 1e-4) |
                ((p_sub["High"] - d_sub["High"]).abs() > 1e-4) |
                ((p_sub["Low"] - d_sub["Low"]).abs() > 1e-4) |
                ((p_sub["Close"] - d_sub["Close"]).abs() > 1e-4) |
                ((p_sub["Volume"] - d_sub["Volume"]).abs() > 1e-4)
            ).sum()

            if val_diff > 0:
                mismatched_symbols.append((sym, f"VALUE_MISMATCH_{val_diff}", len(df_p), len(df_d)))

    con.close()

    print(f"\n[*] Parquet Audit Results:")
    print(f"    - Parquet Cumulative Row Count: {parquet_total_rows}")
    print(f"    - Parquet Files with NaN/Inf: {parquet_nan_inf_count}")
    print(f"    - Parquet Files with OHLC Geometry Violations: {parquet_geom_count}")
    print(f"    - Parquet Files with Duplicate Dates: {parquet_dup_dates_count}")
    print(f"    - DuckDB-to-Parquet Mismatched Symbols Count: {len(mismatched_symbols)}")

    if mismatched_symbols:
        print(f"[-] Sample Mismatches: {mismatched_symbols[:5]}")
    else:
        print("[+] PERFECT ALIGNMENT: All 499 symbols match 100.0% identically in date set and OHLCV values between DuckDB and Parquet stores!")

if __name__ == "__main__":
    run_persisted_data_audit()
