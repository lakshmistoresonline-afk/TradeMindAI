import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.api.v1.endpoints.equity import is_eligible_buy

client = TestClient(app)

class MockColumn:
    def __init__(self, name):
        self.name = name

class MockSignalDB:
    def __init__(self, status, signal_type="SWING", direction="LONG", rating="BUY", signal_rating=None, net_pnl=5.0, calibrated_probability=0.8, raw_probability=None, created_at=None, symbol="RELIANCE"):
        self.status = status
        self.signal_type = signal_type
        self.direction = direction
        self.rating = rating
        self.signal_rating = signal_rating
        self.net_pnl = net_pnl
        self.calibrated_probability = calibrated_probability
        self.raw_probability = raw_probability if raw_probability is not None else calibrated_probability
        self.created_at = created_at
        self.symbol = symbol
        self.__table__ = type("Table", (), {
            "columns": [
                MockColumn("status"),
                MockColumn("signal_type"),
                MockColumn("direction"),
                MockColumn("rating"),
                MockColumn("signal_rating"),
                MockColumn("net_pnl"),
                MockColumn("calibrated_probability"),
                MockColumn("raw_probability"),
                MockColumn("created_at"),
                MockColumn("symbol")
            ]
        })()

# 1. Empty ledger
def test_scenario_1_empty_ledger(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return []
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    perf = client.get("/api/v1/equity/performance").json()
    assert perf["sample_size"] == 0
    assert perf["status"] == "INSUFFICIENT_EVIDENCE"
    assert perf["net_pnl"] is None

    acc = client.get("/api/v1/equity/accuracy").json()
    assert acc["verified_benchmark"]["status"] == "INSUFFICIENT_EVIDENCE"
    for h in ["SHORT", "SWING", "LONG"]:
        assert acc["horizons"][h]["status"] == "INSUFFICIENT_EVIDENCE"

# 2. Expired-only ledger
def test_scenario_2_expired_only(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("EXPIRED", net_pnl=0.0),
            MockSignalDB("EXPIRED", net_pnl=1.0)
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    perf = client.get("/api/v1/equity/performance").json()
    assert perf["sample_size"] == 2
    assert perf["eligible_directional_outcomes"] == 0
    assert perf["status"] == "INSUFFICIENT_EVIDENCE"
    assert perf["net_pnl"] is None

# 3. Valid target-hit and stop-loss outcomes
def test_scenario_3_valid_target_hit_stop_loss(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("TARGET_HIT", signal_type="SWING", net_pnl=10.0, calibrated_probability=0.8),
            MockSignalDB("STOP_LOSS", signal_type="SWING", net_pnl=-4.0, calibrated_probability=0.2)
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    perf = client.get("/api/v1/equity/performance").json()
    assert perf["sample_size"] == 2
    assert perf["eligible_directional_outcomes"] == 2
    assert perf["wins"] == 1
    assert perf["losses"] == 1
    assert perf["win_rate"] == 50.0
    assert perf["net_pnl"] == 6.0
    assert perf["profit_factor"] == 2.5
    assert perf["financial_status"] == "VERIFIED"
    assert perf["status"] == "VERIFIED"

# 4. Missing P&L
def test_scenario_4_missing_pnl(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("TARGET_HIT", signal_type="SWING", net_pnl=10.0, calibrated_probability=0.8),
            MockSignalDB("STOP_LOSS", signal_type="SWING", net_pnl=float('nan'), calibrated_probability=0.2)
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    perf = client.get("/api/v1/equity/performance").json()
    assert perf["eligible_directional_outcomes"] == 2
    assert perf["wins"] == 1
    assert perf["losses"] == 1
    assert perf["outcome_status"] == "VERIFIED"
    assert perf["financial_status"] == "INCOMPLETE_DATA"
    assert perf["net_pnl"] is None
    assert perf["expectancy"] is None
    assert perf["profit_factor"] is None
    assert perf["status"] == "PARTIALLY_VERIFIED"

# 5. Both outcome classes present for AUC
def test_scenario_5_both_classes_present_auc(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("TARGET_HIT", signal_type="SWING", calibrated_probability=0.9),
            MockSignalDB("STOP_LOSS", signal_type="SWING", calibrated_probability=0.1)
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    acc = client.get("/api/v1/equity/accuracy").json()
    swing = acc["horizons"]["SWING"]
    assert swing["eligible_directional_outcomes"] == 2
    assert swing["auc"] == 1.0
    assert swing["status"] == "VERIFIED"

# 6. Single outcome class for AUC
def test_scenario_6_single_class_auc(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("TARGET_HIT", signal_type="SWING", calibrated_probability=0.8),
            MockSignalDB("TARGET_HIT", signal_type="SWING", calibrated_probability=0.9)
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    acc = client.get("/api/v1/equity/accuracy").json()
    swing = acc["horizons"]["SWING"]
    assert swing["eligible_directional_outcomes"] == 2
    assert swing["auc"] is None
    assert swing["status"] == "PARTIALLY_VERIFIED"

# 7. Mixed valid and invalid prediction probabilities
def test_scenario_7_mixed_probabilities(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("TARGET_HIT", signal_type="SWING", calibrated_probability=0.8),
            MockSignalDB("STOP_LOSS", signal_type="SWING", calibrated_probability=1.5) # Invalid > 1.0
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    acc = client.get("/api/v1/equity/accuracy").json()
    swing = acc["horizons"]["SWING"]
    assert swing["eligible_directional_outcomes"] == 2
    assert swing["valid_prediction_pairs"] == 1
    assert swing["prediction_coverage"] == 0.5
    assert swing["status"] == "PARTIALLY_VERIFIED"

# 8. Zero valid prediction pairs
def test_scenario_8_zero_valid_prediction_pairs(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("TARGET_HIT", signal_type="SWING", calibrated_probability=float('nan'), raw_probability=float('nan')),
            MockSignalDB("STOP_LOSS", signal_type="SWING", calibrated_probability=None, raw_probability=None)
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    acc = client.get("/api/v1/equity/accuracy").json()
    swing = acc["horizons"]["SWING"]
    assert swing["eligible_directional_outcomes"] == 2
    assert swing["valid_prediction_pairs"] == 0
    assert swing["status"] == "INSUFFICIENT_EVIDENCE"

# 9. Partial prediction coverage
def test_scenario_9_partial_prediction_coverage(monkeypatch):
    class MockQuery:
        def filter(self, *args, **kwargs): return self
        def all(self): return [
            MockSignalDB("TARGET_HIT", signal_type="SWING", calibrated_probability=0.8),
            MockSignalDB("STOP_LOSS", signal_type="SWING", calibrated_probability=0.2),
            MockSignalDB("STOP_LOSS", signal_type="SWING", calibrated_probability=None, raw_probability=None)
        ]
    class MockSession:
        def query(self, model): return MockQuery()
        def __enter__(self): return self
        def __exit__(self, *args): pass

    monkeypatch.setattr("backend.core.postgres.SessionLocal", lambda: MockSession())

    acc = client.get("/api/v1/equity/accuracy").json()
    swing = acc["horizons"]["SWING"]
    assert swing["eligible_directional_outcomes"] == 3
    assert swing["valid_prediction_pairs"] == 2
    assert swing["prediction_coverage"] == 0.6667
    assert swing["status"] == "PARTIALLY_VERIFIED"

# 10. BUY-only eligibility filtering
def test_scenario_10_buy_eligibility_filtering():
    assert is_eligible_buy(MockSignalDB("TARGET_HIT", direction="LONG", rating="BUY")) is True
    assert is_eligible_buy(MockSignalDB("TARGET_HIT", direction="LONG", rating="STRONG_BUY")) is True
    assert is_eligible_buy(MockSignalDB("TARGET_HIT", direction="SHORT", rating="BUY")) is False
    assert is_eligible_buy(MockSignalDB("TARGET_HIT", direction="LONG", rating="SELL")) is False
    assert is_eligible_buy(MockSignalDB("TARGET_HIT", direction="LONG", rating="BUY", signal_rating="SELL")) is False
    assert is_eligible_buy(MockSignalDB("TARGET_HIT", direction=None, rating="BUY")) is False
    assert is_eligible_buy(MockSignalDB("TARGET_HIT", direction="LONG", rating=None)) is False
