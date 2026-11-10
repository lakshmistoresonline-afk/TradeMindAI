"""
================================================================================
TradeMindAI Phase 4: Automated Test Suite for Multi-Provider Market Data Integration
================================================================================
Tests FYERS & Angel One adapters, compliance registry, security master, repair planner,
reconciliation engine, and absolute safety invariants.
================================================================================
"""

import pytest
import datetime
from datetime import timezone
from backend.services.providers.fyers_adapter import FYERSProviderAdapter
from backend.services.providers.angel_one_adapter import AngelOneProviderAdapter
from backend.services.provider_compliance_service import ProviderComplianceService
from backend.services.security_master_service import SecurityMasterService
from backend.services.data_repair_planner_service import DataRepairPlannerService
from backend.services.data_reconciliation_engine import DataReconciliationEngine
from backend.core.config import settings

@pytest.mark.asyncio
async def test_fyers_adapter_capabilities_and_normalization():
    adapter = FYERSProviderAdapter(client_id="test_client", access_token="test_token")
    caps = adapter.discover_capabilities()
    assert caps["provider"] == "FYERS"
    assert caps["max_lookback_years"] == 5
    assert "5" in caps["supported_timeframes"]

    raw_candles = [
        [1700000000, 2500.0, 2520.0, 2490.0, 2510.0, 15000.0]
    ]
    norm = adapter.normalize_candles(raw_candles, "RELIANCE")
    assert len(norm) == 1
    assert norm[0]["symbol"] == "RELIANCE"
    assert norm[0]["close"] == 2510.0
    assert norm[0]["provider"] == "FYERS"

@pytest.mark.asyncio
async def test_angel_one_adapter_capabilities_and_normalization():
    adapter = AngelOneProviderAdapter(api_key="test_key", client_code="test_code")
    caps = adapter.discover_capabilities()
    assert caps["provider"] == "ANGEL_ONE"
    assert caps["max_lookback_years"] == 5

    raw_candles = [
        ["2026-03-01T09:15:00+00:00", 2500.0, 2520.0, 2490.0, 2510.0, 15000.0]
    ]
    norm = adapter.normalize_candles(raw_candles, "RELIANCE")
    assert len(norm) == 1
    assert norm[0]["symbol"] == "RELIANCE"
    assert norm[0]["close"] == 2510.0
    assert norm[0]["provider"] == "ANGEL_ONE"

def test_provider_compliance_service_preflight():
    compliance = ProviderComplianceService.validate_ingestion_preflight()
    assert "can_ingest_real_data" in compliance
    assert compliance["dry_run_available"] is True
    assert compliance["fyers"]["provider_name"] == "FYERS"
    assert compliance["angel_one"]["provider_name"] == "ANGEL_ONE"

def test_security_master_audit_and_bagmane_mapping():
    audit = SecurityMasterService.audit_nifty500_security_master()
    assert audit["total_canonical_symbols"] == 500
    assert audit["mapped_symbols"] == 500

    bagmane_info = audit["bagmane_audit_status"]
    assert bagmane_info["symbol"] == "BAGMANE"
    assert bagmane_info["isin"] == "INE002A01018"
    assert bagmane_info["fyers_symbol"] == "NSE:BAGMANE-EQ"
    assert bagmane_info["angel_token"] == "99999"

def test_data_repair_planner_dry_run_manifest():
    manifest = DataRepairPlannerService.generate_repair_manifest(lookback_years=5)
    assert manifest["mode"] == "DRY_RUN"
    assert manifest["target_universe_size"] == 500
    assert manifest["complete_symbols_count"] + manifest["partial_symbols_count"] + manifest["missing_symbols_count"] == 500
    assert isinstance(manifest["repair_manifest"], list)

def test_reconciliation_engine_candle_geometry_validation():
    valid_candle = {"open": 100.0, "high": 105.0, "low": 98.0, "close": 102.0, "volume": 500.0}
    is_valid, err = DataReconciliationEngine.validate_candle_geometry(valid_candle)
    assert is_valid is True
    assert err is None

    invalid_candle = {"open": 100.0, "high": 95.0, "low": 98.0, "close": 102.0, "volume": 500.0}
    is_valid_bad, err_bad = DataReconciliationEngine.validate_candle_geometry(invalid_candle)
    assert is_valid_bad is False
    assert "HIGH_GEOMETRY_VIOLATION" in err_bad

def test_safety_invariants_and_freeze_manifest():
    assert getattr(settings, "REAL_TRADING", True) is False
    assert getattr(settings, "LIVE_EXECUTION_ENABLED", True) is False
    assert getattr(settings, "BROKER_ORDER_EXECUTION_ENABLED", True) is False
    assert getattr(settings, "QUARANTINE_ACTIVE", False) is True
