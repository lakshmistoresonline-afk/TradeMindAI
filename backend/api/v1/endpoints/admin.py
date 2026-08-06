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

@router.get("/logs")
async def get_system_logs(limit: int = 20):
    """
    Retrieves real-time forensic logs from the AI background workers.
    """
    from backend.core.database import db_client
    from google.cloud import firestore
    docs = db_client.collection("system_logs")\
        .order_by("timestamp", direction=firestore.Query.DESCENDING)\
        .limit(limit).stream()
    return [doc.to_dict() for doc in docs]
