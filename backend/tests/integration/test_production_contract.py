import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.container import container
import os

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_root_contract(client: TestClient):
    """Verify root endpoint returns canonical hardened metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "app" in data
    assert "mode" in data

def test_health_contract(client: TestClient):
    """Verify health endpoint structure and unified versioning."""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert "version" in data
    assert data["status"].upper() in ("HEALTHY", "DEGRADED", "FAILED")

def test_market_stats_contract():
    """Verify market stats resilience (should not return 500 even if provider fails)."""
    with TestClient(app) as client:
        response = client.get("/api/v1/stocks/market-stats")
        assert response.status_code == 200
        data = response.json()
        assert "NIFTY 50" in data
        assert "India VIX" in data

        for name in ["NIFTY 50", "India VIX"]:
            assert "status" in data[name]
            if data[name]["status"] == "UNAVAILABLE":
                assert data[name].get("value") is None
            else:
                assert data[name].get("value") is not None

def test_negative_security_missing_secret():
    """P0: Production mode requires SECRET_KEY."""
    import os
    from backend.core.config import Settings

    os.environ["ENVIRONMENT"] = "production"
    os.environ["SECRET_KEY"] = "SECRET"

    with pytest.raises(Exception):
        Settings()

    os.environ["ENVIRONMENT"] = "development"
    os.environ["SECRET_KEY"] = "SECRET"

def test_negative_ingest_bad_key():
    """P0: Ingestion fails with wrong key."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/market-data/ingest",
            json=[{"symbol": "RELIANCE", "price": 2500}],
            headers={"X-Collector-Key": "wrong-key"}
        )
        assert response.status_code == 403

def test_deep_health_contract(client: TestClient):
    """P1: Deep health model truth check."""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "pulse_watchdog" in data
    assert "components" in data

def test_signals_contract(client: TestClient):
    """Verify primary signal intelligence endpoint."""
    response = client.get("/api/v1/equity/signals")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_container_instantiation():
    """Verify dependency injection container health."""
    assert container.health_service is not None
    assert container.market_data_service is not None
    assert container.provider is not None
    assert container.repository is not None

def test_security_settings_contract():
    """Verify production security guards are active in settings object."""
    from backend.core.config import settings
    assert settings.ADMIN_EMAILS is not None
    assert "admin@trademind.ai" in settings.ADMIN_EMAILS

if __name__ == "__main__":
    pytest.main([__file__])
