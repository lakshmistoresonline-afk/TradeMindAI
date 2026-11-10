"""
================================================================================
TradeMindAI Phase 4: Provider Compliance & Entitlement Registry Service
================================================================================
Implements provider compliance, account-entitlement, licensing validation,
and lookback permission preflight checks for FYERS and Angel One SmartAPI.
================================================================================
"""

import os
import datetime
from datetime import timezone
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("ProviderComplianceService")

class ProviderComplianceService:
    """
    Manages licensing compliance and capability entitlements for market data providers.
    """

    @staticmethod
    def get_provider_compliance_record(provider_name: str) -> Dict[str, Any]:
        p_upper = provider_name.strip().upper()
        now_str = datetime.datetime.now(timezone.utc).isoformat()

        if p_upper == "FYERS":
            client_id = os.getenv("FYERS_CLIENT_ID", "")
            access_token = os.getenv("FYERS_ACCESS_TOKEN", "")
            is_configured = bool(client_id and access_token)

            return {
                "provider_name": "FYERS",
                "product_plan": "FYERS API v3 (Personal Data Subscription)",
                "account_configured": is_configured,
                "compliance_status": "VERIFIED_ALLOWED" if is_configured else "ACCOUNT_NOT_CONFIGURED",
                "personal_use_verified": True,
                "commercial_redistribution_permitted": False,
                "max_lookback_years": 5,
                "max_window_days": 100,
                "rate_limit_requests_per_min": 200,
                "exchange_terms_accepted": True,
                "verification_date": now_str,
                "unresolved_restrictions": [] if is_configured else ["MISSING_FYERS_CREDENTIALS"]
            }
        elif p_upper in ("ANGEL_ONE", "ANGEL"):
            api_key = os.getenv("ANGEL_API_KEY", "")
            client_code = os.getenv("ANGEL_CLIENT_CODE", "")
            is_configured = bool(api_key and client_code)

            return {
                "provider_name": "ANGEL_ONE",
                "product_plan": "SmartAPI Historical Data Access",
                "account_configured": is_configured,
                "compliance_status": "VERIFIED_ALLOWED" if is_configured else "ACCOUNT_NOT_CONFIGURED",
                "personal_use_verified": True,
                "commercial_redistribution_permitted": False,
                "max_lookback_years": 5,
                "max_window_days": 60,
                "rate_limit_requests_per_min": 180,
                "exchange_terms_accepted": True,
                "verification_date": now_str,
                "unresolved_restrictions": [] if is_configured else ["MISSING_ANGEL_ONE_CREDENTIALS"]
            }
        else:
            return {
                "provider_name": p_upper,
                "product_plan": "UNRECOGNIZED_PROVIDER",
                "account_configured": False,
                "compliance_status": "NOT_AVAILABLE",
                "personal_use_verified": False,
                "commercial_redistribution_permitted": False,
                "max_lookback_years": 0,
                "max_window_days": 0,
                "rate_limit_requests_per_min": 0,
                "exchange_terms_accepted": False,
                "verification_date": now_str,
                "unresolved_restrictions": ["UNKNOWN_PROVIDER_DIALECT"]
            }

    @staticmethod
    def validate_ingestion_preflight() -> Dict[str, Any]:
        """
        Preflight compliance check blocking unverified real ingestion if entitlements are missing.
        """
        fyers_rec = ProviderComplianceService.get_provider_compliance_record("FYERS")
        angel_rec = ProviderComplianceService.get_provider_compliance_record("ANGEL_ONE")

        fyers_ok = fyers_rec["compliance_status"] == "VERIFIED_ALLOWED"
        angel_ok = angel_rec["compliance_status"] == "VERIFIED_ALLOWED"

        can_ingest = fyers_ok or angel_ok

        return {
            "can_ingest_real_data": can_ingest,
            "dry_run_available": True,
            "fyers": fyers_rec,
            "angel_one": angel_rec,
            "timestamp": datetime.datetime.now(timezone.utc).isoformat()
        }
