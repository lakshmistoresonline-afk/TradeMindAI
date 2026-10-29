"""
================================================================================
TradeMindAI Gate B — Comprehensive Read-Only Persisted-Store Audit Script
================================================================================
Performs robust read-only validation across all 1,143,549 live DuckDB records and
499 Parquet feature store files:
- Cell-level Null, NaN, +Inf, -Inf detection
- Geometry and non-positive value checks
- Duplicate keys/dates
- Bidirectional symbol set equality
- DuckDB-to-Parquet element-wise equality (< 1e-4 numeric tolerance)
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

def run_comprehensive_store_audit():
    print("=== [GATE B] Comprehensive Read-Only Persisted-Store Audit ===")

    con = duckdb.connect(str(duckdb_path), read_only=True)

    # 1. Total DuckDB Row Count & Symbol List
    total_duck_rows = con.execute("SELECT count(*) FROM daily_ohlcv").fetchone()[0]
    duck_symbols = [r[0] for r in con.execute("SELECT DISTINCT symbol FROM daily_ohlcv ORDER BY symbol").fetchall()]
    print(f"[*] DuckDB Total Row Count: {total_duck_rows} rows across {len(duck_symbols)} symbols.")

    # 2. DuckDB Null, NaN, +Inf, -Inf Cell Count
    duck_invalid_cells = con.execute("""
        SELECT
            sum(CASE WHEN open IS NULL OR open != open OR open = 'Infinity' OR open = '-Infinity' THEN 1 ELSE 0 END) +
            sum(CASE WHEN high IS NULL OR high != high OR high = 'Infinity' OR high = '-Infinity' THEN 1 ELSE 0 END) +
            sum(CASE WHEN low IS NULL OR low != low OR low = 'Infinity' OR low = '-Infinity' THEN 1 ELSE 0 END) +
            sum(CASE WHEN close IS NULL OR close != close OR close = 'Infinity' OR close = '-Infinity' THEN 1 ELSE 0 END) +
            sum(CASE WHEN volume IS NULL OR volume != volume OR volume = 'Infinity' OR volume = '-Infinity' THEN 1 ELSE 0 END)
        FROM daily_ohlcv
    """).fetchone()[0] or 0
    print(f"[*] DuckDB Invalid (Null/NaN/Inf) Cell Count: {duck_invalid_cells}")

    # 3. DuckDB Geometry Violations (Row & Cell Count)
    duck_geom_rows = con.execute("""
        SELECT count(*) FROM daily_ohlcv
        WHERE low > open OR low > close OR high < open OR high < close OR high < low
    """).fetchone()[0]
    print(f"[*] DuckDB OHLC Geometry Violation Rows: {duck_geom_rows}")

    # 4. DuckDB Non-Positive Price & Negative Volume Rows
    duck_price_rows = con.execute("""
        SELECT count(*) FROM daily_ohlcv
        WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0 OR volume < 0
    """).fetchone()[0]
    print(f"[*] DuckDB Non-Positive Price / Negative Volume Rows: {duck_price_rows}")

    # 5. DuckDB Null/Invalid Symbol/Date Keys
    duck_key_nulls = con.execute("""
        SELECT count(*) FROM daily_ohlcv
        WHERE symbol IS NULL OR symbol = '' OR date IS NULL OR date = ''
    """).fetchone()[0]
    print(f"[*] DuckDB Null/Blank Primary Key Rows: {duck_key_nulls}")

    # 6. DuckDB Duplicate (Symbol, Date) Keys
    duck_dup_keys = con.execute("""
        SELECT count(*) FROM (
            SELECT symbol, date, count(*) as cnt
            FROM daily_ohlcv GROUP BY symbol, date HAVING count(*) > 1
        )
    """).fetchone()[0]
    print(f"[*] DuckDB Duplicate (Symbol, Date) PK Rows: {duck_dup_keys}")

    # 7. Bidirectional Symbol-Set Equality
    parquet_files = sorted(glob.glob(str(features_dir / "*.parquet")))
    parquet_symbols = set(Path(f).stem for f in parquet_files)
    duck_sym_set = set(duck_symbols)

    duck_not_parquet = duck_sym_set - parquet_symbols
    parquet_not_duck = parquet_symbols - duck_sym_set

    print(f"\n[*] Bidirectional Symbol-Set Audit:")
    print(f"    - DuckDB Symbols Count: {len(duck_sym_set)}")
    print(f"    - Parquet Files Count: {len(parquet_symbols)}")
    print(f"    - Symbols in DuckDB but missing in Parquet: {duck_not_parquet if duck_not_parquet else 'None (0)'}")
    print(f"    - Symbols in Parquet but missing in DuckDB: {parquet_not_duck if parquet_not_duck else 'None (0)'}")

    # 8. Parquet Store Robust Inspection & Numeric Tolerance Comparison (< 1e-4)
    p_total_rows = 0
    p_invalid_cells = 0
    p_geom_rows = 0
    p_price_rows = 0
    p_dup_date_files = 0
    value_mismatched_symbols = []

    req_cols = ["date", "Open", "High", "Low", "Close", "Volume"]

    for pf in parquet_files:
        sym = Path(pf).stem
        df_p = pd.read_parquet(pf)
        p_total_rows += len(df_p)

        # Robust cell-level NaN/Inf check
        p_vals = df_p[req_cols[1:]].to_numpy()
        invalid_mask = np.isnan(p_vals) | np.isinf(p_vals)
        p_invalid_cells += int(invalid_mask.sum())

        # Geometry check
        p_geom = (
            (df_p["Low"] > df_p["Open"]) | (df_p["Low"] > df_p["Close"]) |
            (df_p["High"] < df_p["Open"]) | (df_p["High"] < df_p["Close"]) |
            (df_p["High"] < df_p["Low"])
        )
        p_geom_rows += int(p_geom.sum())

        # Price/volume bounds check
        p_price = (
            (df_p["Open"] <= 0) | (df_p["High"] <= 0) |
            (df_p["Low"] <= 0) | (df_p["Close"] <= 0) |
            (df_p["Volume"] < 0)
        )
        p_price_rows += int(p_price.sum())

        # Duplicate dates check
        if df_p["date"].duplicated().any():
            p_dup_date_files += 1

        # Element-wise comparison with DuckDB (< 1e-4 tolerance)
        df_d = con.execute("""
            SELECT date, open as Open, high as High, low as Low, close as Close, volume as Volume
            FROM daily_ohlcv WHERE symbol = ? ORDER BY date
        """, [sym]).df()

        if len(df_p) != len(df_d) or set(df_p["date"]) != set(df_d["date"]):
            value_mismatched_symbols.append((sym, "ROW_COUNT_OR_DATE_SET_MISMATCH"))
        else:
            df_p_sub = df_p.set_index("date")[["Open", "High", "Low", "Close", "Volume"]]
            df_d_sub = df_d.set_index("date")[["Open", "High", "Low", "Close", "Volume"]]
            common_dates = sorted(list(set(df_p["date"])))

            p_sub = df_p_sub.loc[common_dates]
            d_sub = df_d_sub.loc[common_dates]

            diff_mask = (
                ((p_sub["Open"] - d_sub["Open"]).abs() > 1e-4) |
                ((p_sub["High"] - d_sub["High"]).abs() > 1e-4) |
                ((p_sub["Low"] - d_sub["Low"]).abs() > 1e-4) |
                ((p_sub["Close"] - d_sub["Close"]).abs() > 1e-4) |
                ((p_sub["Volume"] - d_sub["Volume"]).abs() > 1e-4)
            )
            diff_count = int(diff_mask.sum().sum())
            if diff_count > 0:
                value_mismatched_symbols.append((sym, f"VALUE_MISMATCH_{diff_count}_CELLS"))

    con.close()

    print(f"\n[*] Parquet Store Inspection Output:")
    print(f"    - Total Parquet Rows: {p_total_rows}")
    print(f"    - Invalid (Null/NaN/Inf) Cells: {p_invalid_cells}")
    print(f"    - OHLC Geometry Violation Rows: {p_geom_rows}")
    print(f"    - Non-Positive Price / Negative Volume Rows: {p_price_rows}")
    print(f"    - Files with Duplicate Dates: {p_dup_date_files}")
    print(f"    - DuckDB-to-Parquet Value Mismatched Symbols (<1e-4 tol): {len(value_mismatched_symbols)}")

    gate_b_pass = (
        duck_invalid_cells == 0 and duck_geom_rows == 0 and duck_price_rows == 0 and
        duck_key_nulls == 0 and duck_dup_keys == 0 and len(duck_not_parquet) == 0 and
        len(parquet_not_duck) == 0 and p_invalid_cells == 0 and p_geom_rows == 0 and
        p_price_rows == 0 and p_dup_date_files == 0 and len(value_mismatched_symbols) == 0
    )

    print(f"\n=== [GATE B] Final Verdict: {'PASS' if gate_b_pass else 'FAIL'} ===")

if __name__ == "__main__":
    run_comprehensive_store_audit()
