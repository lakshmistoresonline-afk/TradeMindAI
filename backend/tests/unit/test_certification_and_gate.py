import pytest
import hashlib
from datetime import datetime, timedelta, timezone
from backend.core.data_certification import MarketDataCertifier, CertificationPolicy, PriceRecord
from backend.core.release_gate import ReleaseGateEvaluator, ReleasePolicy, Evidence
from backend.core.config import Settings

def test_market_data_certifier_valid_record():
    now = datetime.now(timezone.utc)
    policy = CertificationPolicy(minimum_records_per_symbol=1, maximum_age=timedelta(hours=1))
    certifier = MarketDataCertifier(policy)

    rec = PriceRecord(
        symbol="RELIANCE",
        timestamp=now,
        open=100.0,
        high=105.0,
        low=95.0,
        close=102.0,
        volume=50000.0,
        source="YFINANCE_AUTHENTIC"
    )
    result = certifier.certify([rec], ["RELIANCE"], current_time=now)
    assert result.certified is True
    assert result.missing_symbols == ()

def test_market_data_certifier_missing_symbol():
    now = datetime.now(timezone.utc)
    policy = CertificationPolicy(minimum_records_per_symbol=1, maximum_age=timedelta(hours=1))
    certifier = MarketDataCertifier(policy)

    rec = PriceRecord(
        symbol="RELIANCE",
        timestamp=now,
        open=100.0,
        high=105.0,
        low=95.0,
        close=102.0,
        volume=50000.0,
        source="YFINANCE_AUTHENTIC"
    )
    result = certifier.certify([rec], ["RELIANCE", "TCS"], current_time=now)
    assert result.certified is False
    assert "TCS" in result.missing_symbols

def test_market_data_certifier_invalid_ohlc():
    now = datetime.now(timezone.utc)
    policy = CertificationPolicy(minimum_records_per_symbol=1, maximum_age=timedelta(hours=1))
    certifier = MarketDataCertifier(policy)

    # Low > High invalid range
    rec = PriceRecord(
        symbol="RELIANCE",
        timestamp=now,
        open=100.0,
        high=90.0,
        low=95.0,
        close=102.0,
        volume=50000.0,
        source="YFINANCE_AUTHENTIC"
    )
    result = certifier.certify([rec], ["RELIANCE"], current_time=now)
    assert result.certified is False

def test_release_gate_evaluator_success(tmp_path):
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("unit_tests", "security_scan"), evidence_root=str(tmp_path))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)

    art1 = tmp_path / "unit_tests.log"
    art1.write_text("unit_tests_ok")
    sha1 = hashlib.sha256(art1.read_bytes()).hexdigest()

    art2 = tmp_path / "security_scan.log"
    art2.write_text("security_scan_ok")
    sha2 = hashlib.sha256(art2.read_bytes()).hexdigest()

    ev1 = Evidence(name="unit_tests", passed=True, git_sha=sha, generated_at=now.isoformat(), artifact_path=str(art1), artifact_sha256=sha1)
    ev2 = Evidence(name="security_scan", passed=True, git_sha=sha, generated_at=now.isoformat(), artifact_path=str(art2), artifact_sha256=sha2)

    decision = evaluator.evaluate([ev1, ev2], evaluated_at=now)
    assert decision.status == "READY"
    assert decision.blockers == ()

def test_release_gate_evaluator_git_sha_mismatch(tmp_path):
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("unit_tests",), evidence_root=str(tmp_path))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)

    art1 = tmp_path / "unit_tests.log"
    art1.write_text("unit_tests_ok")
    sha1 = hashlib.sha256(art1.read_bytes()).hexdigest()

    ev1 = Evidence(name="unit_tests", passed=True, git_sha="2bd7478bce2df25fd9bc224a956eaad11e6ff539", generated_at=now.isoformat(), artifact_path=str(art1), artifact_sha256=sha1)

    decision = evaluator.evaluate([ev1], evaluated_at=now)
    assert decision.status == "NOT_READY"
    assert any("Git SHA mismatch" in b for b in decision.blockers)

def test_real_trading_true_fails():
    with pytest.raises(ValueError):
        Settings(REAL_TRADING=True)
