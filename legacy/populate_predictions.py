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
from backend.domain.models.data_platform import Prediction

async def populate():
    print("[*] Populating Predictions...")
    try:
        symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]

        for symbol in symbols:
            prediction = Prediction(
                symbol=symbol,
                date=datetime.datetime.utcnow(),
                model_version="v2.2.0-beta",
                prediction="UP" if symbol in ["RELIANCE", "HDFCBANK"] else "NEUTRAL",
                confidence=0.82 if symbol == "RELIANCE" else 0.65,
                metadata={"probability_up": 0.82, "source": "bootstrap_seeding"}
            )
            await container.data_platform_repo.save_prediction(prediction)
            print(f"   [+] Saved Prediction: {symbol} ({prediction.prediction})")

        print("[*] Predictions population complete.")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(populate())
