from fastapi import APIRouter
from backend.services.seo_service import SEOService

router = APIRouter()

@router.get("/seo/{page}")
async def get_seo_metadata(page: str):
    return SEOService.get_metadata(page)

@router.get("/config")
async def get_public_config():
    return {
        "version": "1.4.0",
        "universe": "NIFTY-200",
        "strategy": "V2.2 FROZEN",
        "real_trading": False
    }
