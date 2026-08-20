
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def check():
    symbols = ["SBIN", "RELIANCE", "TCS"]
    for s in symbols:
        m = await container.data_platform_repo.get_champion_model(s)
        print(f"{s} Champ: {m}")

if __name__ == "__main__":
    asyncio.run(check())
