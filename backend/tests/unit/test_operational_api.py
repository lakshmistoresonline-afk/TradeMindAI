import pytest
from fastapi.testclient import TestClient
from backend.app.operational_api import app, state

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_livez(client):
    response = client.get("/livez")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readyz_when_ready(client):
    state.ready = True
    state.shutting_down = False
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

def test_readyz_when_not_ready(client):
    state.ready = False
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}
    # Reset state for other tests
    state.ready = True
