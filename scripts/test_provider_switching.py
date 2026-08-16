import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.config import settings
from backend.core.container import container

async def test():
    print("--- TRADEMIND PROVIDER SWITCHING AUDIT ---")

    # 1. Test yfinance (Default)
    settings.MARKET_DATA_PROVIDER = "yfinance"
    container._provider = None # Reset
    provider = container.provider
    print(f"[*] Provider: {type(provider).__name__}")
    print(f"[*] Capabilities: {provider.capabilities}")

    # 2. Test Groww
    settings.MARKET_DATA_PROVIDER = "groww"
    container._provider = None # Reset
    provider = container.provider
    print(f"[*] Provider: {type(provider).__name__}")
    print(f"[*] Capabilities: {provider.capabilities}")

    print("\n--- AUDIT COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test())
