import unittest
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.strategy_engine import StrategyEngine
from backend.domain.models.stock import StockPrice
from backend.domain.models.data_platform import FeatureVector

class TestBacktestLogic(unittest.TestCase):
    def setUp(self):
        self.engine = StrategyEngine()

    def test_backtest_simple_strategy(self):
        symbol = "RELIANCE"
        # Create some dummy prices
        prices = [
            StockPrice(symbol=symbol, date=datetime(2024,1,i), open=100, high=110, low=90, close=100+i, volume=1000)
            for i in range(1, 11)
        ]

        # Create some features
        history = [
            FeatureVector(symbol=symbol, date=datetime(2024,1,i), version="1", features={"rsi": 20+i*5})
            for i in range(1, 11)
        ]

        # Strategy: BUY if rsi < 30, EXIT if rsi > 40
        rules = [{"feature": "rsi", "op": "lt", "val": 30}]

        result = self.engine.backtest_strategy(symbol, history, rules, prices)

        print(f"Backtest Result: {result}")
        self.assertIn("final_equity", result)
        self.assertIn("trade_log", result)

if __name__ == "__main__":
    unittest.main()
