"""
================================================================================
TradeMindAI Unit Tests — Signal Export Schema & Output Contract (Fix 1)
================================================================================
Directly exercises build_export_payload() and write_export_payload() from
scripts.signals.generate_walkforward_signals_duckdb to verify payload keys,
field types, boolean preservation, atomic writing, failure recovery,
replacement failure handling, and mocked engine orchestration error propagation.
================================================================================
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scripts.signals.generate_walkforward_signals_duckdb import build_export_payload, write_export_payload

def test_production_build_export_payload():
    active_signals = [{
        "id": "sig_RELIANCE_2026-10-27",
        "symbol": "RELIANCE",
        "direction": "BUY",
        "timeframe": "DAILY",
        "horizon_days": np.int64(20),
        "entry_price": np.float64(2800.0),
        "target_price": np.float64(3024.0),
        "stop_price": np.float64(2660.0),
        "rsi_14": np.float64(62.5),
        "timestamp": "2026-10-27",
        "status": "ACTIVE",
        "conviction_score": np.float64(88.5)
    }]

    history_records = [{
        "id": "hist_RELIANCE_2026-01-01_h20",
        "symbol": "RELIANCE",
        "direction": "BUY",
        "horizon_days": np.int64(20),
        "entry_date": "2026-01-01",
        "entry_price": np.float64(2500.0),
        "target_price": np.float64(2700.0),
        "stop_price": np.float64(2375.0),
        "exit_date": "2026-01-15",
        "exit_price": np.float64(2700.0),
        "status": "TARGET_HIT",
        "pnl_pct": np.float64(8.0),
        "conviction_score": np.float64(85.0),
        "is_full_horizon": True
    }, {
        "id": "hist_TCS_2026-10-20_h60",
        "symbol": "TCS",
        "direction": "BUY",
        "horizon_days": np.int64(60),
        "entry_date": "2026-10-20",
        "entry_price": np.float64(3500.0),
        "target_price": np.float64(3780.0),
        "stop_price": np.float64(3325.0),
        "exit_date": "2026-10-27",
        "exit_price": np.float64(3550.0),
        "status": "INCOMPLETE_WINDOW",
        "pnl_pct": np.float64(1.43),
        "conviction_score": np.float64(80.0),
        "is_full_horizon": False
    }]

    payload = build_export_payload(
        active_buy_signals=active_signals,
        all_history_signals=history_records,
        total_candidates=2
    )

    # Verify top-level payload keys
    assert "active_signals" in payload
    assert "history_records" in payload
    assert "summary" in payload
    assert "generated_at" in payload
    assert "source" in payload

    # Verify active_signals schema
    active = payload["active_signals"][0]
    required_active_keys = ["id", "symbol", "direction", "timeframe", "horizon_days", "entry_price", "target_price", "stop_price", "rsi_14", "timestamp", "status", "conviction_score"]
    for req_k in required_active_keys:
        assert req_k in active, f"Missing required active signal key '{req_k}'"

    # Verify history_records schema
    hist = payload["history_records"][0]
    required_hist_keys = ["id", "symbol", "direction", "horizon_days", "entry_date", "entry_price", "target_price", "stop_price", "exit_date", "exit_price", "status", "pnl_pct", "conviction_score", "is_full_horizon"]
    for req_k in required_hist_keys:
        assert req_k in hist, f"Missing required history record key '{req_k}'"

    # Verify JSON serializability with allow_nan=False
    json_str = json.dumps(payload, allow_nan=False)
    assert len(json_str) > 0
    assert "NaN" not in json_str
    assert "Infinity" not in json_str

    parsed = json.loads(json_str)
    assert parsed["summary"]["total_candidates"] == 2
    assert parsed["summary"]["total_evaluations"] == 2
    assert parsed["summary"]["active_buy_count"] == 1

def test_boolean_type_preservation_and_allow_nan_false():
    history_records = [{
        "id": "hist_TEST_01",
        "symbol": "TEST",
        "is_full_horizon": True, # Python bool
        "is_partial": np.bool_(False), # NumPy bool
        "nan_metric": np.nan, # NumPy NaN
        "inf_metric": np.inf, # NumPy Inf
        "neg_inf_metric": -np.inf, # NumPy -Inf
        "valid_float": np.float64(12.34),
        "valid_int": np.int64(100)
    }]

    payload = build_export_payload(
        active_buy_signals=[],
        all_history_signals=history_records,
        total_candidates=1
    )

    # Must succeed with allow_nan=False
    json_str = json.dumps(payload, allow_nan=False)

    parsed = json.loads(json_str)
    hist = parsed["history_records"][0]

    # Verify Booleans are preserved as JSON true/false (not converted to 1/0)
    assert hist["is_full_horizon"] is True
    assert hist["is_partial"] is False
    assert type(hist["is_full_horizon"]) is bool
    assert type(hist["is_partial"]) is bool

    # Verify NaNs and Infinities become JSON null
    assert hist["nan_metric"] is None
    assert hist["inf_metric"] is None
    assert hist["neg_inf_metric"] is None

    # Verify numbers retain exact types and values
    assert hist["valid_float"] == 12.34
    assert hist["valid_int"] == 100

def test_write_export_payload_atomic_temporary_file(tmp_path):
    target_out = tmp_path / "test_signals_export.json"

    history_records = [{
        "id": "hist_TEST_01",
        "symbol": "TEST",
        "is_full_horizon": True,
        "pnl_pct": 5.5
    }]

    payload = build_export_payload(
        active_buy_signals=[],
        all_history_signals=history_records,
        total_candidates=1
    )

    written_path = write_export_payload(payload, output_path=target_out)
    assert written_path.exists()

    loaded = json.loads(written_path.read_text(encoding="utf-8"))
    assert loaded["summary"]["total_candidates"] == 1
    assert loaded["history_records"][0]["is_full_horizon"] is True

def test_write_export_payload_failure_preserves_destination(tmp_path):
    target_out = tmp_path / "test_existing_destination.json"
    initial_bytes = b'{"status": "INITIAL_KNOWN_CONTENT"}'
    target_out.write_bytes(initial_bytes)

    # Inject a non-serializable payload object to cause json.dumps(..., allow_nan=False) to fail
    class NonSerializableObject:
        pass

    invalid_payload = {
        "invalid_field": NonSerializableObject()
    }

    with pytest.raises(RuntimeError, match="Failed atomic write for export payload"):
        write_export_payload(invalid_payload, output_path=target_out)

    # Destination file MUST remain byte-for-byte unchanged!
    assert target_out.read_bytes() == initial_bytes

def test_write_export_payload_replace_failure_preserves_destination_and_cleans_temp(tmp_path, monkeypatch):
    target_out = tmp_path / "test_replace_failure_destination.json"
    initial_bytes = b'{"status": "ORIGINAL_UNMUTATED_BYTES"}'
    target_out.write_bytes(initial_bytes)

    payload = {
        "active_signals": [],
        "history_records": [],
        "summary": {"total_candidates": 0, "total_evaluations": 0, "active_buy_count": 0}
    }

    # Mock os.replace to raise OSError during file replacement
    def mock_replace(src, dst):
        raise OSError("Simulated atomic replacement disk failure")

    monkeypatch.setattr("os.replace", mock_replace)

    with pytest.raises(RuntimeError, match="Failed atomic write for export payload"):
        write_export_payload(payload, output_path=target_out)

    # Destination file MUST remain byte-for-byte identical to original
    assert target_out.read_bytes() == initial_bytes

    # Temporary json files in destination directory MUST be cleaned up
    temp_json_files = list(tmp_path.glob("*.json"))
    assert len(temp_json_files) == 1
    assert temp_json_files[0].name == "test_replace_failure_destination.json"

def test_run_duckdb_signal_engine_orchestration_mocked(tmp_path, monkeypatch):
    import duckdb
    from scripts.signals import generate_walkforward_signals_duckdb

    dummy_db = tmp_path / "dummy.duckdb"
    dummy_db.touch()

    # Create an in-memory DuckDB connection fixture
    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE
        )
    """)

    # Populate 35 bars for symbol 'MOCK' to pass minimum history
    dates = pd.date_range("2026-01-01", periods=35, freq="D")
    for d in dates:
        con.execute("INSERT INTO daily_ohlcv VALUES (?, ?, 100.0, 105.0, 95.0, 102.0, 5000.0)", ["MOCK", d.strftime("%Y-%m-%d")])

    monkeypatch.setattr(generate_walkforward_signals_duckdb, "duckdb_path", dummy_db)

    # Mock duckdb.connect to return in-memory con
    def mock_connect(*args, **kwargs):
        return con

    monkeypatch.setattr("duckdb.connect", mock_connect)

    # Mock write_export_payload to capture call without writing live files
    written_calls = []
    def mock_write(payload, output_path=None):
        written_calls.append((payload, output_path))
        return tmp_path / "mock_out.json"

    monkeypatch.setattr(generate_walkforward_signals_duckdb, "write_export_payload", mock_write)

    # Execute engine orchestration on mock in-memory connection
    generate_walkforward_signals_duckdb.run_duckdb_signal_engine()

    assert len(written_calls) == 1
    captured_payload, _ = written_calls[0]
    assert "active_signals" in captured_payload
    assert "history_records" in captured_payload
    assert "summary" in captured_payload

def test_run_duckdb_signal_engine_writer_failure_propagates(tmp_path, monkeypatch):
    import duckdb
    from scripts.signals import generate_walkforward_signals_duckdb

    dummy_db = tmp_path / "dummy_fail.duckdb"
    dummy_db.touch()

    con = duckdb.connect(":memory:")
    con.execute("""
        CREATE TABLE daily_ohlcv (
            symbol VARCHAR, date VARCHAR, open DOUBLE, high DOUBLE, low DOUBLE, close DOUBLE, volume DOUBLE
        )
    """)

    dates = pd.date_range("2026-01-01", periods=35, freq="D")
    for d in dates:
        con.execute("INSERT INTO daily_ohlcv VALUES (?, ?, 100.0, 105.0, 95.0, 102.0, 5000.0)", ["MOCK", d.strftime("%Y-%m-%d")])

    monkeypatch.setattr(generate_walkforward_signals_duckdb, "duckdb_path", dummy_db)

    def mock_connect(*args, **kwargs):
        return con

    monkeypatch.setattr("duckdb.connect", mock_connect)

    calls = []
    def mock_failing_write(payload, output_path=None):
        calls.append(payload)
        raise RuntimeError("Simulated export writer failure in orchestration test")

    monkeypatch.setattr(generate_walkforward_signals_duckdb, "write_export_payload", mock_failing_write)

    try:
        with pytest.raises(RuntimeError, match="Simulated export writer failure in orchestration test"):
            generate_walkforward_signals_duckdb.run_duckdb_signal_engine()

        assert len(calls) == 1
    finally:
        con.close()
