import pytest
import os
import json
import tempfile
import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.core.postgres import Base, ShadowSignalDB
from backend.services.research_metrics_service import ResearchMetricsService
from scripts.export_history_json import export_history
from scripts.export_performance_json import export_performance

client = TestClient(app)

def test_research_metrics_insufficient_data():
    metrics = ResearchMetricsService.calculate_performance_metrics([])
    assert metrics["sample_size"] == 0
    assert metrics["win_rate"] is None
    assert metrics["profit_factor"] is None
    assert metrics["net_pnl"] is None
    assert metrics["status"] == "INSUFFICIENT_EVIDENCE"

    unresolved = [
        {"id": "sig_1", "symbol": "RELIANCE", "status": "ACTIVE", "rating": "BUY", "direction": "LONG", "net_pnl": 0.0}
    ]
    metrics_unresolved = ResearchMetricsService.calculate_performance_metrics(unresolved)
    assert metrics_unresolved["eligible_directional_outcomes"] == 0
    assert metrics_unresolved["win_rate"] is None
    assert metrics_unresolved["status"] == "INSUFFICIENT_EVIDENCE"

def test_universes_api_integration():
    response = client.get("/api/v1/universes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    for tier in data:
        assert tier["status"] == "UNVERIFIED"
        assert tier["count"] >= 0

    res_const = client.get("/api/v1/universes/NIFTY_50/constituents")
    assert res_const.status_code == 200
    const_data = res_const.json()
    assert const_data["universe_id"] == "NIFTY_50"
    assert "constituents" in const_data

def test_exporters_provenance_and_determinism():
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    now = datetime.datetime.now(datetime.timezone.utc)
    session = TestSessionLocal()

    sig_win = ShadowSignalDB(
        id="test_win_1",
        symbol="RELIANCE",
        direction="LONG",
        rating="BUY",
        asset_class="EQUITY",
        status="TARGET_HIT",
        signal_eligibility=True,
        entry_price=1000.0,
        target_price=1050.0,
        stop_price=950.0,
        net_pnl=5.0,
        created_at=now,
        timestamp=now
    )
    sig_loss = ShadowSignalDB(
        id="test_loss_1",
        symbol="TCS",
        direction="LONG",
        rating="BUY",
        asset_class="EQUITY",
        status="STOP_LOSS",
        signal_eligibility=True,
        entry_price=3000.0,
        target_price=3150.0,
        stop_price=2900.0,
        net_pnl=-3.0,
        created_at=now,
        timestamp=now
    )
    sig_active = ShadowSignalDB(
        id="test_active_1",
        symbol="INFY",
        direction="LONG",
        rating="BUY",
        asset_class="EQUITY",
        status="ACTIVE",
        signal_eligibility=True,
        entry_price=1500.0,
        net_pnl=0.0,
        created_at=now,
        timestamp=now
    )

    session.add_all([sig_win, sig_loss, sig_active])
    session.commit()
    session.close()

    with tempfile.TemporaryDirectory() as tmpdir:
        hist_out = os.path.join(tmpdir, "signals_history.json")
        perf_out = os.path.join(tmpdir, "performance.json")

        from unittest.mock import patch
        with patch('scripts.export_history_json.SessionLocal', TestSessionLocal), \
             patch('scripts.export_history_json.os.path.abspath', return_value=hist_out), \
             patch('scripts.export_performance_json.os.path.abspath', side_effect=lambda p: hist_out if 'signals_history' in p else perf_out):

            export_history()
            assert os.path.exists(hist_out)

            with open(hist_out, 'r') as f:
                hist_data = json.load(f)

            assert "records" in hist_data
            assert hist_data["total"] == 3

            record_ids = [r["id"] for r in hist_data["records"]]
            assert "test_win_1" in record_ids
            assert "test_loss_1" in record_ids
            assert "test_active_1" in record_ids

            win_rec = next(r for r in hist_data["records"] if r["id"] == "test_win_1")
            assert win_rec["symbol"] == "RELIANCE"
            assert win_rec["entry_price"] == 1000.0
            assert win_rec["net_pnl"] == 5.0
            assert win_rec["status"] == "TARGET_HIT"

            export_performance()
            assert os.path.exists(perf_out)

            with open(perf_out, 'r') as f:
                perf_data = json.load(f)

            assert "verified_benchmark" in perf_data
            bench = perf_data["verified_benchmark"]
            assert bench["n"] == 3
            assert bench["eligible_directional_outcomes"] == 2
            assert bench["win_rate"] == 50.0
            assert bench["net_pnl"] == 2.0

            with open(hist_out, 'r') as f1, open(perf_out, 'r') as f2:
                h1 = json.load(f1)
                p1 = json.load(f2)

            export_history()
            export_performance()

            with open(hist_out, 'r') as f1, open(perf_out, 'r') as f2:
                h2 = json.load(f1)
                p2 = json.load(f2)

            assert h1["total"] == h2["total"]
            assert len(h1["records"]) == len(h2["records"])
            assert p1["verified_benchmark"] == p2["verified_benchmark"]

    test_engine.dispose()

def test_exporters_database_failure_handling():
    with tempfile.TemporaryDirectory() as tmpdir:
        hist_out = os.path.join(tmpdir, "signals_history.json")

        def mock_session_fail():
            raise RuntimeError("Database connection refused")

        from unittest.mock import patch
        with patch('scripts.export_history_json.SessionLocal', mock_session_fail), \
             patch('scripts.export_history_json.os.path.abspath', return_value=hist_out):

            with pytest.raises(RuntimeError, match="Database history export failed"):
                export_history()

            assert not os.path.exists(hist_out)
