from typing import List, Dict, Any, Optional
import pandas as pd
from backend.domain.models.stock import StockPrice
from backend.domain.models.data_platform import FeatureVector

class StrategyEngine:
    @staticmethod
    def evaluate_rules(strategy_rules: List[Dict[str, Any]], features: FeatureVector) -> bool:
        """
        Executes a set of logical rules against a feature vector.
        Example rule: {"feature": "momentum_rsi", "op": "lt", "val": 0.3}
        """
        for rule in strategy_rules:
            feat_name = rule["feature"]
            op = rule["op"]
            val = rule["val"]

            if feat_name not in features.features:
                return False

            current_val = features.features[feat_name]

            if op == "gt" and not (current_val > val): return False
            if op == "lt" and not (current_val < val): return False
            if op == "eq" and not (current_val == val): return False

        return True

    def backtest_strategy(self, symbol: str, history: List[FeatureVector], rules: List[Dict[str, Any]], prices: List[StockPrice]) -> Dict[str, Any]:
        """
        Simulates strategy performance over historical feature data.
        """
        trades = []
        equity = 100000.0 # Start with 1L INR
        position = 0
        entry_price = 0

        price_map = {p.date.date(): p.close for p in prices}

        for feat in history:
            date = feat.date.date()
            if date not in price_map: continue

            current_price = price_map[date]

            if position == 0 and self.evaluate_rules(rules, feat):
                # BUY
                position = equity / current_price
                entry_price = current_price
                trades.append({"date": date, "type": "BUY", "price": current_price})

            elif position > 0 and not self.evaluate_rules(rules, feat):
                # SELL (Exit when rules no longer met)
                equity = position * current_price
                trades.append({"date": date, "type": "SELL", "price": current_price, "profit": (current_price - entry_price)*position})
                position = 0

        return {
            "final_equity": equity,
            "total_trades": len(trades) // 2,
            "trade_log": trades
        }
