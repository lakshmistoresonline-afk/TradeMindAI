from fastapi import APIRouter, Depends, HTTPException
from backend.core.auth import get_current_user
from backend.core.postgres import SessionLocal, UserChartDB, UserReportDB, UserWatchlistDB, UserSubscriptionDB, UserReferralDB
from typing import List, Dict, Any, Optional
import uuid
import datetime

router = APIRouter()

# --- CHARTS ---
@router.get("/charts")
async def get_user_charts(current_user: dict = Depends(get_current_user)):
    with SessionLocal() as session:
        return session.query(UserChartDB).filter(UserChartDB.user_id == current_user["uid"]).all()

@router.post("/charts")
async def save_user_chart(chart_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    with SessionLocal() as session:
        chart = UserChartDB(
            id=str(uuid.uuid4()),
            user_id=current_user["uid"],
            symbol=chart_data.get("symbol"),
            name=chart_data.get("name", "Untitled Chart"),
            config_json=chart_data.get("config")
        )
        session.add(chart)
        session.commit()
        return chart

# --- REPORTS ---
@router.get("/reports")
async def get_user_reports(current_user: dict = Depends(get_current_user)):
    with SessionLocal() as session:
        return session.query(UserReportDB).filter(UserReportDB.user_id == current_user["uid"]).all()

# --- WATCHLIST ---
@router.get("/watchlist")
async def get_watchlist(current_user: dict = Depends(get_current_user)):
    with SessionLocal() as session:
        return [w.symbol for w in session.query(UserWatchlistDB).filter(UserWatchlistDB.user_id == current_user["uid"]).all()]

@router.post("/watchlist/{symbol}")
async def add_to_watchlist(symbol: str, current_user: dict = Depends(get_current_user)):
    with SessionLocal() as session:
        item = UserWatchlistDB(user_id=current_user["uid"], symbol=symbol.upper())
        session.merge(item) # merge handles duplicate symbol for same user
        session.commit()
        return {"status": "success"}

# --- SUBSCRIPTION ---
@router.get("/subscription")
async def get_subscription(current_user: dict = Depends(get_current_user)):
    with SessionLocal() as session:
        sub = session.query(UserSubscriptionDB).filter(UserSubscriptionDB.user_id == current_user["uid"]).first()
        if not sub:
            return {"plan_id": "FREE", "status": "ACTIVE"}
        return sub

# --- REFERRALS ---
@router.get("/referrals")
async def get_referrals(current_user: dict = Depends(get_current_user)):
    with SessionLocal() as session:
        return session.query(UserReferralDB).filter(UserReferralDB.referrer_id == current_user["uid"]).all()

@router.post("/referrals")
async def send_referral(ref_data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    from backend.services.referral_service import ReferralService
    success = await ReferralService.create_referral(current_user["uid"], ref_data.get("email"))
    if not success:
        raise HTTPException(status_code=400, detail="Referral already exists for this email.")
    return {"status": "success"}

# --- B2B LEADS ---
@router.post("/b2b/request")
async def request_b2b_access(lead_data: Dict[str, Any]):
    from backend.services.lead_service import LeadService
    lead_id = await LeadService.capture_lead(lead_data)
    return {"status": "success", "lead_id": lead_id}

# --- UPGRADE ---
@router.post("/upgrade")
async def upgrade_user_plan(data: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    from backend.services.monetization_service import MonetizationService
    success = await MonetizationService.upgrade_to_pro(current_user["uid"], data.get("provider_ref", "sim_123"))
    return {"status": "success" if success else "failed"}
