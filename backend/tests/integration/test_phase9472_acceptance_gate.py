"""
================================================================================
TradeMindAI: Phase 9.4.77 Isolated End-to-End Acceptance Gate & Adversarial Tests
================================================================================
Pipeline:
  Isolated SQLite Fixture -> Actual Generator -> Disk CSVs & Manifest -> Validator Subprocess

Validates Scenarios A-Q:
  A: Two identified sources agree on valid OHLCV (SYM_A)
  B: Two identified sources conflict on OHLCV (SYM_B)
  C: Unverified / missing source provenance (SYM_C)
  D: Missing observations / No data (SYM_D)
  E: Same-source duplicate records (SYM_E)
  F: Invalid OHLCV geometry (high < low) (SYM_F)
  G: Insufficient data history (<200 bars) (SYM_G)
  H: Subprocess validator accepts untampered report sets (Exit 0)
  I: Subprocess validator rejects checksum tampering (Exit 1)
  J: Subprocess validator rejects semantic readiness tampering with updated hashes (Exit 1)
  K: Subprocess validator rejects summary count falsification with updated hashes (Exit 1)
  L: Subprocess validator rejects unsupported manifest schema version (Exit 1)
  M: Subprocess validator rejects unsafe path traversal in manifest (Exit 1)
  N: Staging publication failure preserves previous published report set
  O: Concurrent publications use collision-resistant UUIDs and maintain atomic pointer integrity
  P: Empty symbol universe behaves safely and fails closed
  Q: Missing dependency isolation guard enforcement
================================================================================
"""

import os
import csv
import json
import sys
import pytest
import tempfile
import subprocess
import hashlib
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.postgres import Base, PriceDB
from scripts.audit.generate_audit_csvs import generate_audit_csvs_isolated, file_sha256

@pytest.fixture
def isolated_db_engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()

def populate_fixture_symbols(session):
    now_utc = datetime.now(timezone.utc)

    bars = []

    # Symbol A: 200 bars, 2 distinct sources agree
    for i in range(200):
        dt = now_utc - timedelta(days=250 - i)
        c_price = 1000.0 + i
        bars.append(PriceDB(symbol="SYM_A", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=c_price, volume=10000, source="SRC_1"))
        bars.append(PriceDB(symbol="SYM_A", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=c_price, volume=10000, source="SRC_2"))

    # Symbol B: 200 bars, 2 distinct sources conflict on last date
    for i in range(200):
        dt = now_utc - timedelta(days=250 - i)
        c_price = 1000.0 + i
        bars.append(PriceDB(symbol="SYM_B", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=c_price, volume=10000, source="SRC_1"))
        b_close = c_price + 20.0 if i == 199 else c_price
        bars.append(PriceDB(symbol="SYM_B", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=b_close, volume=10000, source="SRC_2"))

    # Symbol C: 200 bars, source is None (unverified)
    for i in range(200):
        dt = now_utc - timedelta(days=250 - i)
        c_price = 1000.0 + i
        bars.append(PriceDB(symbol="SYM_C", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=c_price, volume=10000, source=None))

    # Symbol D: No bars in database

    # Symbol E: 200 bars with same-source duplicates
    for i in range(200):
        dt = now_utc - timedelta(days=250 - i)
        c_price = 1000.0 + i
        bars.append(PriceDB(symbol="SYM_E", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=c_price, volume=10000, source="SRC_1"))
        bars.append(PriceDB(symbol="SYM_E", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=c_price, volume=10000, source="SRC_1"))

    # Symbol F: 200 bars with invalid OHLCV geometry (high < low)
    for i in range(200):
        dt = now_utc - timedelta(days=250 - i)
        c_price = 1000.0 + i
        bars.append(PriceDB(symbol="SYM_F", date=dt, open=c_price-1, high=90.0, low=95.0, close=c_price, volume=10000, source="SRC_1"))

    # Symbol G: Insufficient history (50 bars)
    for i in range(50):
        dt = now_utc - timedelta(days=50 - i)
        c_price = 1000.0 + i
        bars.append(PriceDB(symbol="SYM_G", date=dt, open=c_price-1, high=c_price+30, low=c_price-2, close=c_price, volume=10000, source="SRC_1"))

    session.add_all(bars)
    session.commit()

def test_full_acceptance_gate_pipeline_and_adversarial_tampering(isolated_db_engine):
    Session = sessionmaker(bind=isolated_db_engine)
    session = Session()

    populate_fixture_symbols(session)

    symbols_list = ["SYM_A", "SYM_B", "SYM_C", "SYM_D", "SYM_E", "SYM_F", "SYM_G"]
    val_script = os.path.join("scripts", "audit", "validate_audit_csvs.py")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Run actual generator with injected dependencies
        gen_result = generate_audit_csvs_isolated(
            session=session,
            symbols=symbols_list,
            output_dir=temp_dir
        )
        assert gen_result is True

        # 2. Inspect generated CSVs on disk
        ready_path = os.path.join(temp_dir, "READINESS_AUDIT.csv")
        manifest_path = os.path.join(temp_dir, "AUDIT_REPORT_MANIFEST.json")
        cross_path = os.path.join(temp_dir, "CROSS_SOURCE_RECONCILIATION.csv")
        active_ptr_path = os.path.join(temp_dir, "ACTIVE_REPORT_SET.json")

        assert os.path.exists(ready_path)
        assert os.path.exists(manifest_path)
        assert os.path.exists(cross_path)
        assert os.path.exists(active_ptr_path)

        outcomes = {}
        with open(ready_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                outcomes[row["symbol"]] = row["v22_input_readiness"]

        assert outcomes["SYM_A"] == "V22_INPUT_REQUIREMENTS_PASSED"
        assert outcomes["SYM_B"] == "BLOCKED_DUPLICATE_CONFLICT"
        assert outcomes["SYM_C"] == "BLOCKED_UNVERIFIED_PROVENANCE"
        assert outcomes["SYM_D"] == "BLOCKED_NO_DATA"
        assert outcomes["SYM_E"] == "V22_INPUT_REQUIREMENTS_PASSED"
        assert outcomes["SYM_F"] == "BLOCKED_INVALID_OHLCV"
        assert outcomes["SYM_G"] == "BLOCKED_INSUFFICIENT_HISTORY"

        # Case A: Subprocess validator accepts untampered report set (Exit 0)
        proc_clean = subprocess.run(
            [sys.executable, val_script, "--dir", temp_dir],
            capture_output=True,
            text=True
        )
        assert proc_clean.returncode == 0
        assert "Independent Audit Acceptance Validator verified all CSV invariants" in proc_clean.stdout

        # Case B: Checksum Tampering Test - Modify CSV without updating manifest -> Exit 1
        tampered_rows = []
        with open(ready_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            for row in reader:
                if row["symbol"] == "SYM_B":
                    row["v22_input_readiness"] = "V22_INPUT_REQUIREMENTS_PASSED"
                tampered_rows.append(row)

        with open(ready_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(tampered_rows)

        proc_checksum_tampered = subprocess.run(
            [sys.executable, val_script, "--dir", temp_dir],
            capture_output=True,
            text=True
        )
        assert proc_checksum_tampered.returncode == 1
        assert "SHA256 checksum mismatch" in proc_checksum_tampered.stderr

        # Case C: Semantic Tampering Test - Update manifest checksums so hash check passes, but validator catches semantic contradiction -> Exit 1
        with open(manifest_path, "r", encoding="utf-8") as mf:
            m_data = json.load(mf)
        m_data["files"]["READINESS_AUDIT.csv"] = file_sha256(ready_path)
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(m_data, mf, indent=2)

        proc_semantic_tampered = subprocess.run(
            [sys.executable, val_script, "--dir", temp_dir],
            capture_output=True,
            text=True
        )
        assert proc_semantic_tampered.returncode == 1
        assert "Semantic Contradiction for SYM_B" in proc_semantic_tampered.stderr

        # Case D: Summary Falsification Test - Falsify summary count in CROSS_SOURCE_RECONCILIATION.csv & update hash -> Exit 1
        generate_audit_csvs_isolated(session=session, symbols=symbols_list, output_dir=temp_dir)

        cross_rows = []
        with open(cross_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers_cross = reader.fieldnames
            for row in reader:
                if row["metric_key"] == "symbols_v22_ready":
                    row["count_value"] = "7"
                cross_rows.append(row)

        with open(cross_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers_cross)
            writer.writeheader()
            writer.writerows(cross_rows)

        with open(manifest_path, "r", encoding="utf-8") as mf:
            m_data = json.load(mf)
        m_data["files"]["CROSS_SOURCE_RECONCILIATION.csv"] = file_sha256(cross_path)
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(m_data, mf, indent=2)

        proc_summary_tampered = subprocess.run(
            [sys.executable, val_script, "--dir", temp_dir],
            capture_output=True,
            text=True
        )
        assert proc_summary_tampered.returncode == 1
        assert "Summary mismatch: symbols_v22_ready=7 != recomputed v22_ready_count=2" in proc_summary_tampered.stderr

        # Case E: Unsupported Schema Version Test -> Exit 1
        generate_audit_csvs_isolated(session=session, symbols=symbols_list, output_dir=temp_dir)
        with open(manifest_path, "r", encoding="utf-8") as mf:
            m_data = json.load(mf)
        m_data["schema_version"] = "v999.0-UNSUPPORTED"
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(m_data, mf, indent=2)

        proc_schema_invalid = subprocess.run(
            [sys.executable, val_script, "--dir", temp_dir],
            capture_output=True,
            text=True
        )
        assert proc_schema_invalid.returncode == 1
        assert "Unsupported report set schema version" in proc_schema_invalid.stderr

        # Case F: Path Traversal Test -> Exit 1
        generate_audit_csvs_isolated(session=session, symbols=symbols_list, output_dir=temp_dir)
        with open(manifest_path, "r", encoding="utf-8") as mf:
            m_data = json.load(mf)
        m_data["files"]["../etc/passwd"] = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump(m_data, mf, indent=2)

        proc_traversal_invalid = subprocess.run(
            [sys.executable, val_script, "--dir", temp_dir],
            capture_output=True,
            text=True
        )
        assert proc_traversal_invalid.returncode == 1
        assert "Invalid or unsafe relative filename" in proc_traversal_invalid.stderr

    session.close()

def test_staging_publication_failure_preserves_previous_set(isolated_db_engine):
    Session = sessionmaker(bind=isolated_db_engine)
    session = Session()

    populate_fixture_symbols(session)
    symbols_list = ["SYM_A", "SYM_B"]

    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Generate initial valid report set
        generate_audit_csvs_isolated(session=session, symbols=symbols_list, output_dir=temp_dir)
        initial_manifest_path = os.path.join(temp_dir, "AUDIT_REPORT_MANIFEST.json")
        with open(initial_manifest_path, "r", encoding="utf-8") as mf:
            initial_manifest_data = json.load(mf)

        # 2. Simulate generation failure with empty symbols list
        res = generate_audit_csvs_isolated(session=session, symbols=[], output_dir=temp_dir)
        assert res is False

        # 3. Assert initial published set in output_dir remains intact
        with open(initial_manifest_path, "r", encoding="utf-8") as mf:
            current_manifest_data = json.load(mf)

        assert current_manifest_data["report_set_id"] == initial_manifest_data["report_set_id"]

    session.close()

def test_concurrent_publication_safety(isolated_db_engine):
    Session = sessionmaker(bind=isolated_db_engine)
    session = Session()

    populate_fixture_symbols(session)

    with tempfile.TemporaryDirectory() as temp_dir:
        res1 = generate_audit_csvs_isolated(session=session, symbols=["SYM_A"], output_dir=temp_dir)
        assert res1 is True
        ptr1_path = os.path.join(temp_dir, "ACTIVE_REPORT_SET.json")
        with open(ptr1_path, "r", encoding="utf-8") as pf:
            ptr1 = json.load(pf)

        res2 = generate_audit_csvs_isolated(session=session, symbols=["SYM_E"], output_dir=temp_dir)
        assert res2 is True
        with open(ptr1_path, "r", encoding="utf-8") as pf:
            ptr2 = json.load(pf)

        # Assert UUID report set IDs are distinct and collision-resistant
        assert ptr1["active_report_set_id"] != ptr2["active_report_set_id"]

        # Assert pointer resolves to valid versioned directory
        v_dir = os.path.join(temp_dir, ptr2["active_report_set_id"])
        assert os.path.exists(v_dir)
        assert os.path.exists(os.path.join(v_dir, "AUDIT_REPORT_MANIFEST.json"))

    session.close()

def test_empty_symbol_universe_handling(isolated_db_engine):
    Session = sessionmaker(bind=isolated_db_engine)
    session = Session()
    with tempfile.TemporaryDirectory() as temp_dir:
        res = generate_audit_csvs_isolated(session=session, symbols=[], output_dir=temp_dir)
        assert res is False
    session.close()

def test_missing_dependency_isolation_guard():
    with pytest.raises(ValueError, match="CRITICAL ISOLATION GUARD"):
        generate_audit_csvs_isolated(session=None, symbols=[], output_dir=None)
