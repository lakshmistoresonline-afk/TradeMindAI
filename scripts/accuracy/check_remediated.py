import os
import sys
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def check():
    symbols = ["GUJGASLTD", "LTIM", "PEL", "TATAMOTORS"]
    dp_repo = container.data_platform_repo

    print("--- REMEDIATED SYMBOL HEALTH CHECK ---")

    for s in symbols:
        print(f"[*] Checking {s}...")
        feats = await dp_repo.get_features_by_range(s, datetime.utcnow() - timedelta(days=7), datetime.utcnow())
        if feats:
            print(f"   [+] Features FOUND: {len(feats)} vectors")
            # Try scoring
            ml_res = await container.ml_service.predict_with_champion(s, feats[-1].features)
            print(f"   [+] ML Score: {ml_res.get('confidence')}% (Direction: {ml_res.get('prediction')})")
        else:
            print(f"   [!] Features MISSING")

if __name__ == "__main__":
    asyncio.run(check())
