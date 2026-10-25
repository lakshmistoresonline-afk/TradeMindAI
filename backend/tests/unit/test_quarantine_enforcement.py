"""
================================================================================
TradeMindAI: Unit Test Suite for Central Quarantine Enforcement
================================================================================
Verifies that settings.QUARANTINE_ACTIVE defaults to True and that all signal/equity API
endpoints fail closed with 503 Service Unavailable when quarantine is active.
================================================================================
"""

import pytest
from fastapi.testclient import TestClient
from backend.core.config import settings, Settings
from backend.app.main import app
from scripts.audit.generate_route_inventory_json import classify_route

client = TestClient(app)

def test_quarantine_setting_defaults_to_true():
    """Verify that settings.QUARANTINE_ACTIVE defaults to True for fail-closed security."""
    assert getattr(settings, "QUARANTINE_ACTIVE", True) is True

@pytest.mark.parametrize("false_val", [False, "false", "0", "no", "off", "disable", "disabled"])
def test_quarantine_cannot_be_disabled_via_override(false_val):
    """Verify that attempting to set QUARANTINE_ACTIVE=False or false-like strings raises a ValueError security audit exception."""
    with pytest.raises(ValueError, match="CRITICAL SECURITY AUDIT FAILURE: QUARANTINE_ACTIVE is permanently active"):
        Settings(QUARANTINE_ACTIVE=false_val)

@pytest.mark.parametrize("env_val", ["false", "0", "no", "off", "disable", "disabled"])
def test_quarantine_override_via_monkeypatch_env_refused(monkeypatch, env_val):
    """Verify that setting QUARANTINE_ACTIVE environment variable to false-like strings raises a ValueError on Settings initialization."""
    monkeypatch.setenv("QUARANTINE_ACTIVE", env_val)
    with pytest.raises(ValueError, match="CRITICAL SECURITY AUDIT FAILURE: QUARANTINE_ACTIVE is permanently active"):
        Settings()

def test_adversarial_cache_transition_denied_when_quarantined():
    """
    Adversarial Cache Transition Test:
    1. Verifies that request to cached endpoint GET /api/v1/equity/market evaluates the quarantine guard before cache retrieval.
    2. Asserts HTTP 503 QUARANTINED is returned cleanly, denying cached payload disclosure.
    3. Verifies that sequential requests consistently fail closed without cache hit bypass.
    """
    for idx in range(3):
        res = client.get("/api/v1/equity/market")
        assert res.status_code == 503, f"Iteration {idx}: Expected HTTP 503, got {res.status_code}"
        data = res.json()
        assert "QUARANTINED" in data.get("detail", ""), f"Iteration {idx}: Expected QUARANTINED detail, got {data}"

def test_route_inventory_completeness_and_classification_coverage():
    """Route Completeness Regression Test: Asserts 100% of registered OpenAPI paths are classified with zero UNRESOLVED routes."""
    schema = app.openapi()
    paths = schema.get("paths", {})

    unresolved_paths = []
    for p in paths.keys():
        classification, guard, status = classify_route(p)
        if classification == "UNRESOLVED_REQUIRES_REVIEW":
            unresolved_paths.append(p)

    assert len(unresolved_paths) == 0, f"Found {len(unresolved_paths)} unclassified routes in app schema: {unresolved_paths}"

def test_all_registered_openapi_signal_routes_fail_closed():
    """Programmatically inspects all OpenAPI routes in app and asserts every signal/equity route fails closed with HTTP 503 while quarantined."""
    schema = app.openapi()
    paths = schema.get("paths", {})
    signal_paths = []

    for p in paths.keys():
        p_lower = p.lower()
        if any(k in p_lower for k in ["signal", "equity/accuracy", "equity/performance", "equity/features", "equity/market", "indicators", "opportunities"]):
            if "status" not in p_lower:
                signal_paths.append(p)

    assert len(signal_paths) >= 11, f"Expected at least 11 registered signal/equity routes, found {len(signal_paths)}"

    for path in signal_paths:
        test_path = path.replace("{symbol}", "RELIANCE").replace("{signal_id}", "sig_test_1").replace("{universe_id}", "NIFTY_50")
        response = client.get(test_path)
        assert response.status_code == 503, f"Expected 503 for path {test_path}, got {response.status_code}"
        data = response.json()
        assert "QUARANTINED" in data.get("detail", ""), f"Expected QUARANTINED in detail for {test_path}, got {data}"

def test_cache_hit_cannot_bypass_quarantine_guard():
    """Adversarial Cache Test: Verifies that multiple sequential requests to cached endpoints (e.g. /equity/market) fail closed on every attempt."""
    for _ in range(5):
        response = client.get("/api/v1/equity/market")
        assert response.status_code == 503
        data = response.json()
        assert "QUARANTINED" in data.get("detail", "")

def test_signals_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/signals/{symbol} returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/signals/RELIANCE")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_signals_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/equity/signals returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/equity/signals")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_signal_detail_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/equity/signals/{id} returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/equity/signals/sig_test_1")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_accuracy_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/equity/accuracy returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/equity/accuracy")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_performance_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/equity/performance returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/equity/performance")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_history_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/equity/history returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/equity/history")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_forensics_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/equity/signals/sig_test_1/forensics returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/equity/signals/sig_test_1/forensics")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_market_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/equity/market returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/equity/market")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_indicators_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/indicators/{symbol} returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/indicators/RELIANCE")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_ios_opportunities_endpoint_fails_closed_when_quarantined():
    """Verify that GET /api/v1/ios/opportunities returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/ios/opportunities")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_equity_v1_status_endpoint_returns_quarantined_status():
    """Verify that GET /api/v1/equity/status returns status=QUARANTINED and quarantine_active=true."""
    response = client.get("/api/v1/equity/status")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "QUARANTINED"
    assert data.get("quarantine_active") is True

def test_ios_live_signals_fails_closed_when_quarantined():
    """Verify that GET /api/v1/ios/signals/live returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/ios/signals/live")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_stream_signals_fails_closed_when_quarantined():
    """Verify that GET /api/v1/stream/signals returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/stream/signals")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_universe_signals_fails_closed_when_quarantined():
    """Verify that GET /api/v1/universes/{universe_id}/signals returns 503 Service Unavailable when quarantined."""
    response = client.get("/api/v1/universes/NIFTY_50/signals")
    assert response.status_code == 503
    data = response.json()
    assert "QUARANTINED" in data.get("detail", "")

def test_signal_only_product_boundaries_permanently_false():
    """Verify that real trading flags remain strictly False."""
    assert settings.REAL_TRADING is False
    assert settings.LIVE_EXECUTION_ENABLED is False
    assert settings.BROKER_ORDER_EXECUTION_ENABLED is False
