import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from unittest.mock import MagicMock
from backend.core.database import get_db

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def client(mock_db):
    # Override get_db to return our mock
    app.dependency_overrides[get_db] = lambda: mock_db
    return TestClient(app)

@pytest.fixture
def mock_stock_service():
    return MagicMock()
