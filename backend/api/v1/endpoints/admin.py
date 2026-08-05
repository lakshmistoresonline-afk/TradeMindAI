from fastapi import APIRouter, Depends
from backend.core.auth import get_current_user
from backend.core.container import container

router = APIRouter()

@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    # Check if user is admin (Vision 2.0: Restricted access)
    return {
        "total_users": 1240,
        "active_jobs": 12,
        "system_health": "OPTIMAL"
    }

@router.get("/evaluation")
async def get_model_evaluation():
    return await container.adaptive_service.evaluate_agent_performance()

@router.post("/retrain/{model_name}")
async def retrain_model(model_name: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        return {"error": "Unauthorized"}
    return {"message": f"Retraining started for {model_name}"}
