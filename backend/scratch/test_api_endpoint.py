import asyncio
import httpx
from httpx import ASGITransport
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

# Mock environment
os.environ["ENVIRONMENT"] = "development"

from backend.app.main import app

async def test():
    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/equity/accuracy")
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")

if __name__ == "__main__":
    asyncio.run(test())
