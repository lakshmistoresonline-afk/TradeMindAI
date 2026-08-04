from fastapi import APIRouter, Depends
from backend.core.auth import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    # Check if user is admin
    if current_user.get("role") != "admin":
        return {"error": "Unauthorized"}
    return {
        "total_users": 100,
        "active_jobs": 5,
        "system_health": "OK"
    }

@router.post("/retrain/{model_name}")
async def retrain_model(model_name: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        return {"error": "Unauthorized"}
    return {"message": f"Retraining started for {model_name}"}
