import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container

async def test():
    print("[*] Testing Opportunities Repository...")
    try:
        active = await container.ios_repo.get_active_opportunities(limit=10)
        print(f"[*] Found {len(active)} active opportunities.")
        for opp in active:
            print(f"   - {opp.symbol}: {opp.type} (Score: {opp.conviction_score})")
            # Try to serialize to JSON to check for issues
            print(f"     JSON: {opp.model_dump_json()[:100]}...")
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
