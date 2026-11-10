"""
================================================================================
TradeMindAI Phase 4: Market Data Providers & Repair Management API Endpoints
================================================================================
Provides endpoints for provider health, compliance registry, security master audit,
missing-data repair planner, controlled ingestion, and signal readiness diagnostics.
================================================================================
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, Optional
import datetime

from backend.services.providers.fyers_adapter import FYERSProviderAdapter
from backend.services.providers.angel_one_adapter import AngelOneProviderAdapter
from backend.services.provider_compliance_service import ProviderComplianceService
from backend.services.security_master_service import SecurityMasterService
from backend.services.data_repair_planner_service import DataRepairPlannerService

router = APIRouter(prefix="/providers", tags=["Market Data Providers & Repair"])

@router.get("/health")
async def get_providers_health() -> Dict[str, Any]:
    """
    Returns health, connection status, rate limits, and authentication state for FYERS & Angel One adapters.
    """
    fyers = FYERSProviderAdapter()
    angel = AngelOneProviderAdapter()

    fyers_health = await fyers.health_check()
    angel_health = await angel.health_check()

    return {
        "fyers": fyers_health,
        "angel_one": angel_health,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

@router.get("/compliance")
async def get_providers_compliance() -> Dict[str, Any]:
    """
    Returns compliance, licensing, and account entitlement registry preflight.
    """
    return ProviderComplianceService.validate_ingestion_preflight()

@router.get("/security-master/audit")
async def audit_security_master() -> Dict[str, Any]:
    """
    Audits NIFTY 500 security master mapping and BAGMANE constituent lookup.
    """
    return SecurityMasterService.audit_nifty500_security_master()

@router.get("/repair/manifest")
async def get_repair_manifest(lookback_years: int = Query(default=5, ge=1, le=5)) -> Dict[str, Any]:
    """
    Generates missing data repair manifest in 100% Dry-Run mode (0 database mutations).
    """
    return DataRepairPlannerService.generate_repair_manifest(lookback_years=lookback_years)

@router.post("/repair/execute")
async def execute_repair_batch(max_symbols: int = Query(default=10, ge=1, le=500)) -> Dict[str, Any]:
    """
    Executes a controlled batch repair for approved manifest items.
    Enforces compliance preflight, rate limits, and safety invariants.
    """
    manifest = DataRepairPlannerService.generate_repair_manifest()
    return DataRepairPlannerService.execute_controlled_ingestion_batch(manifest=manifest, max_symbols=max_symbols)

@router.get("/readiness")
async def get_signal_readiness_diagnostic() -> Dict[str, Any]:
    """
    Returns signal engine readiness diagnostics for SHORT, SWING, and LONG timeframes.
    """
    master_audit = SecurityMasterService.audit_nifty500_security_master()
    compliance = ProviderComplianceService.validate_ingestion_preflight()

    return {
        "readiness_summary": {
            "SHORT": "BLOCKED_DATA_GATE" if not compliance.get("can_ingest_real_data") else "READY",
            "SWING": "BLOCKED_DATA_GATE" if not compliance.get("can_ingest_real_data") else "READY",
            "LONG": "BLOCKED_DATA_GATE" if not compliance.get("can_ingest_real_data") else "READY"
        },
        "target_universe_size": master_audit.get("total_canonical_symbols", 500),
        "mapped_symbols": master_audit.get("mapped_symbols", 500),
        "can_ingest_real_data": compliance.get("can_ingest_real_data", False),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
