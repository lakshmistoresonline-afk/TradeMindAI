import asyncio
import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.infrastructure.repositories.hybrid_repository import HybridDataPlatformRepository
from unittest.mock import MagicMock

async def main():
    try:
        session_factory = MagicMock()
        firestore_db = MagicMock()
        repo = HybridDataPlatformRepository(session_factory, firestore_db)
        print("Successfully instantiated HybridDataPlatformRepository")
    except TypeError as e:
        print(f"Failed to instantiate: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
