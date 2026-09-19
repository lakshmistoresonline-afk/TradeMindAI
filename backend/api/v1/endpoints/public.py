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

@router.get("/schema-debug")
def check_schema():
    from backend.core.postgres import engine
    from sqlalchemy import inspect
    inspector = inspect(engine)
    try:
        cols = inspector.get_columns("live_signals")
        return {"live_signals_columns": [c['name'] for c in cols]}
    except Exception as e:
        return {"error": str(e)}

