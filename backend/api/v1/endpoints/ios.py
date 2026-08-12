from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.core.container import container
from backend.core.auth import get_current_user
from backend.domain.models.ios import WorkspaceState, ResearchNote, MarketRegime, MarketOpportunity, MarketIntelligenceReport, TradeFeedback, LiveSignal
from backend.domain.models.data_platform import PortfolioHealth
from google.cloud import firestore
import uuid
import datetime
import traceback

router = APIRouter()

@router.get("/regime", response_model=MarketRegime)
async def get_market_regime():
    try:
        regime = await container.ios_repo.get_latest_regime()
        if not regime:
            return MarketRegime(
                date=datetime.datetime.utcnow(), regime="SIDEWAYS", risk_mode="NEUTRAL",
                sentiment_score=0.5, volatility_index=15.0,
                description="Market analysis engine initialized. Calculating institutional bias..."
            )
        return regime
    except Exception as e:
        print(f"Error in get_market_regime: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/opportunities")
async def get_opportunities(limit: int = 20):
    try:
        active = []
        try:
            active = await container.ios_repo.get_active_opportunities(limit=limit)
        except Exception as repo_err:
            print(f"Repository error fetching opportunities: {repo_err}")
            # Fallback to bootstrap if repo fails (e.g. DB issue)
            active = []

        if not active:
            try:
                stocks = await container.repository.get_all_stocks(limit=100)
                active = container.opportunity_engine.find_opportunities(stocks)
                # Save asynchronously to avoid blocking
                for opp in active:
                    try: await container.ios_repo.save_opportunity(opp)
                    except: pass
            except Exception as engine_err:
                print(f"Engine error generating opportunities: {engine_err}")
                return []

        # Manual serialization for maximum robustness
        results = []
        for o in active:
            try:
                # Handle both Pydantic objects and dicts
                is_dict = isinstance(o, dict)

                oid = str(o.get("id") if is_dict else getattr(o, "id", uuid.uuid4()))
                symbol = str(o.get("symbol") if is_dict else getattr(o, "symbol", "UNK"))
                otype = str(o.get("type") if is_dict else getattr(o, "type", "MOMENTUM"))
                score = float(o.get("conviction_score") if is_dict else getattr(o, "conviction_score", 0))
                thesis = str(o.get("ai_thesis") if is_dict else getattr(o, "ai_thesis", ""))
                indicators = list(o.get("indicators") if is_dict else getattr(o, "indicators", []))

                results.append({
                    "id": oid,
                    "symbol": symbol,
                    "type": otype,
                    "conviction_score": score,
                    "ai_thesis": thesis,
                    "indicators": indicators,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })
            except Exception as ser_err:
                print(f"Serialization error in /opportunities: {ser_err}")

        return results
    except Exception as e:
        print(f"Critical Error in get_opportunities: {e}")
        traceback.print_exc()
        return []

@router.get("/intel", response_model=MarketIntelligenceReport)
async def get_market_intelligence(type: str = "CLOSING"):
    try:
        report = await container.ios_repo.get_latest_intel_report(type)
        if not report:
            return MarketIntelligenceReport(
                id="initial", type=type, date=datetime.datetime.utcnow(),
                summary="Market Intelligence Engine initialized. Synchronizing session data...",
                key_events=["Sync Active"], top_movers=[], sector_performance={}, ai_bias="NEUTRAL"
            )
        return report
    except Exception as e:
        print(f"Error in get_market_intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notes")
async def create_research_note(note_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    try:
        note = ResearchNote(
            id=str(uuid.uuid4()),
            user_id=current_user["uid"],
            symbol=note_data["symbol"],
            content=note_data["content"],
            tags=note_data.get("tags", [])
        )
        await container.ios_repo.save_research_note(note)
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notes/{symbol}", response_model=List[ResearchNote])
async def get_research_notes(symbol: str, current_user: dict = Depends(get_current_user)):
    return await container.ios_repo.get_stock_notes(current_user["uid"], symbol)

@router.get("/workspaces", response_model=List[WorkspaceState])
async def get_workspaces(current_user: dict = Depends(get_current_user)):
    return await container.ios_repo.get_user_workspaces(current_user["uid"])

@router.post("/workspaces")
async def save_workspace(workspace: WorkspaceState, current_user: dict = Depends(get_current_user)):
    workspace.user_id = current_user["uid"]
    await container.ios_repo.save_workspace(workspace)
    return workspace

@router.get("/journal", response_model=List[TradeFeedback])
async def get_trade_journal(current_user: dict = Depends(get_current_user)):
    return await container.ios_repo.get_user_trades(current_user["uid"])

@router.get("/portfolio/health", response_model=PortfolioHealth)
async def get_portfolio_health_dashboard(current_user: dict = Depends(get_current_user)):
    """
    Vision 2.2: Dynamic Risk Engine.
    Calculates real-time health and risk metrics for the user's holdings.
    """
    from backend.services.portfolio_engine import PortfolioEngine
    # 1. Fetch current holdings (Simulated for Institutional Demo)
    stocks = await container.repository.get_all_stocks(limit=5)

    # 2. Analyze
    health = PortfolioEngine.analyze_health(current_user["uid"], stocks)
    return health

@router.get("/portfolio/optimize")
async def get_portfolio_optimizations(current_user: dict = Depends(get_current_user)):
    """
    Vision 2.2: Institutional Portfolio Optimizer.
    Suggests rebalancing weights using Mean-Variance baseline.
    """
    from backend.services.portfolio_engine import PortfolioEngine
    # 1. Fetch current holdings
    stocks = await container.repository.get_all_stocks(limit=5)

    # 2. Optimize
    return PortfolioEngine.optimize_weights(stocks)

@router.post("/journal")
async def add_trade_to_journal(trade_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    try:
        ai_score = 75.0
        feedback = container.coach_service.generate_feedback({
            **trade_data,
            "user_id": current_user["uid"],
            "entry_date": datetime.datetime.fromisoformat(trade_data["entry_date"]),
            "exit_date": datetime.datetime.fromisoformat(trade_data["exit_date"])
        }, ai_score)
        await container.ios_repo.save_trade_feedback(feedback)
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/live", response_model=List[LiveSignal])
async def get_live_signals_audit(limit: int = 100):
    """
    Vision 2.2: Live Production Signal Audit from SQL Tier.
    """
    try:
        return await container.ios_repo.get_active_live_signals()
    except Exception as e:
        print(f"Error fetching live signals: {e}")
        return []

@router.get("/deals", response_model=List[Dict[str, Any]])
async def get_bulk_deals(symbol: Optional[str] = None):
    """
    Vision 2.2: Institutional Bulk Deal Feed.
    Returns latest heavy-weight transactions for the specified symbol or entire universe.
    """
    from backend.core.postgres import SessionLocal, BulkDealDB
    with SessionLocal() as session:
        query = session.query(BulkDealDB)
        if symbol:
            query = query.filter(BulkDealDB.symbol == symbol)

        deals = query.order_by(BulkDealDB.date.desc()).limit(50).all()
        return [{
            "symbol": d.symbol,
            "client_name": d.client_name,
            "deal_type": d.deal_type,
            "quantity": d.quantity,
            "price": d.price,
            "value_cr": d.value_cr,
            "date": d.date.isoformat()
        } for d in deals]

@router.get("/calendar")
async def get_economic_calendar():
    return [
        {"time": "11:00 AM", "country": "IN", "event": "RBI Policy Meet", "impact": "CRITICAL", "forecast": "6.50%", "actual": "6.50%"},
        {"time": "6:00 PM", "country": "US", "event": "CPI Data", "impact": "HIGH", "forecast": "3.1%", "actual": "---"}
    ]
