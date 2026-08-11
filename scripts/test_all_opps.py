import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container
from backend.domain.models.ios import MarketOpportunity

async def test():
    print("[*] Testing All Opportunities Mapping...")
    try:
        from backend.core.postgres import OpportunityDB
        with container.repository.session_factory() as pg:
            res = pg.query(OpportunityDB).all()
            print(f"[*] Found {len(res)} records in database.")

            success = 0
            fail = 0
            for r in res:
                try:
                    data = {
                        "id": r.id,
                        "symbol": r.symbol,
                        "type": r.type,
                        "conviction_score": float(r.conviction_score),
                        "ai_thesis": r.ai_thesis,
                        "indicators": r.indicators if isinstance(r.indicators, list) else [],
                        "timestamp": r.timestamp
                    }
                    MarketOpportunity(**data)
                    success += 1
                except Exception as e:
                    print(f"   [!] Failed to map {r.symbol}: {e}")
                    fail += 1

            print(f"[*] Summary: Success={success}, Fail={fail}")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
