import asyncio
import sys
import os
from unittest.mock import MagicMock

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.infrastructure.repositories.hybrid_repository import HybridDataPlatformRepository

async def main():
    try:
        session_factory = MagicMock()
        firestore_db = MagicMock()

        # Mock firestore structure
        collection_mock = MagicMock()
        document_mock = MagicMock()
        firestore_db.collection.return_value = collection_mock
        collection_mock.document.return_value = document_mock

        repo = HybridDataPlatformRepository(session_factory, firestore_db)
        print("Successfully instantiated HybridDataPlatformRepository")

        # Test one of the new methods
        mock_health = MagicMock()
        mock_health.user_id = "test_user"
        mock_health.model_dump.return_value = {"user_id": "test_user", "score": 85}

        await repo.save_portfolio_health(mock_health)
        print("Successfully called save_portfolio_health")

    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
