import firebase_admin
from firebase_admin import auth
from fastapi import Header, HTTPException, status, Depends
from backend.core.config import settings

async def get_current_user(authorization: str = Header(None)):
    """
    Standardizes user authentication across the platform.
    Uses Firebase Admin SDK for token verification. Fails closed in production.
    """
    is_production = settings.ENVIRONMENT == "production" or os.getenv("ENVIRONMENT") == "production"

    if not authorization:
        if not is_production and settings.ENVIRONMENT in ("development", "test"):
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
        if not is_production and settings.ENVIRONMENT in ("development", "test"):
             return {"uid": "test_user_123", "email": "dev@trademind.ai"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID Token: {str(e)}",
        )

async def get_current_admin(user: dict = Depends(get_current_user)):
    """
    Authorization layer for admin-only operations.
    """
    if user.get("email") not in settings.ADMIN_EMAILS and not user.get("isAdmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have administrative privileges",
        )
    return user
