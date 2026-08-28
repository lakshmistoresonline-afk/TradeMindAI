from fastapi import Depends, HTTPException, status
from backend.core.auth import get_current_user
from backend.core.rbac.roles import has_permission, Role

def require_permission(permission: str):
    async def permission_dependency(current_user: dict = Depends(get_current_user)):
        # Get role from user claims or database
        user_role = current_user.get("role", Role.FREE)

        if not has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required. Current role: {user_role}"
            )
        return current_user
    return permission_dependency
