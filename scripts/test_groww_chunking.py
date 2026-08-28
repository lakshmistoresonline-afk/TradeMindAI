import unittest
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.infrastructure.repositories.groww_provider import GrowwProvider

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    def json(self):
        return self.json_data

class TestGrowwChunking(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.provider = GrowwProvider()
        # Mock the client to avoid real API calls
        from unittest.mock import AsyncMock
        self.provider.client = AsyncMock()

    async def test_chunking_1m_90days(self):
        # 5m interval, 90 days range -> should result in 3 chunks (30 days each)
        start_date = datetime(2024, 1, 1)
        end_date = start_date + timedelta(days=90)
        interval = "5m"

        self.provider.client.get.return_value = MockResponse({"candles": []})

        await self.provider.get_historical_candles("RELIANCE", start_date, end_date, interval)

        # Verify the number of calls
        self.assertEqual(self.provider.client.get.call_count, 3)

        # Verify call arguments (start/end times)
        calls = self.provider.client.get.call_args_list

        # First chunk
        first_start = calls[0].kwargs['params']['startTime']
        first_end = calls[0].kwargs['params']['endTime']
        self.assertEqual(first_start, int(start_date.timestamp() * 1000))
        self.assertEqual(first_end, int((start_date + timedelta(days=30)).timestamp() * 1000))

    async def test_chunking_1d_400days(self):
        # 1D interval, 400 days range -> should result in 3 chunks (180, 180, 40 days)
        start_date = datetime(2023, 1, 1)
        end_date = start_date + timedelta(days=400)
        interval = "1D"

        self.provider.client.get.return_value = MockResponse({"candles": []})

        await self.provider.get_historical_candles("RELIANCE", start_date, end_date, interval)

        self.assertEqual(self.provider.client.get.call_count, 3)

if __name__ == "__main__":
    unittest.main()
