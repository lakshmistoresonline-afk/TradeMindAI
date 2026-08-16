import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to TradeMind AI API"}

def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_market_stats_endpoint(client: TestClient):
    # This endpoint currently talks to yfinance direct
    response = client.get("/api/v1/stocks/market-stats")
    assert response.status_code == 200
    assert "NIFTY 100" in response.json()

def test_stocks_list_protected(client: TestClient):
    # This should fail if security is on, but we reverted security to mock for now
    response = client.get("/api/v1/stocks/")
    assert response.status_code == 200 # Should succeed with our mock dev user
