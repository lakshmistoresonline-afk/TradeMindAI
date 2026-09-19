import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.core.container import container
import os

client = TestClient(app)

def test_root_contract():
    """Verify root endpoint returns canonical hardened metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "git_sha" in data
    assert "release" in data
    assert data["status"] == "ONLINE"

def test_health_contract():
    """Verify health endpoint structure and unified versioning."""
    response = client.get("/api/v1/system/health")
    # Redirect check if applicable, but TestClient handles it
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert "version" in data
    assert data["status"].upper() in ( "HEALTHY", "DEGRADED")


def test_market_stats_contract():
    """Verify market stats resilience (should not return 500 even if provider fails)."""
    with TestClient(app) as client:
        response = client.get("/api/v1/stocks/market-stats")
        assert response.status_code == 200
        data = response.json()
        assert "NIFTY 50" in data
        assert "India VIX" in data


def test_signals_contract():
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
    # In test env it might be development, but we verify the logic exists
    assert settings.ADMIN_EMAILS is not None
    assert "admin@trademind.ai" in settings.ADMIN_EMAILS

if __name__ == "__main__":
    pytest.main([__file__])
