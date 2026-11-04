import os
import json
import pytest
import duckdb
import pandas as pd
import numpy as np
from pathlib import Path
from scripts.ingest_historical_nifty500 import (
    validate_and_normalize_ohlcv,
    get_provider_ticker,
    recover_pending_transactions,
    ingest_symbol,
    save_journal,
    load_checkpoint,
    save_checkpoint,
    POST_2015_LISTING_DATES
)
from scripts.audit.generate_coverage_csvs import audit_symbol_record, MUTUALLY_EXCLUSIVE_STATUSES
from scripts.audit.generate_r4_reports import compare_pilot_full_table_integrity, audit_symbol_record_direct_r4613
from backend.app.db.nifty500_symbols import get_nifty_500_universe
from backend.services.coverage_engine import evaluate_symbol_date_set_coverage

def test_get_provider_ticker_alias_resolution():
    assert get_provider_ticker("L&TFH") == "LTF.NS"
    assert get_provider_ticker("RELIANCE") == "RELIANCE.NS"

def test_validate_and_normalize_ohlcv_valid():
    dates = pd.date_range("2026-01-01", periods=5, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
        "High": [105.0, 106.0, 107.0, 108.0, 109.0],
        "Low": [95.0, 96.0, 97.0, 98.0, 99.0],
        "Close": [102.0, 103.0, 104.0, 105.0, 106.0],
        "Volume": [1000, 2000, 3000, 4000, 5000]
    })
    df_clean = validate_and_normalize_ohlcv(df, "TEST")
    assert len(df_clean) == 5
    assert list(df_clean.columns) == ["date", "Open", "High", "Low", "Close", "Volume"]

def test_validate_and_normalize_ohlcv_invalid_geometry():
    dates = pd.date_range("2026-01-01", periods=1, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "Open": [100.0],
        "High": [90.0], # High < Low
        "Low": [95.0],
        "Close": [102.0],
        "Volume": [1000]
    })
    with pytest.raises(ValueError, match="OHLC geometry violations detected"):
        validate_and_normalize_ohlcv(df, "TEST")

def test_validate_and_normalize_ohlcv_non_positive_price():
    dates = pd.date_range("2026-01-01", periods=1, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "Open": [100.0],
        "High": [105.0],
        "Low": [-5.0], # Invalid negative price
        "Close": [102.0],
        "Volume": [1000]
    })
    with pytest.raises(ValueError, match="Non-positive prices detected"):
        validate_and_normalize_ohlcv(df, "TEST")

def test_provider_response_normalization_multiindex_flattening():
    # Simulate yfinance MultiIndex column structure
    tuples = [("Close", "RELIANCE.NS"), ("High", "RELIANCE.NS"), ("Low", "RELIANCE.NS"), ("Open", "RELIANCE.NS"), ("Volume", "RELIANCE.NS")]
    cols = pd.MultiIndex.from_tuples(tuples)
    df_multi = pd.DataFrame([
        [102.0, 105.0, 95.0, 100.0, 1000],
        [103.0, 106.0, 96.0, 101.0, 2000]
    ], columns=cols, index=pd.date_range("2026-01-01", periods=2, freq="D"))

    df_clean = validate_and_normalize_ohlcv(df_multi, "RELIANCE")
    assert len(df_clean) == 2
    assert list(df_clean.columns) == ["date", "Open", "High", "Low", "Close", "Volume"]

def test_empty_dataframe_raises_value_error():
    with pytest.raises(ValueError, match="empty or None"):
        validate_and_normalize_ohlcv(pd.DataFrame(), "EMPTY_SYM")

def test_duplicate_date_rejection_in_daily_ohlcv():
    dates = ["2026-01-01", "2026-01-01", "2026-01-02"]
    df_raw = pd.DataFrame({
        "date": dates,
        "Open": [100.0, 100.5, 102.0],
        "High": [105.0, 105.5, 107.0],
        "Low": [95.0, 95.5, 98.0],
        "Close": [102.0, 102.5, 106.0],
        "Volume": [1000, 1200, 1500]
    })
    with pytest.raises(ValueError, match="Duplicate dates detected"):
        validate_and_normalize_ohlcv(df_raw, "DUP_SYM")

def test_checkpoint_resume_from_verified_state(tmp_path):
    cp_path = tmp_path / "checkpoint.json"
    cp_data = {
        "RELIANCE": {"status": "SUCCESS", "rows": 2500, "earliest_date": "2015-01-01", "latest_date": "2026-01-01"}
    }
    save_checkpoint(cp_data, target=cp_path)

    loaded = load_checkpoint(cp_path)
    assert loaded["RELIANCE"]["status"] == "SUCCESS"
    assert loaded["RELIANCE"]["rows"] == 2500

def test_post_2015_listing_date_resolution():
    assert POST_2015_LISTING_DATES.get("LICI") == "2022-05-17"
    assert POST_2015_LISTING_DATES.get("ATGL") == "2018-11-05"

def test_coverage_categories_mutually_exclusive_sum_500():
    symbols_dict = get_nifty_500_universe()
    assert len(symbols_dict) == 500

    records = [audit_symbol_record(idx, sym, name) for idx, (sym, name) in enumerate(symbols_dict.items(), 1)]
    assert len(records) == 500

    status_counts = {cat: 0 for cat in MUTUALLY_EXCLUSIVE_STATUSES}
    for r in records:
        st = r["coverage_status"]
        assert st in MUTUALLY_EXCLUSIVE_STATUSES, f"Unknown status '{st}' for symbol {r['canonical_symbol']}"
        status_counts[st] += 1

    total_accounted = sum(status_counts.values())
    assert total_accounted == 500

def test_full_table_integrity_detects_value_mismatch():
    p_df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 103.0],
        "Volume": [1000, 2000]
    }).set_index("date")

    d_df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 150.0], # Mismatched close price on second row
        "Volume": [1000, 2000]
    }).set_index("date")

    diff_mask = (
        ((p_df['Open'] - d_df['Open']).abs() > 1e-4) |
        ((p_df['High'] - d_df['High']).abs() > 1e-4) |
        ((p_df['Low'] - d_df['Low']).abs() > 1e-4) |
        ((p_df['Close'] - d_df['Close']).abs() > 1e-4) |
        ((p_df['Volume'] - d_df['Volume']).abs() > 1e-4)
    )
    mismatches = int(diff_mask.sum())
    assert mismatches == 1

def test_production_function_compare_pilot_full_table_integrity_detects_value_mismatch(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    p_file = feat_dir / "TESTSYM.parquet"

    df_p = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 103.0],
        "Volume": [1000.0, 2000.0]
    })
    df_p.to_parquet(p_file, index=False)

    db_path = tmp_path / "test.duckdb"
    con = duckdb.connect(str(db_path))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    # Insert modified Close price on second row
    con.execute("INSERT INTO daily_ohlcv VALUES ('TESTSYM', '2026-01-01', 100.0, 105.0, 95.0, 102.0, 1000.0, 'SRC', 'TS')")
    con.execute("INSERT INTO daily_ohlcv VALUES ('TESTSYM', '2026-01-02', 101.0, 106.0, 96.0, 999.0, 2000.0, 'SRC', 'TS')") # Close 999.0 vs 103.0

    rec = compare_pilot_full_table_integrity("TESTSYM", con, feat_dir)
    con.close()

    assert rec["integrity_status"] == "FAIL_OHLCV_VALUE_MISMATCH"
    assert rec["full_table_value_mismatch_count"] == 1

def test_exact_date_set_equality_passes_coverage_engine():
    expected = {"2026-01-01", "2026-01-02", "2026-01-03"}
    observed = ["2026-01-01", "2026-01-02", "2026-01-03"]
    res = evaluate_symbol_date_set_coverage("TEST", "Test Co", observed, expected, calendar_verified=True, listing_verified=True, verified_listing_date="2026-01-01")
    assert res["coverage_status"] == "COMPLETE_POST_LISTING_COVERAGE"
    assert res["missing_session_count"] == 0
    assert res["unexpected_session_count"] == 0

def test_date_substitution_detects_missing_and_unexpected_sessions():
    expected = {"2026-01-01", "2026-01-02", "2026-01-03"}
    # Substitute 2026-01-02 with 2026-01-04 (same row count 3, but different date set!)
    observed = ["2026-01-01", "2026-01-04", "2026-01-03"]
    res = evaluate_symbol_date_set_coverage("TEST", "Test Co", observed, expected, calendar_verified=True, listing_verified=True, verified_listing_date="2026-01-01")
    assert res["coverage_status"] == "PARTIAL_HISTORY"
    assert res["missing_session_count"] == 1 # 2026-01-02 missing
    assert res["unexpected_session_count"] == 1 # 2026-01-04 unexpected

def test_unverified_calendar_blocks_complete_status():
    expected = {"2026-01-01", "2026-01-02"}
    observed = ["2026-01-01", "2026-01-02"]
    res = evaluate_symbol_date_set_coverage("TEST", "Test Co", observed, expected, calendar_verified=False, listing_verified=True, verified_listing_date="2026-01-01")
    assert res["coverage_status"] == "SESSION_CALENDAR_UNVERIFIED"

def test_unverified_listing_date_blocks_complete_status():
    expected = {"2026-01-01", "2026-01-02"}
    observed = ["2026-01-01", "2026-01-02"]
    res = evaluate_symbol_date_set_coverage("TEST", "Test Co", observed, expected, calendar_verified=True, listing_verified=False, verified_listing_date="2026-01-01")
    assert res["coverage_status"] == "LISTING_DATE_UNVERIFIED"

def test_r4613_report_generator_invokes_direct_coverage_engine_path():
    symbols_dict = get_nifty_500_universe()
    feat_dir = Path("backend/data/features")
    rec = audit_symbol_record_direct_r4613(1, "RELIANCE", symbols_dict["RELIANCE"], feat_dir)
    assert "coverage_status" in rec
    assert "missing_session_count" in rec
    assert "unexpected_session_count" in rec
    assert rec["canonical_symbol"] == "RELIANCE"

def test_recover_pending_transactions_after_simulated_crash_post_duckdb_commit(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    db_path = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_path))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    con.execute("INSERT INTO daily_ohlcv VALUES ('TESTCRASH', '2026-01-01', 100.0, 105.0, 95.0, 102.0, 1000.0, 'TX_crash_tx_001', 'TS')")
    con.execute("INSERT INTO daily_ohlcv VALUES ('TESTCRASH', '2026-01-02', 101.0, 106.0, 96.0, 103.0, 2000.0, 'TX_crash_tx_001', 'TS')")
    con.close()

    staged_p = feat_dir / "TESTCRASH.staged.parquet"
    final_p = feat_dir / "TESTCRASH.parquet"

    df_staged = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 103.0],
        "Volume": [1000.0, 2000.0]
    })
    df_staged.to_parquet(staged_p, index=False)

    j_path = tmp_path / "journal.json"
    journal = {
        "TESTCRASH": {
            "tx_id": "crash_tx_001",
            "status": "COMMITTED_DUCKDB",
            "staged_parquet_path": str(staged_p),
            "target_parquet_path": str(final_p)
        }
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    # Assert final Parquet file does not exist before recovery
    assert not final_p.exists()
    assert staged_p.exists()

    # Run recovery protocol after simulated process crash post-DuckDB commit
    recovered = recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=db_path)

    assert recovered == 1
    assert final_p.exists()
    assert not staged_p.exists()

    # Verify recovered Parquet contents
    df_recovered = pd.read_parquet(final_p)
    assert len(df_recovered) == 2
    assert list(df_recovered["date"]) == ["2026-01-01", "2026-01-02"]

    # Verify idempotency: running recovery a second time returns 0 recovered
    recovered_again = recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=db_path)
    assert recovered_again == 0

def test_recovery_protocol_reconciles_post_duckdb_commit_crash_with_real_database(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    db_path = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_path))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    # Insert DuckDB rows committed with TX_abc123 tag
    con.execute("INSERT INTO daily_ohlcv VALUES ('TESTREAL', '2026-01-01', 100.0, 105.0, 95.0, 102.0, 1000.0, 'TX_abc123', 'TS')")
    con.execute("INSERT INTO daily_ohlcv VALUES ('TESTREAL', '2026-01-02', 101.0, 106.0, 96.0, 103.0, 2000.0, 'TX_abc123', 'TS')")
    con.close()

    staged_p = feat_dir / "TESTREAL.staged.parquet"
    final_p = feat_dir / "TESTREAL.parquet"

    df_staged = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 103.0],
        "Volume": [1000.0, 2000.0]
    })
    df_staged.to_parquet(staged_p, index=False)

    j_path = tmp_path / "journal.json"
    journal = {
        "TESTREAL": {
            "tx_id": "abc123",
            "status": "PENDING_DUCKDB", # Crash occurred right after DuckDB commit before journal update
            "staged_parquet_path": str(staged_p),
            "target_parquet_path": str(final_p)
        }
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    # Recovery protocol detects DuckDB has TX_abc123 rows and promotes staged Parquet file
    recovered = recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=db_path)

    assert recovered == 1
    assert final_p.exists()
    assert not staged_p.exists()

    df_rec = pd.read_parquet(final_p)
    assert len(df_rec) == 2
    assert list(df_rec["date"]) == ["2026-01-01", "2026-01-02"]

def test_uncommitted_pending_transaction_does_not_promote_staged_parquet_over_old_rows(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    db_path = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_path))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    # Insert OLD DuckDB rows committed in a previous transaction with TX_old999 tag
    con.execute("INSERT INTO daily_ohlcv VALUES ('TESTOLD', '2025-12-01', 50.0, 55.0, 48.0, 52.0, 500.0, 'TX_old999', 'TS')")
    con.close()

    # Pre-existing old Parquet store
    final_p = feat_dir / "TESTOLD.parquet"
    df_old = pd.DataFrame({
        "date": ["2025-12-01"],
        "Open": [50.0],
        "High": [55.0],
        "Low": [48.0],
        "Close": [52.0],
        "Volume": [500.0]
    })
    df_old.to_parquet(final_p, index=False)

    # Staged Parquet store for NEW uncommitted transaction TX_new000
    staged_p = feat_dir / "TESTOLD.staged.parquet"
    df_new = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "Open": [100.0, 101.0],
        "High": [105.0, 106.0],
        "Low": [95.0, 96.0],
        "Close": [102.0, 103.0],
        "Volume": [1000.0, 2000.0]
    })
    df_new.to_parquet(staged_p, index=False)

    j_path = tmp_path / "journal.json"
    journal = {
        "TESTOLD": {
            "tx_id": "new000", # New transaction ID that was NOT committed in DuckDB
            "status": "PENDING_DUCKDB",
            "staged_parquet_path": str(staged_p),
            "target_parquet_path": str(final_p)
        }
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    # Ambiguous PENDING_DUCKDB with no matching DuckDB transaction rows raises RuntimeError and fails closed, preserving staged_p and final_p!
    with pytest.raises(RuntimeError, match="Ambiguous PENDING_DUCKDB transaction"):
        recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=db_path)

    # Assert both staged_p and final_p remain preserved!
    assert staged_p.exists()
    assert final_p.exists()

    df_preserved = pd.read_parquet(final_p)
    assert len(df_preserved) == 1
    assert list(df_preserved["date"]) == ["2025-12-01"]
    assert df_preserved["Close"].iloc[0] == 52.0

def test_corrupt_journal_file_raises_runtime_error_fail_closed(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()

    j_path = tmp_path / "journal.json"
    j_path.write_text("{CORRUPT_JSON_DATA_MALFORMED", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Corrupt or malformed journal file"):
        recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir)

def test_committed_duckdb_without_duckdb_rows_does_not_promote_staged_parquet(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    db_path = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_path))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    con.close()

    staged_p = feat_dir / "TESTNOCOMMIT.staged.parquet"
    final_p = feat_dir / "TESTNOCOMMIT.parquet"

    df_staged = pd.DataFrame({
        "date": ["2026-01-01"],
        "Open": [100.0],
        "High": [105.0],
        "Low": [95.0],
        "Close": [102.0],
        "Volume": [1000.0]
    })
    df_staged.to_parquet(staged_p, index=False)

    j_path = tmp_path / "journal.json"
    journal = {
        "TESTNOCOMMIT": {
            "tx_id": "missing_tx_999",
            "status": "COMMITTED_DUCKDB", # Journal claims COMMITTED_DUCKDB but DuckDB has NO matching rows!
            "staged_parquet_path": str(staged_p),
            "target_parquet_path": str(final_p)
        }
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    # Recovery fails closed with RuntimeError because journal status COMMITTED_DUCKDB has no matching DuckDB rows
    with pytest.raises(RuntimeError, match="has no matching DuckDB transaction rows"):
        recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=db_path)

def test_missing_duckdb_database_raises_runtime_error_fail_closed(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    non_existent_db_path = tmp_path / "non_existent.duckdb"

    staged_p = feat_dir / "TESTMISSINGDB.staged.parquet"
    final_p = feat_dir / "TESTMISSINGDB.parquet"

    df_staged = pd.DataFrame({
        "date": ["2026-01-01"],
        "Open": [100.0],
        "High": [105.0],
        "Low": [95.0],
        "Close": [102.0],
        "Volume": [1000.0]
    })
    df_staged.to_parquet(staged_p, index=False)

    j_path = tmp_path / "journal.json"
    journal = {
        "TESTMISSINGDB": {
            "tx_id": "tx_missing_db",
            "status": "PENDING_DUCKDB",
            "staged_parquet_path": str(staged_p),
            "target_parquet_path": str(final_p)
        }
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    # Assert recovery raises RuntimeError and fails closed without removing staged Parquet file
    with pytest.raises(RuntimeError, match="DuckDB database missing or unavailable"):
        recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=non_existent_db_path)

    # Staged Parquet file remains preserved!
    assert staged_p.exists()

def test_malformed_non_dictionary_journal_entry_raises_runtime_error(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    db_path = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_path))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    con.close()

    j_path = tmp_path / "journal.json"
    journal = {
        "TESTMALFORMED": "NOT_A_DICTIONARY_ENTRY" # String instead of dictionary object
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    with pytest.raises(RuntimeError, match="Malformed non-dictionary journal entry"):
        recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=db_path)

def test_target_parquet_path_mismatch_raises_runtime_error(tmp_path):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    db_path = tmp_path / "test.duckdb"

    con = duckdb.connect(str(db_path))
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE, source VARCHAR, ingested_at VARCHAR, PRIMARY KEY (symbol, date)
        )
    """)
    con.close()

    j_path = tmp_path / "journal.json"
    journal = {
        "TESTMISMATCH": {
            "tx_id": "tx_mismatch_123",
            "status": "PENDING_DUCKDB",
            "staged_parquet_path": str(feat_dir / "TESTMISMATCH.staged.parquet"),
            "target_parquet_path": str(feat_dir / "WRONGSYMBOL.parquet") # Path filename does NOT match TESTMISMATCH.parquet!
        }
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    with pytest.raises(RuntimeError, match="Target Parquet path mismatch for symbol"):
        recover_pending_transactions(custom_journal_path=j_path, custom_feat_dir=feat_dir, custom_db_path=db_path)

def test_failed_journal_entry_blocks_ingestion_retry(tmp_path, monkeypatch):
    feat_dir = tmp_path / "features"
    feat_dir.mkdir()
    db_path = tmp_path / "test.duckdb"
    cp_file = tmp_path / "checkpoint.json"

    j_path = tmp_path / "journal.json"
    journal = {
        "RELIANCE": {
            "tx_id": "failed_tx_123",
            "status": "FAILED",
            "error": "Simulated DuckDB error",
            "failed_at": "2026-10-27T00:00:00Z"
        }
    }
    j_path.write_text(json.dumps(journal), encoding="utf-8")

    # Patch journal path to use custom j_path
    monkeypatch.setattr("scripts.ingest_historical_nifty500.journal_path", j_path)

    with pytest.raises(RuntimeError, match="Unresolved FAILED journal entry exists for symbol 'RELIANCE'"):
        ingest_symbol("RELIANCE", f_dir_p=feat_dir, db_p=db_path, cp_path=cp_file, j_path=j_path)

    # Verify FAILED journal entry remains preserved and intact!
    journal_after = json.loads(j_path.read_text(encoding="utf-8"))
    assert journal_after["RELIANCE"]["status"] == "FAILED"
    assert journal_after["RELIANCE"]["error"] == "Simulated DuckDB error"
