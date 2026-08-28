import os
import sys
import asyncio
import datetime
import uuid
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container
from backend.domain.models.ios import TradeFeedback

async def populate():
    print("[*] Populating Trade Journal...")
    try:
        # We need a user_id. Use a fixed one for now or get from auth.
        user_id = "test_user_123"

        trades = [
            {
                "symbol": "RELIANCE",
                "entry_price": 2400.0,
                "exit_price": 2550.0,
                "quantity": 10,
                "entry_date": datetime.datetime.utcnow() - datetime.timedelta(days=10),
                "exit_date": datetime.datetime.utcnow() - datetime.timedelta(days=2),
                "pnl": 1500.0,
                "ai_score_at_entry": 82.0,
                "feedback": "Perfect institutional alignment. Trend was confirmed by EMA 20/50 cross.",
                "mistakes": [],
                "lessons": ["Trust the AI conviction during breakout phases."]
            },
            {
                "symbol": "TCS",
                "entry_price": 3800.0,
                "exit_price": 3720.0,
                "quantity": 5,
                "entry_date": datetime.datetime.utcnow() - datetime.timedelta(days=15),
                "exit_date": datetime.datetime.utcnow() - datetime.timedelta(days=12),
                "pnl": -400.0,
                "ai_score_at_entry": 55.0,
                "feedback": "Disciplined stop-loss execution. Entry was premature as FII flow was negative.",
                "mistakes": ["Early entry"],
                "lessons": ["Wait for institutional flow confirmation."]
            },
            {
                "symbol": "HDFCBANK",
                "entry_price": 1450.0,
                "exit_price": 1520.0,
                "quantity": 20,
                "entry_date": datetime.datetime.utcnow() - datetime.timedelta(days=5),
                "exit_date": datetime.datetime.utcnow() - datetime.timedelta(days=1),
                "pnl": 1400.0,
                "ai_score_at_entry": 78.0,
                "feedback": "Strong sector rotation into financials. Good holding period.",
                "mistakes": [],
                "lessons": ["Sector strength is a primary alpha driver."]
            }
        ]

        for t in trades:
            feedback = TradeFeedback(
                id=str(uuid.uuid4()),
                user_id=user_id,
                **t
            )
            await container.ios_repo.save_trade_feedback(feedback)
            print(f"   [+] Recorded Trade: {feedback.symbol} (PnL: ₹{feedback.pnl})")

        print("[*] Trade Journal population complete.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate())
