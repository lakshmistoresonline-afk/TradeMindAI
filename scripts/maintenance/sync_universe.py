import asyncio
import sys
import os

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.core.container import container
from backend.services.universe_service import UniverseService

async def sync():
    print("Syncing Universe...")
    service = UniverseService(container.repository, container.provider)
    res = await service.sync_universe()
    print(f"Sync complete. {res}")

if __name__ == "__main__":
    asyncio.run(sync())
