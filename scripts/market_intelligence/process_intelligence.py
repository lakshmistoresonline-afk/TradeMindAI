import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.workers.tasks import _process_intel_logic

if __name__ == "__main__":
    print("[*] Starting Market Intelligence Processing...")
    asyncio.run(_process_intel_logic())
    print("[SUCCESS] Intelligence Processing Complete.")
