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

        # Phase 3 Hardening: Truthful nulls check
        # (Assuming test env might not have credentials, so stats should be UNAVAILABLE)
        for name in ["NIFTY 50", "India VIX"]:
            assert "status" in data[name]
            if data[name]["status"] == "UNAVAILABLE":
                assert data[name]["value"] is None

def test_negative_security_missing_secret():
    """P0: Production mode requires SECRET_KEY."""
    import os
    from backend.core.config import Settings

    # Mock production environment
    os.environ["ENVIRONMENT"] = "production"
    os.environ["SECRET_KEY"] = "SECRET" # The forbidden default

    with pytest.raises(Exception):
        Settings()

    # Cleanup
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

def test_deep_health_contract():
    """P1: Deep health model truth check."""
    with TestClient(app) as client:
        response = client.get("/api/v1/system/health")
        assert response.status_code == 200
        data = response.json()
        assert "pulse_watchdog" in data
        assert "components" in data
        # Historical Data should be NOT_CHECKED if not actually implemented check
        assert data["components"]["Historical Data"] == "NOT_CHECKED"



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
