import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.workers.tasks import _analyze_stock_ai_logic

async def main():
    symbol = "ADANIENSOL"
    print(f"[*] Starting AI Analysis for {symbol}...")
    try:
        result = await _analyze_stock_ai_logic(symbol)
        print(f"[*] Result: {result}")
    except Exception as e:
        print(f"[!] Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
