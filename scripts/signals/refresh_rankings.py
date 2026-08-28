import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.workers.tasks import _refresh_rankings_logic

if __name__ == "__main__":
    print("[*] Refreshing AI Rankings and Opportunities...")
    asyncio.run(_refresh_rankings_logic())
    print("[SUCCESS] Rankings Refreshed.")
