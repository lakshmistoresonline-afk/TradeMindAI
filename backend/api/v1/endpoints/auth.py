from fastapi import APIRouter, Depends, HTTPException
from backend.core.auth import get_current_user

router = APIRouter()

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """
    Returns current authenticated user info.
    """
    return {
        "uid": user.get("uid"),
        "email": user.get("email"),
        "email_verified": user.get("email_verified", False)
    }

@router.post("/login")
async def login():
    # Login is handled by Firebase client side.
    # This endpoint is just a placeholder.
    return {"message": "Login should be performed via Firebase Client SDK"}
