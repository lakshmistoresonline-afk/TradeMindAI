import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

from backend.core.container import container
from backend.core.postgres import init_db

async def verify():
    print("\n--- TradeMind AI: HYBRID ARCHITECTURE LINKAGE VERIFICATION ---\n")

    # 1. Check Container Injection
    repo = container.repository
    print(f"[CONTAINER] Active Repository: {type(repo).__name__}")
    if "Hybrid" in type(repo).__name__:
        print("✅ SUCCESS: Container is correctly injecting the Hybrid tier.")
    else:
        print("❌ FAILURE: Container is still using legacy Firestore repository.")

    # 2. Check Data Retrieval
    try:
        init_db()
        stock = await repo.get_stock_by_symbol("RELIANCE")
        if stock:
            print(f"[DATABASE] Retrieved RELIANCE from SQL operational store.")
            print(f"           AI Score: {stock.ai_investment_score}")
            print(f"           Updated At: {stock.updated_at}")
            print("✅ SUCCESS: Data link is operational.")
        else:
            print("⚠️ WARNING: RELIANCE not found in SQL. Did you run the population script?")
    except Exception as e:
        print(f"❌ ERROR: Could not retrieve data through hybrid link: {e}")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(verify())
