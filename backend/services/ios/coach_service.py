from typing import List, Dict, Any
from backend.domain.models.ios import TradeFeedback
from datetime import datetime

class TradeCoachService:
    @staticmethod
    def generate_feedback(trade_data: Dict[str, Any], ai_sentiment_at_entry: float) -> TradeFeedback:
        """
        AI Trade Coach: Analyzes execution quality and provides mentorship.
        """
        symbol = trade_data["symbol"]
        pnl = trade_data["pnl"]
        entry_price = trade_data["entry_price"]
        exit_price = trade_data["exit_price"]

        status = "PROFIT" if pnl > 0 else "LOSS"
        feedback = ""
        mistakes = []
        lessons = []

        # 1. Execution Logic
        # Was it a "Good Loss" or a "Bad Win"?
        if status == "PROFIT":
            if ai_sentiment_at_entry > 70:
                feedback = f"Excellent alignment. You entered {symbol} when AI conviction was high. Perfect execution of the institutional thesis."
            else:
                feedback = f"You made a profit on {symbol}, but AI conviction was low at entry. This might have been a 'lucky win'. Ensure you follow the multi-agent consensus for long-term consistency."
                mistakes.append("Low conviction entry")
        else:
            if ai_sentiment_at_entry > 70:
                feedback = f"A disciplined loss. You followed a high-conviction AI setup, but the market invalidated the thesis. These 'good losses' are part of institutional trading."
            else:
                feedback = f"Poor execution. You entered {symbol} against the AI consensus. This was a low-probability trade."
                mistakes.append("Trading against bias")
                lessons.append("Wait for AI consensus alignment before entry.")

        # 2. Risk Management (Placeholder)
        if abs(pnl / entry_price) > 0.1: # > 10% move
             lessons.append("Review your stop-loss placement. The volatility on this trade was higher than institutional standards.")

        return TradeFeedback(
            id=trade_data.get("id", "t-1"),
            user_id=trade_data["user_id"],
            symbol=symbol,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=trade_data["quantity"],
            entry_date=trade_data["entry_date"],
            exit_date=trade_data["exit_date"],
            pnl=pnl,
            ai_score_at_entry=ai_sentiment_at_entry,
            feedback=feedback,
            mistakes=mistakes,
            lessons=lessons
        )
