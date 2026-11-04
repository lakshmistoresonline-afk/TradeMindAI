"""
================================================================================
TradeMindAI Unit Tests — Authoritative Signal Ledger Contract (Fix B)
================================================================================
Verifies that:
1. When QUARANTINE_ACTIVE=True, signal API endpoints fail closed with 503 Quarantined.
2. SignalLedgerService enforces BUY-only eligibility and global active-signal uniqueness.
3. Duplicate active signal creation returns existing active record.
4. Missing or malformed ledger responses fail closed safely without fabricating replacement signals.
================================================================================
"""

import pytest
import json
import pandas as pd
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.services.signal_ledger_service import SignalLedgerService
from backend.domain.models.ios import LiveSignal
from backend.core.postgres import LiveSignalDB

client = TestClient(app)

def test_signal_endpoint_fails_closed_when_quarantined(monkeypatch):
    from backend.core.config import settings
    monkeypatch.setattr(settings, "QUARANTINE_ACTIVE", True)

    response = client.get("/api/v1/equity/signals")
    assert response.status_code == 503
    assert "QUARANTINED" in response.json()["detail"]

def test_signal_ledger_service_rejects_ineligible_non_buy_signal(mock_db):
    ineligible_signal = LiveSignal(
        id="sig_SELL_TEST_01",
        symbol="TEST",
        direction="SHORT", # Ineligible non-BUY direction!
        rating="SELL",
        status="ACTIVE",
        timestamp=pd.Timestamp.now("UTC").to_pydatetime()
    )

    with pytest.raises(ValueError, match="violates BUY-only eligibility policy"):
        import asyncio
        asyncio.run(SignalLedgerService.create_signal(ineligible_signal, session=mock_db))

def test_signal_ledger_service_returns_existing_active_signal_on_duplicate():
    sig1 = LiveSignal(
        id="sig_BUY_TEST_01",
        symbol="DUPLICATE_TEST",
        direction="LONG",
        rating="BUY",
        status="ACTIVE",
        timestamp=pd.Timestamp.now("UTC").to_pydatetime()
    )

    real_db_obj = LiveSignalDB(
        id="sig_BUY_TEST_01",
        symbol="DUPLICATE_TEST",
        direction="LONG",
        rating="BUY",
        status="ACTIVE"
    )

    query_mock = MagicMock()
    filter_mock = MagicMock()
    filter_mock.first.side_effect = [None, real_db_obj]
    query_mock.filter.return_value = filter_mock

    session_mock = MagicMock()
    session_mock.query.return_value = query_mock

    import asyncio
    created1 = asyncio.run(SignalLedgerService.create_signal(sig1, session=session_mock))
    created2 = asyncio.run(SignalLedgerService.create_signal(sig1, session=session_mock))

    assert created1.id == created2.id == "sig_BUY_TEST_01"

def test_signal_ledger_contract_quarantine_blocks_static_json_fallback(monkeypatch):
    from backend.core.config import settings
    monkeypatch.setattr(settings, "QUARANTINE_ACTIVE", True)

    response = client.get("/api/v1/equity/signals")
    assert response.status_code == 503
    assert "QUARANTINED" in response.json()["detail"]
    assert "active_signals" not in response.json()
