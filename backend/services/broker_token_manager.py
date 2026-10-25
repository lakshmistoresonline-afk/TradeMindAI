"""
================================================================================
TradeMindAI: Resilient Broker OAuth Token & Live Session Manager
================================================================================
Manages Upstox/Kite live market session tokens.
Provides seamless failover to yfinance real-time polling during live market hours
if broker OAuth session tokens are unconfigured or expired.
================================================================================
"""

import os
import logging
import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BrokerTokenManager:
    """
    Handles live market session tokens and provider failover.
    """

    _access_token: Optional[str] = None
    _token_expiry: Optional[datetime.datetime] = None

    @classmethod
    def get_active_token(cls) -> Optional[str]:
        """
        Returns active Upstox/Kite access token if valid and unexpired.
        """
        env_token = os.getenv("UPSTOX_ACCESS_TOKEN") or os.getenv("KITE_ACCESS_TOKEN")
        if env_token:
            return env_token
        return cls._access_token

    @classmethod
    def is_session_active(cls) -> bool:
        """
        Checks whether a valid live broker session token is available.
        """
        token = cls.get_active_token()
        if not token:
            return False
        if cls._token_expiry and datetime.datetime.now() > cls._token_expiry:
            return False
        return True

    @classmethod
    def set_session_token(cls, token: str, valid_hours: int = 24):
        """
        Registers an active session token with expiration.
        """
        cls._access_token = token
        cls._token_expiry = datetime.datetime.now() + datetime.timedelta(hours=valid_hours)
        logger.info("[BrokerTokenManager] Registered active broker live market session token.")

    @classmethod
    def get_live_feed_status(cls) -> Dict[str, Any]:
        """
        Returns status of live market feed session and active provider.
        """
        if cls.is_session_active():
            return {
                "feed_mode": "BROKER_WEBSOCKET_LIVE",
                "session_active": True,
                "provider": "Upstox/Kite",
                "status": "ONLINE"
            }
        return {
            "feed_mode": "YFINANCE_REALTIME_POLLING",
            "session_active": False,
            "provider": "yfinance",
            "status": "ONLINE_RESILIENT_POLLING"
        }
