import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Header, HTTPException, status, Depends
from backend.core.config import settings

# Note: firebase_admin is initialized in backend/core/database.py

async def get_current_user(authorization: str = Header(None)):
    """
    Standardizes user authentication across the platform.
    Uses Firebase Admin SDK for token verification.
    """
    # Environment guard: Allow dev fallback only in development mode
    if not authorization:
        if settings.ENVIRONMENT == "development":
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
        # Only allow bypass in development
        if settings.ENVIRONMENT == "development":
             return {"uid": "test_user_123", "email": "dev@trademind.ai"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID Token: {str(e)}",
        )

async def get_current_admin(user: dict = Depends(get_current_user)):
    """
    Authorization layer for admin-only operations.
    """
    if user.get("email") not in settings.ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have administrative privileges",
        )
    return user
