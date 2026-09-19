import sys
import os
import asyncio
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.health_service import SystemHealthService

async def test_failures():
    print("CLAIM: Health system accurately reports degraded states")
    print("-" * 60)

    # 1. Test Redis Down
    with patch("redis.asyncio.from_url") as mock_redis:
        mock_redis.side_effect = Exception("Redis Connection Refused")
        health = await SystemHealthService.get_comprehensive_health()
        print(f"Redis DOWN => Health Status: {health['status']} | Component: {health['components']['Redis_Cache']}")

    # 2. Test DB Down
    with patch("sqlalchemy.engine.base.Engine.connect") as mock_db:
        mock_db.side_effect = Exception("DB Connection Refused")
        health = await SystemHealthService.get_comprehensive_health()
        print(f"Database DOWN => Health Status: {health['status']} | Component: {health['components']['SQL_Database']}")

    # 3. Verify Overall logic
    # Critical components failure => FAILED
    if health['status'] == "FAILED":
        print("RESULT: PASS")
    else:
        print(f"RESULT: FAIL (Expected FAILED, got {health['status']})")

if __name__ == "__main__":
    asyncio.run(test_failures())
