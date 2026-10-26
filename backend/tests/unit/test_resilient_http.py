import pytest
import httpx
from backend.infrastructure.resilient_http import ResilientHTTPClient, UpstreamUnavailable

def test_resilient_http_client_validation():
    with pytest.raises(ValueError):
        ResilientHTTPClient(base_url="https://api.example.com", timeout_seconds=0)
    with pytest.raises(ValueError):
        ResilientHTTPClient(base_url="https://api.example.com", max_attempts=0)

@pytest.mark.asyncio
async def test_resilient_http_client_init_and_close():
    client = ResilientHTTPClient(base_url="https://api.example.com", timeout_seconds=2.0, max_attempts=2)
    assert client.max_attempts == 2
    await client.close()
