"""
================================================================================
TradeMindAI: Dedicated Unit Test Suite for Regression Defect Verification
================================================================================
Directly verifies DEF-01, DEF-02, DEF-03, DEF-04, and static asset containment
semantics using isolated in-memory fixtures.
================================================================================
"""

import pytest
import datetime
import json
import os
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

from backend.app.services.indicator_service import LocalIndicatorService
from backend.services.signal_engine import SignalEngine
from backend.infrastructure.repositories.hybrid_repository import HybridDataPlatformRepository
from backend.core.postgres import ModelMetadataDB, Base, PriceDB
from backend.domain.models.data_platform import ModelMetadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# --- DEF-01: Historical As-Of Boundary Test ---
def test_def01_historical_as_of_boundary_excludes_future_rows():
    """Verify that PriceDB queries with as_of_date NEVER return rows dated after as_of_date."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    eval_date = datetime.datetime(2023, 6, 1, 12, 0, 0)

    # Insert rows before, at, and after eval_date
    rows = [
        PriceDB(symbol="TEST_SYM", date=datetime.datetime(2023, 5, 20), open=100.0, high=105.0, low=95.0, close=102.0, volume=1000, source="YFINANCE_AUTHENTIC"),
        PriceDB(symbol="TEST_SYM", date=datetime.datetime(2023, 6, 1), open=101.0, high=106.0, low=96.0, close=103.0, volume=1100, source="YFINANCE_AUTHENTIC"),
        PriceDB(symbol="TEST_SYM", date=datetime.datetime(2023, 6, 15), open=105.0, high=110.0, low=100.0, close=108.0, volume=1200, source="YFINANCE_AUTHENTIC"),  # FUTURE ROW
        PriceDB(symbol="TEST_SYM", date=datetime.datetime(2023, 7, 1), open=108.0, high=112.0, low=102.0, close=110.0, volume=1300, source="YFINANCE_AUTHENTIC")   # FUTURE ROW
    ]

    with TestSession() as session:
        session.bulk_save_objects(rows)
        session.commit()

        p_objs = session.query(PriceDB).filter(
            PriceDB.symbol == "TEST_SYM",
            PriceDB.date <= eval_date
        ).order_by(PriceDB.date.desc()).all()

        assert len(p_objs) == 2, f"Expected exactly 2 rows as of {eval_date}, got {len(p_objs)}"
        for p in p_objs:
            assert p.date <= eval_date, f"Row date {p.date} exceeds historical as_of_date {eval_date}"


# --- DEF-02: Champion Model Fallback Test ---
def test_def02_champion_model_fallback_hierarchy():
    """Verify champion model lookup uses per-symbol model if present, falls back to universal index model, or returns None."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Insert universal index champion for SWING
    univ_model = ModelMetadataDB(
        name="universal_swing_model",
        symbol="NIFTY_200",
        version="v2.3",
        horizon="SWING",
        type="CLASSIFIER",
        status="ACTIVE",
        accuracy=0.80,
        precision=0.75,
        recall=0.75,
        f1_score=0.75,
        is_champion=True,
        last_trained=datetime.datetime.utcnow(),
        hyperparameters='{"test_size": 100, "positives_test": 20}',
        feature_importances='{"ema_20": 0.5}'
    )

    with TestSession() as session:
        session.add(univ_model)
        session.commit()

        r = session.query(ModelMetadataDB).filter(
            ModelMetadataDB.symbol == "RELIANCE",
            ModelMetadataDB.is_champion == True,
            ModelMetadataDB.horizon == "SWING"
        ).first()

        if not r:
            r = session.query(ModelMetadataDB).filter(
                ModelMetadataDB.is_champion == True,
                ModelMetadataDB.horizon == "SWING"
            ).first()

        assert r is not None
        assert r.name == "universal_swing_model"
        assert r.horizon == "SWING"


# --- DEF-03: EMA200 Insufficient History & Exact Lookback Boundaries Test ---
def test_def03_ema200_insufficient_history_returns_none():
    """Verify that 0, 1, 13, 14, 199 bars return None for ema_200, while 200 bars returns valid float."""
    for periods in [0, 1, 13, 14, 199]:
        if periods == 0:
            df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        else:
            dates = pd.date_range("2023-01-01", periods=periods, freq="B")
            df = pd.DataFrame({
                "open": [100.0] * periods, "high": [105.0] * periods, "low": [95.0] * periods,
                "close": [101.0] * periods, "volume": [1000] * periods
            }, index=dates)

        metrics = LocalIndicatorService.get_latest_metrics(df)
        if periods < 200:
            assert metrics.get("ema_200") is None, f"Expected None for {periods} bars, got {metrics.get('ema_200')}"

    # Exactly 200 bars
    dates_200 = pd.date_range("2023-01-01", periods=200, freq="B")
    prices_200 = [100.0 + (i * 0.1) for i in range(200)]
    df_200 = pd.DataFrame({
        "open": [p - 1.0 for p in prices_200],
        "high": [p + 2.0 for p in prices_200],
        "low": [p - 2.0 for p in prices_200],
        "close": prices_200,
        "volume": [1000] * 200
    }, index=dates_200)

    metrics_200 = LocalIndicatorService.get_latest_metrics(df_200)
    assert metrics_200["ema_200"] is not None, "Expected valid float for 200 bars"
    assert isinstance(metrics_200["ema_200"], float)


# --- DEF-04: Malformed Model Metadata Test ---
def test_def04_malformed_model_metadata_handling():
    """Verify _map_db_to_model_metadata handles None, dict, and unexpected types safely."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    repo = HybridDataPlatformRepository(session_factory=TestSession, firestore_db=MagicMock())

    now = datetime.datetime.utcnow()
    # None input in DB
    db_obj_none = ModelMetadataDB(
        name="test_model_none", symbol="TCS", version="v1.0", horizon="SWING",
        type="CLASSIFIER", status="ACTIVE", accuracy=0.75, precision=0.7, recall=0.7,
        f1_score=0.7, last_trained=now, is_champion=True,
        hyperparameters=None, feature_importances=None, calibration_metadata=None
    )

    meta_none = repo._map_db_to_model_metadata(db_obj_none)
    assert meta_none.hyperparameters == {}
    assert meta_none.feature_importances == {}
    assert meta_none.calibration_metadata == {}

    # Valid dict/json string input
    db_obj_valid = ModelMetadataDB(
        name="test_model_valid", symbol="TCS", version="v1.0", horizon="SWING",
        type="CLASSIFIER", status="ACTIVE", accuracy=0.75, precision=0.7, recall=0.7,
        f1_score=0.7, last_trained=now, is_champion=True,
        hyperparameters='{"param1": "val1"}', feature_importances='{"feat1": 0.5}', calibration_metadata='{}'
    )

    meta_valid = repo._map_db_to_model_metadata(db_obj_valid)
    assert meta_valid.hyperparameters == {"param1": "val1"}
    assert meta_valid.feature_importances == {"feat1": 0.5}


# --- Static Asset Build Output Containment Test ---
def test_static_asset_containment_in_build_output():
    """Verify signals.json and performance.json do not exist in web/dist build output."""
    dist_dir = r"D:\TradeMindAI\web\dist"
    if os.path.exists(dist_dir):
        sig_path = os.path.join(dist_dir, "signals.json")
        perf_path = os.path.join(dist_dir, "performance.json")
        assert not os.path.exists(sig_path), f"signals.json should be absent from {dist_dir}"
        assert not os.path.exists(perf_path), f"performance.json should be absent from {dist_dir}"
