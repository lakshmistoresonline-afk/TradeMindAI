import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Header, HTTPException, status
from backend.core.config import settings

# Note: firebase_admin is initialized in backend/core/database.py

async def get_current_user(authorization: str = Header(None)):
    """
    Standardizes user authentication across the platform.
    Uses Firebase Admin SDK for token verification.
    """
    if not authorization:
        # Fallback for development if configured
        if settings.PROJECT_NAME == "TradeMind AI (DEV)":
            return {"uid": "dev_user", "email": "dev@trademind.ai"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    try:
        id_token = authorization.split("Bearer ")[1] if "Bearer " in authorization else authorization
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        return decoded_token
    except Exception as e:
        # Check for dev bypass
        if settings.PROJECT_NAME == "TradeMind AI (DEV)":
             return {"uid": "dev_user", "email": "dev@trademind.ai"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID Token: {str(e)}",
        )
