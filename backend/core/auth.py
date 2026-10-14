import os
import firebase_admin
from firebase_admin import auth
from fastapi import Header, HTTPException, status, Depends
from backend.core.config import settings

async def get_current_user(authorization: str = Header(None)):
    """
    Standardizes user authentication across the platform.
    Uses Firebase Admin SDK for token verification. Fails closed in production/staging.
    """
    env = str(os.getenv("ENVIRONMENT") or getattr(settings, "ENVIRONMENT", "production")).lower()
    is_production_or_staging = env in ("production", "staging")

    if not authorization:
        if not is_production_or_staging and env == "development":
            return {"uid": "dev_user", "email": "dev@trademind.ai"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    try:
        id_token = authorization.split("Bearer ")[1] if "Bearer " in authorization else authorization
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        return decoded_token
    except Exception:
        if not is_production_or_staging and env == "development":
             return {"uid": "test_user_123", "email": "dev@trademind.ai"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials.",
        )

async def get_current_admin(user: dict = Depends(get_current_user)):
    """
    Authorization layer for admin-only operations using trusted server-side email configuration.
    """
    email = user.get("email")
    admin_emails = getattr(settings, "ADMIN_EMAILS", [])
    if not email or email not in admin_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have administrative privileges",
        )
    return user
