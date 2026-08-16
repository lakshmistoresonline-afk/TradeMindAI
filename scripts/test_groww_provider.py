import unittest
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.infrastructure.repositories.groww_provider import GrowwProvider

class TestGrowwProvider(unittest.TestCase):
    def setUp(self):
        self.provider = GrowwProvider()

    def test_symbol_mapping(self):
        self.assertEqual(self.provider._map_to_groww_symbol("RELIANCE"), "NSE-RELIANCE")
        self.assertEqual(self.provider._map_to_groww_symbol("NIFTY"), "NSE-NIFTY")
        self.assertEqual(self.provider._map_to_groww_symbol("^NSEI"), "NSE-NIFTY")

    def test_interval_limits(self):
        self.assertEqual(self.provider._get_interval_limit_days("1m"), 30)
        self.assertEqual(self.provider._get_interval_limit_days("15m"), 90)
        self.assertEqual(self.provider._get_interval_limit_days("1D"), 180)

if __name__ == "__main__":
    unittest.main()
