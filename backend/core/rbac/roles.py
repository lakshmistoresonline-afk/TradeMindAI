from enum import Enum
from typing import List, Dict

class Role(str, Enum):
    GUEST = "guest"
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

# Permission Matrix
PERMISSIONS = {
    Role.FREE: ["view_dashboard", "view_market", "view_analysis"],
    Role.PRO: ["view_dashboard", "view_market", "view_analysis", "adhoc_analysis", "chat_ai"],
    Role.PREMIUM: ["view_dashboard", "view_market", "view_analysis", "adhoc_analysis", "chat_ai", "run_backtest", "strategy_builder"],
    Role.ADMIN: ["*"] # All permissions
}

def has_permission(user_role: str, required_permission: str) -> bool:
    if user_role == Role.ADMIN:
        return True

    user_perms = PERMISSIONS.get(user_role, [])
    return required_permission in user_perms
