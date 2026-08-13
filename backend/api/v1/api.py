from fastapi import APIRouter
from backend.api.v1.endpoints import auth, stocks, analysis, ai, admin, ios, stream

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ios.router, prefix="/ios", tags=["ios"])
api_router.include_router(stream.router, prefix="/stream", tags=["stream"])
