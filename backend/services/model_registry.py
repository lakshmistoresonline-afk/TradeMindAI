import datetime
from typing import List, Dict, Any, Optional
from backend.domain.models.data_platform import ModelMetadata
from backend.domain.interfaces.repository import IDataPlatformRepository

class ModelRegistryService:
    """
    Workstream 9: Model Registry.
    Manages model metadata and champion/challenger promotion.
    """
    def __init__(self, repository: IDataPlatformRepository):
        self.repository = repository

    async def register_model(self, metadata: ModelMetadata):
        await self.repository.save_model_metadata(metadata)

    async def get_champion(self, symbol: str) -> Optional[ModelMetadata]:
        return await self.repository.get_champion_model(symbol)

    async def promote_to_champion(self, name: str):
        """
        Formally promotes a model to champion state.
        """
        with self.repository.session_factory() as pg:
            from backend.core.postgres import ModelMetadataDB
            model = pg.query(ModelMetadataDB).filter(ModelMetadataDB.name == name).first()
            if not model:
                return {"status": "FAILED", "reason": "MODEL_NOT_FOUND"}

            # Demote current champion for this symbol
            pg.query(ModelMetadataDB).filter(
                ModelMetadataDB.symbol == model.symbol,
                ModelMetadataDB.is_champion == True
            ).update({"is_champion": False})

            # Promote new one
            model.is_champion = True
            pg.commit()
            return {"status": "SUCCESS", "promoted": name}
