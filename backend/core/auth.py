import firebase_admin
from firebase_admin import auth
from fastapi import Header, HTTPException, status, Depends
from backend.core.config import settings

# Note: firebase_admin is initialized in backend/core/database.py

async def get_current_user(authorization: str = Header(None)):
    """
    Validates the Firebase ID Token passed in the Authorization header.
    Expects format: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header. Format: 'Bearer <token>'",
        )

    try:
        id_token = authorization.split("Bearer ")[1]
        # Verify the ID token while checking if the token is revoked
        decoded_token = auth.verify_id_token(id_token, check_revoked=True)
        return decoded_token
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID Token has expired",
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID Token has been revoked",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Firebase ID Token: {str(e)}",
        )

def require_admin(user: dict = Depends(get_current_user)):
    """
    Ensures the user has the 'admin' claim.
    """
    if not user.get("admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return user
