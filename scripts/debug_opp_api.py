import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.container import container
import datetime
import uuid

async def debug():
    print("[*] Debugging Opportunities API logic (v2)...")
    try:
        active = await container.ios_repo.get_active_opportunities(limit=20)
        print(f"[*] Repository returned {len(active)} items.")

        results = []
        for o in active:
            try:
                is_dict = isinstance(o, dict)

                oid = str(o.get("id") if is_dict else getattr(o, "id", uuid.uuid4()))
                symbol = str(o.get("symbol") if is_dict else getattr(o, "symbol", "UNK"))
                otype = str(o.get("type") if is_dict else getattr(o, "type", "MOMENTUM"))
                score = float(o.get("conviction_score") if is_dict else getattr(o, "conviction_score", 0))
                thesis = str(o.get("ai_thesis") if is_dict else getattr(o, "ai_thesis", ""))
                indicators = list(o.get("indicators") if is_dict else getattr(o, "indicators", []))

                results.append({
                    "id": oid,
                    "symbol": symbol,
                    "type": otype,
                    "conviction_score": score,
                    "ai_thesis": thesis,
                    "indicators": indicators,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })
            except Exception as ser_err:
                print(f"   [!] Serialization error for {getattr(o, 'symbol', 'unknown')}: {ser_err}")

        print(f"[*] Final payload contains {len(results)} items.")
        if len(results) > 0:
            print(f"[*] Sample: {results[0]['symbol']} ({results[0]['type']})")

    except Exception as e:
        print(f"[!] Critical Error in logic: {e}")

if __name__ == "__main__":
    asyncio.run(debug())
