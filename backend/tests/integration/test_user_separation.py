import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_user_cannot_access_admin_stats():
    # Simulate normal user token (using bypass for testing if configured)
    headers = {"Authorization": "Bearer normal_user_token"}
    response = client.get("/api/v1/admin/stats", headers=headers)
    # Expected: 403 Forbidden because normal_user_token is not in ADMIN_EMAILS
    # Note: This assumes the test environment handles token verification or uses a mock
    assert response.status_code == 403

def test_admin_can_access_admin_stats():
    # Simulate admin user token
    headers = {"Authorization": "Bearer admin_user_token"}
    # Note: Requires mocking auth.verify_id_token to return an admin email
    pass

def test_public_metadata_accessible():
    response = client.get("/api/v1/public/seo/home")
    assert response.status_code == 200
    assert "TradeMind AI" in response.json()["title"]
