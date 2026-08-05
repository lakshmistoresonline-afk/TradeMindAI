import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Header, HTTPException, status
from backend.core.config import settings

# Note: firebase_admin is initialized in backend/core/database.py

async def get_current_user(authorization: str = Header(None)):
    # Mock user for development - Bypass security
    return {"uid": "dev_user", "email": "dev@trademind.ai"}

    # Real verification logic (commented out for revert)
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header. Format: 'Bearer <token>'",
        )

    try:
        id_token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID Token: {str(e)}",
        )
    """
