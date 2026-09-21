from fastapi import APIRouter
from backend.api.v1.endpoints import auth, stocks, admin, ios, market_data, equity, health, user, public, stream

api_router = APIRouter()
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ios.router, prefix="/ios", tags=["ios"])
api_router.include_router(equity.router, prefix="/equity", tags=["equity"])
api_router.include_router(health.router, prefix="/system/health", tags=["health"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(stream.router, prefix="/stream", tags=["stream"])
