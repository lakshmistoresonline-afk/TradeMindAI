from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from backend.services.exclusive_universe_service import ExclusiveUniverseService
from backend.core.container import container, get_stock_service
from backend.services.stock_service import StockService
from backend.app.db.nifty500_symbols import get_nifty_500_universe
from fastapi_cache.decorator import cache

router = APIRouter()

@router.get("/")
@cache(expire=300)
async def get_universes():
    """
    Returns metadata and verified exclusive constituent counts for the 4 NIFTY universes.
    """
    return ExclusiveUniverseService.get_universe_metadata()

@router.get("/{universe_id}/constituents")
@cache(expire=300)
async def get_universe_constituents(
    universe_id: str,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: StockService = Depends(get_stock_service)
):
    """
    Returns the constituent stocks assigned to the specified exclusive universe partition.
    """
    partitions = ExclusiveUniverseService.get_exclusive_partitions()
    if universe_id not in partitions:
        raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found.")

    symbols = partitions[universe_id]
    n500_info = get_nifty_500_universe()

    # Filter by search if provided
    if search:
        s_upper = search.strip().upper()
        symbols = [sym for sym in symbols if s_upper in sym or s_upper in n500_info.get(sym, "").upper()]

    total = len(symbols)
    paginated_symbols = symbols[offset:offset + limit]

    # Fetch stock details from repository for these symbols
    stocks = []
    for sym in paginated_symbols:
        stk = await service.repository.get_stock_by_symbol(sym)
        if stk:
            stocks.append(stk)
        else:
            stocks.append({
                "symbol": sym,
                "name": n500_info.get(sym, f"{sym} Limited"),
                "exchange": "NSE",
                "index_membership": universe_id,
                "last_price": None,
                "change": None,
                "volume": None,
                "updated_at": None
            })

    return {
        "universe_id": universe_id,
        "total": total,
        "limit": limit,
        "offset": offset,
        "constituents": stocks
    }

@router.get("/{universe_id}/signals")
@cache(expire=120)
async def get_universe_signals(
    universe_id: str
):
    """
    Returns valid eligible BUY signals for stocks in the specified exclusive universe.
    """
    partitions = ExclusiveUniverseService.get_exclusive_partitions()
    if universe_id not in partitions:
        raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found.")

    symbols = set(partitions[universe_id])

    # Query active/historical signals from database ledger matching symbols
    from backend.core.config import settings
    if getattr(settings, "QUARANTINE_ACTIVE", True):
        raise HTTPException(
            status_code=503,
            detail="QUARANTINED: Universe signal API endpoints are currently quarantined pending authentic market data verification."
        )

    from backend.core.postgres import SessionLocal, ShadowSignalDB
    from backend.api.v1.endpoints.equity import is_eligible_buy

    try:
        with SessionLocal() as session:
            signals = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.symbol.in_(list(symbols))
            ).all()

            eligible = []
            for sig in signals:
                if is_eligible_buy(sig):
                    data = {c.name: getattr(sig, c.name) for c in sig.__table__.columns}
                    eligible.append(data)

            return {
                "universe_id": universe_id,
                "total": len(eligible),
                "signals": eligible
            }
    except Exception as e:
        return {"universe_id": universe_id, "total": 0, "signals": [], "error": str(e)}
