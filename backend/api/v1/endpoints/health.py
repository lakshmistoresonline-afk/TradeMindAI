from fastapi import APIRouter, Depends
from backend.core.container import container
import datetime

router = APIRouter()

@router.get("/")
async def get_system_health():
    """
    Phase 45: Canonical System Status.
    """
    return await container.health_service.get_comprehensive_health()
