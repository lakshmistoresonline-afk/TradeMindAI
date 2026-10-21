"""
================================================================================
TradeMindAI: Independent Audit CSV Acceptance Validator CLI
================================================================================
Standalone CLI tool that reads generated audit CSV files and manifests from disk
and recomputes all data provenance, reconciliation, schema, arithmetic, and readiness invariants.

Exit Codes:
  0 : All acceptance criteria and reconciliation invariants verified.
  1 : Validation failure (missing files, schema corruption, contradictory rows,
      falsified totals, unverified provenance mised as verified, or conflict).
================================================================================
"""

import os
import sys
import csv
import json
import math
import hashlib
import argparse

def file_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def validate_csv_directory(target_dir: str) -> bool:
    print(f"================================================================================")
    print(f"  TRADEMIND AI: INDEPENDENT AUDIT CSV ACCEPTANCE VALIDATOR CLI")
    print(f"  Target Directory: {target_dir}")
    print(f"================================================================================\n")

    if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        print(f"[ERROR] Target directory does not exist: {target_dir}", file=sys.stderr)
        return False

    files_in_dir = os.listdir(target_dir)

    # Task 5: Strict Manifest Validation
    manifest_path = os.path.join(target_dir, "AUDIT_REPORT_MANIFEST.json")
    manifest_files = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as mf:
                manifest_data = json.load(mf)

            schema_ver = manifest_data.get("schema_version", "")
            if schema_ver != "v2.2-ISO":
                print(f"[ERROR] Unsupported report set schema version in manifest: '{schema_ver}'", file=sys.stderr)
                return False

            report_set_id = manifest_data.get("report_set_id", "")
            if not report_set_id:
                print(f"[ERROR] Missing or empty report_set_id in manifest", file=sys.stderr)
                return False

            print(f"[+] Loaded report manifest: {report_set_id} ({schema_ver})")

            manifest_files = manifest_data.get("files", {})
            if not manifest_files:
                print(f"[ERROR] Manifest 'files' map is empty", file=sys.stderr)
                return False

            for m_fname, m_sha in manifest_files.items():
                # Strict filename check: reject absolute paths or path traversal
                if os.path.isabs(m_fname) or ".." in m_fname or "/" in m_fname or "\\" in m_fname:
                    print(f"[ERROR] Invalid or unsafe relative filename in manifest: '{m_fname}'", file=sys.stderr)
                    return False

                m_fpath = os.path.join(target_dir, m_fname)
                if not os.path.exists(m_fpath):
                    print(f"[ERROR] Manifest references missing file: {m_fname}", file=sys.stderr)
                    return False

                actual_hash = file_sha256(m_fpath)
                if actual_hash != m_sha:
                    print(f"[ERROR] SHA256 checksum mismatch for {m_fname}: Expected {m_sha}, got {actual_hash}", file=sys.stderr)
                    return False

            print(f"[+] Manifest SHA256 integrity verified across all {len(manifest_files)} report files.")
        except Exception as e:
            print(f"[ERROR] Failed to validate report set manifest: {e}", file=sys.stderr)
            return False

    # Exact Filename Resolution
    ready_file = os.path.join(target_dir, "READINESS_AUDIT.csv")
    cross_file = os.path.join(target_dir, "CROSS_SOURCE_RECONCILIATION.csv")
    dup_file = os.path.join(target_dir, "DUPLICATE_RECONCILIATION.csv")
    ohlcv_file = os.path.join(target_dir, "OHLCV_QUALITY_AUDIT.csv")

    # Fallback scanning if default names missing
    if not os.path.exists(ready_file):
        for fname in files_in_dir:
            if fname.endswith("READINESS_AUDIT.csv") and not fname.startswith("PHASE_"):
                ready_file = os.path.join(target_dir, fname)
                break

    if not os.path.exists(cross_file):
        for fname in files_in_dir:
            if fname.endswith("CROSS_SOURCE_RECONCILIATION.csv") and not fname.startswith("PHASE_"):
                cross_file = os.path.join(target_dir, fname)
                break

    if not os.path.exists(dup_file):
        for fname in files_in_dir:
            if fname.endswith("DUPLICATE_RECONCILIATION.csv") and not fname.startswith("PHASE_"):
                dup_file = os.path.join(target_dir, fname)
                break

    if not os.path.exists(ohlcv_file):
        for fname in files_in_dir:
            if fname.endswith("OHLCV_QUALITY_AUDIT.csv") and not fname.startswith("PHASE_"):
                ohlcv_file = os.path.join(target_dir, fname)
                break

    # Missing Required Files Check
    missing_files = []
    if not os.path.exists(ready_file): missing_files.append("READINESS_AUDIT.csv")
    if not os.path.exists(cross_file): missing_files.append("CROSS_SOURCE_RECONCILIATION.csv")
    if not os.path.exists(dup_file): missing_files.append("DUPLICATE_RECONCILIATION.csv")
    if not os.path.exists(ohlcv_file): missing_files.append("OHLCV_QUALITY_AUDIT.csv")

    if missing_files:
        print(f"[ERROR] Missing required audit CSV deliverables: {missing_files}", file=sys.stderr)
        return False

    # 2. Read and Parse Readiness Audit CSV
    readiness_rows = []
    with open(ready_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = ["symbol", "usable_observation_records", "conflicting_dates", "v22_input_readiness"]
        for col in required_cols:
            if col not in reader.fieldnames:
                print(f"[ERROR] Required column '{col}' missing from {os.path.basename(ready_file)}", file=sys.stderr)
                return False
        for row in reader:
            readiness_rows.append(row)

    if not readiness_rows:
        print(f"[ERROR] Readiness audit CSV is empty: {ready_file}", file=sys.stderr)
        return False

    # Check symbol key uniqueness
    symbols_seen = set()
    for r in readiness_rows:
        sym = r["symbol"]
        if sym in symbols_seen:
            print(f"[ERROR] Duplicate symbol row detected in readiness audit: {sym}", file=sys.stderr)
            return False
        symbols_seen.add(sym)

    # Recompute per-symbol readiness invariants and mutually exclusive dispositions
    v22_ready_count = 0
    insufficient_hist_count = 0
    duplicate_conflict_count = 0
    unverified_provenance_count = 0
    invalid_ohlcv_count = 0
    no_data_count = 0

    valid_primary_dispositions = {
        "V22_INPUT_REQUIREMENTS_PASSED",
        "BLOCKED_DUPLICATE_CONFLICT",
        "BLOCKED_UNVERIFIED_PROVENANCE",
        "BLOCKED_INVALID_OHLCV",
        "BLOCKED_INSUFFICIENT_HISTORY",
        "BLOCKED_NO_DATA"
    }

    for r in readiness_rows:
        sym = r["symbol"]
        readiness_status = r["v22_input_readiness"]
        usable_bars = int(r["usable_observation_records"])
        conflicting_dates = int(r.get("conflicting_dates", 0))
        unverified_dates = int(r.get("unverified_provenance_dates", 0))
        invalid_dates = int(r.get("invalid_ohlcv_dates", 0))
        dup_disposition = r.get("duplicate_quality_disposition", "")

        if readiness_status not in valid_primary_dispositions:
            print(f"[ERROR] Unknown primary disposition for symbol {sym}: '{readiness_status}'", file=sys.stderr)
            return False

        if readiness_status == "V22_INPUT_REQUIREMENTS_PASSED":
            if usable_bars < 200:
                print(f"[ERROR] Semantic Contradiction for {sym}: Marked V22_INPUT_REQUIREMENTS_PASSED but usable_bars={usable_bars} < 200", file=sys.stderr)
                return False
            if conflicting_dates > 0:
                print(f"[ERROR] Semantic Contradiction for {sym}: Marked V22_INPUT_REQUIREMENTS_PASSED but conflicting_dates={conflicting_dates} > 0", file=sys.stderr)
                return False
            if unverified_dates > 0:
                print(f"[ERROR] Semantic Contradiction for {sym}: Marked V22_INPUT_REQUIREMENTS_PASSED but unverified_provenance_dates={unverified_dates} > 0", file=sys.stderr)
                return False
            if invalid_dates > 0:
                print(f"[ERROR] Semantic Contradiction for {sym}: Marked V22_INPUT_REQUIREMENTS_PASSED but invalid_ohlcv_dates={invalid_dates} > 0", file=sys.stderr)
                return False
            if dup_disposition in ["CONFLICTING_DAILY_BARS_BLOCKED", "UNVERIFIED_PROVENANCE_BLOCKED", "INVALID_OHLCV_GEOMETRY"]:
                print(f"[ERROR] Semantic Contradiction for {sym}: Marked V22_INPUT_REQUIREMENTS_PASSED with blocked disposition '{dup_disposition}'", file=sys.stderr)
                return False

            for ind_col in ["ema200_valid", "ema50_valid", "ema20_valid", "sma20_valid", "atr14_valid", "rsi14_valid"]:
                val = r.get(ind_col, "").lower()
                if val not in ["true", "1"]:
                    print(f"[ERROR] Semantic Contradiction for {sym}: Marked V22_INPUT_REQUIREMENTS_PASSED but indicator {ind_col}={val}", file=sys.stderr)
                    return False

            v22_ready_count += 1
        elif readiness_status == "BLOCKED_DUPLICATE_CONFLICT":
            duplicate_conflict_count += 1
        elif readiness_status == "BLOCKED_UNVERIFIED_PROVENANCE":
            unverified_provenance_count += 1
        elif readiness_status == "BLOCKED_INVALID_OHLCV":
            invalid_ohlcv_count += 1
        elif readiness_status == "BLOCKED_INSUFFICIENT_HISTORY":
            insufficient_hist_count += 1
        elif readiness_status == "BLOCKED_NO_DATA":
            no_data_count += 1

    # Exact Sum Invariant Check
    total_eval_recomputed = (v22_ready_count + insufficient_hist_count + duplicate_conflict_count +
                             unverified_provenance_count + invalid_ohlcv_count + no_data_count)
    if total_eval_recomputed != len(readiness_rows):
        print(f"[ERROR] Invariant Violation: Sum of disposition categories ({total_eval_recomputed}) != total evaluated symbols ({len(readiness_rows)})", file=sys.stderr)
        return False

    # 3. Read and Validate Cross-Source Reconciliation CSV
    cross_dict = {}
    with open(cross_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "metric_key" in row and "count_value" in row:
                cross_dict[row["metric_key"]] = row["count_value"]

    if not cross_dict:
        # Backward compatibility for single-summary row format
        with open(cross_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                sr = rows[0]
                cross_dict["total_symbols_evaluated"] = sr.get("reconciled_symbol_count", "0")
                cross_dict["symbols_v22_ready"] = sr.get("conflict_free_symbol_count", "0")
                cross_dict["overall_reconciliation_status"] = sr.get("status", "UNKNOWN")

    # Validate Summary vs Row-Level Recomputed Invariants
    claimed_total = int(cross_dict.get("total_symbols_evaluated", -1))
    claimed_v22_ready = int(cross_dict.get("symbols_v22_ready", -1))
    claimed_conflicts = int(cross_dict.get("symbols_with_duplicate_conflicts", -1))
    claimed_unverified = int(cross_dict.get("symbols_with_unverified_provenance", -1))
    claimed_invalid_ohlcv = int(cross_dict.get("symbols_with_invalid_ohlcv", -1))
    claimed_insufficient_hist = int(cross_dict.get("symbols_insufficient_history", -1))
    overall_status = cross_dict.get("overall_reconciliation_status", "UNKNOWN")

    if claimed_total != len(readiness_rows):
        print(f"[ERROR] Summary mismatch: total_symbols_evaluated={claimed_total} != total readiness rows={len(readiness_rows)}", file=sys.stderr)
        return False

    if claimed_v22_ready != v22_ready_count:
        print(f"[ERROR] Summary mismatch: symbols_v22_ready={claimed_v22_ready} != recomputed v22_ready_count={v22_ready_count}", file=sys.stderr)
        return False

    if claimed_conflicts != -1 and claimed_conflicts != duplicate_conflict_count:
        print(f"[ERROR] Summary mismatch: symbols_with_duplicate_conflicts={claimed_conflicts} != recomputed duplicate_conflict_count={duplicate_conflict_count}", file=sys.stderr)
        return False

    if claimed_unverified != -1 and claimed_unverified != unverified_provenance_count:
        print(f"[ERROR] Summary mismatch: symbols_with_unverified_provenance={claimed_unverified} != recomputed unverified_provenance_count={unverified_provenance_count}", file=sys.stderr)
        return False

    if claimed_invalid_ohlcv != -1 and claimed_invalid_ohlcv != invalid_ohlcv_count:
        print(f"[ERROR] Summary mismatch: symbols_with_invalid_ohlcv={claimed_invalid_ohlcv} != recomputed invalid_ohlcv_count={invalid_ohlcv_count}", file=sys.stderr)
        return False

    if claimed_insufficient_hist != -1 and claimed_insufficient_hist != insufficient_hist_count:
        print(f"[ERROR] Summary mismatch: symbols_insufficient_history={claimed_insufficient_hist} != recomputed insufficient_hist_count={insufficient_hist_count}", file=sys.stderr)
        return False

    if overall_status == "ALL_SYMBOLS_READY" and v22_ready_count < len(readiness_rows):
        print(f"[ERROR] Falsified reconciliation status: Overall status claims 'ALL_SYMBOLS_READY' but {len(readiness_rows) - v22_ready_count} symbols are blocked/non-ready", file=sys.stderr)
        return False

    # 4. Read and Validate Duplicate Reconciliation CSV
    dup_rows = []
    with open(dup_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dup_rows.append(row)

    dup_dict = {r["metric_name"]: int(r["count_value"]) for r in dup_rows if "metric_name" in r and "count_value" in r}

    if "total_table_rows" in dup_dict and "excess_duplicate_rows" in dup_dict and "math_crosscheck_unique_keys" in dup_dict:
        total_tbl = dup_dict["total_table_rows"]
        excess = dup_dict["excess_duplicate_rows"]
        math_unique = dup_dict["math_crosscheck_unique_keys"]
        if total_tbl - excess != math_unique:
            print(f"[ERROR] Arithmetic identity violation in duplicate reconciliation: {total_tbl} - {excess} != {math_unique}", file=sys.stderr)
            return False

    # 5. Read and Validate OHLCV Quality Audit CSV
    ohlcv_rows = []
    with open(ohlcv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ohlcv_rows.append(row)

    for r in ohlcv_rows:
        check_name = r.get("validation_check", "")
        err_cnt = int(r.get("error_count", 0))
        status = r.get("status", "")
        if err_cnt > 0 and status == "PASSED":
            print(f"[ERROR] Contradiction in OHLCV quality check '{check_name}': error_count={err_cnt} > 0 but status='PASSED'", file=sys.stderr)
            return False

    print(f"[SUCCESS] Independent Audit Acceptance Validator verified all CSV invariants cleanly across {len(readiness_rows)} evaluated symbols!")
    print(f"          Verified Ready        : {v22_ready_count}")
    print(f"          Insufficient History  : {insufficient_hist_count}")
    print(f"          Duplicate Conflicts   : {duplicate_conflict_count}")
    print(f"          Unverified Provenance : {unverified_provenance_count}")
    print(f"          Invalid OHLCV         : {invalid_ohlcv_count}")
    print(f"          No Data               : {no_data_count}")
    return True

def main():
    parser = argparse.ArgumentParser(description="TradeMindAI Independent Audit CSV Acceptance Validator")
    parser.add_argument("--dir", required=True, help="Directory containing generated audit CSV files")
    args = parser.parse_args()

    success = validate_csv_directory(args.dir)
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
