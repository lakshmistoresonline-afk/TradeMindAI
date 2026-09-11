import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.main import app

def test_equity_endpoints():
    client = TestClient(app)

    print("Testing GET /api/v1/equity/signals...")
    res = client.get("/api/v1/equity/signals")
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        signals = res.json()
        print(f"Signals found: {len(signals)}")
        if signals:
            print(f"First signal ID: {signals[0]['id']}")
    else:
        print(f"Error: {res.text}")

    print("\nTesting GET /api/v1/equity/scanner...")
    res = client.get("/api/v1/equity/scanner")
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"Scanner items: {len(res.json())}")

    print("\nTesting GET /api/v1/equity/performance...")
    res = client.get("/api/v1/equity/performance")
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"Performance: {res.json()}")

    print("\nTesting GET /api/v1/equity/market...")
    res = client.get("/api/v1/equity/market")
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print(f"Market: {res.json()}")

    print("\nTesting GET /api/v1/system/health...")
    # Wait, the prompt says /api/v1/system/health
    # Let me check where it is registered.
    # In api.py: api_router.include_router(equity.router, prefix="/equity", tags=["equity"])
    # Wait, SystemStatus.tsx uses getDataHealth() -> /admin/health?
    # client.ts says: export const getDataHealth = async () => { const response = await apiClient.get('/admin/health'); return response.data; };
    # Prompt says: /api/v1/system/health
    res = client.get("/api/v1/system/health")
    print(f"Status: {res.status_code} (for /api/v1/system/health)")

    # Check /admin/health too
    res = client.get("/api/v1/admin/health")
    print(f"Status: {res.status_code} (for /api/v1/admin/health)")

if __name__ == "__main__":
    test_equity_endpoints()
