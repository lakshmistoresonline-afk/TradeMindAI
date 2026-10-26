import os
import json
import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from backend.core.data_certification import MarketDataCertifier, CertificationPolicy, PriceRecord
from backend.core.release_gate import ReleaseGateEvaluator, ReleasePolicy, Evidence, ReleaseDecision
from backend.core.config import Settings

def test_adversarial_1_empty_expected_universe():
    certifier = MarketDataCertifier(CertificationPolicy(require_non_empty_universe=True))
    res = certifier.certify([], [])
    assert res.certified is False
    assert any("empty" in f.lower() for f in res.failures)

def test_adversarial_2_missing_expected_symbol():
    now = datetime.now(timezone.utc)
    certifier = MarketDataCertifier(CertificationPolicy(minimum_records_per_symbol=1))
    rec = PriceRecord("RELIANCE", now, 100, 105, 95, 102, 1000, "YFINANCE_AUTHENTIC")
    res = certifier.certify([rec], ["RELIANCE", "TCS"], current_time=now)
    assert res.certified is False
    assert "TCS" in res.missing_symbols

def test_adversarial_3_insufficient_history():
    now = datetime.now(timezone.utc)
    certifier = MarketDataCertifier(CertificationPolicy(minimum_records_per_symbol=5))
    rec = PriceRecord("RELIANCE", now, 100, 105, 95, 102, 1000, "YFINANCE_AUTHENTIC")
    res = certifier.certify([rec], ["RELIANCE"], current_time=now)
    assert res.certified is False
    assert any("insufficient" in f.lower() for f in res.failures)

def test_adversarial_5_duplicate_symbol_timestamp():
    now = datetime.now(timezone.utc)
    certifier = MarketDataCertifier(CertificationPolicy(minimum_records_per_symbol=1))
    recs = [
        PriceRecord("RELIANCE", now, 100, 105, 95, 102, 1000, "YFINANCE_AUTHENTIC"),
        PriceRecord("RELIANCE", now, 101, 106, 96, 103, 1100, "YFINANCE_AUTHENTIC")
    ]
    res = certifier.certify(recs, ["RELIANCE"], current_time=now)
    assert res.certified is False
    assert any("duplicate" in f.lower() for f in res.failures)

def test_adversarial_6_naive_and_tz_timestamps():
    now_naive = datetime.now() # naive
    certifier = MarketDataCertifier(CertificationPolicy(minimum_records_per_symbol=1))
    rec = PriceRecord("RELIANCE", now_naive, 100, 105, 95, 102, 1000, "YFINANCE_AUTHENTIC")
    res = certifier.certify([rec], ["RELIANCE"], current_time=now_naive.replace(tzinfo=timezone.utc))
    assert res.certified is True

def test_adversarial_7_future_dated_timestamp():
    now = datetime.now(timezone.utc)
    future = now + timedelta(hours=1)
    certifier = MarketDataCertifier(CertificationPolicy(minimum_records_per_symbol=1))
    rec = PriceRecord("RELIANCE", future, 100, 105, 95, 102, 1000, "YFINANCE_AUTHENTIC")
    res = certifier.certify([rec], ["RELIANCE"], current_time=now)
    assert res.certified is False
    assert any("future" in f.lower() for f in res.failures)

def test_adversarial_8_invalid_ohlc_and_prices():
    now = datetime.now(timezone.utc)
    certifier = MarketDataCertifier(CertificationPolicy(minimum_records_per_symbol=1))
    # Low > High
    rec = PriceRecord("RELIANCE", now, 100, 90, 95, 102, 1000, "YFINANCE_AUTHENTIC")
    res = certifier.certify([rec], ["RELIANCE"], current_time=now)
    assert res.certified is False

def test_adversarial_9_untrusted_provenance():
    now = datetime.now(timezone.utc)
    certifier = MarketDataCertifier(CertificationPolicy(minimum_records_per_symbol=1))
    rec = PriceRecord("RELIANCE", now, 100, 105, 95, 102, 1000, "UNKNOWN_SOURCE")
    res = certifier.certify([rec], ["RELIANCE"], current_time=now)
    assert res.certified is False
    assert any("untrusted" in f.lower() for f in res.failures)

def test_adversarial_10_duplicate_evidence_names():
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("tests",))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)
    ev1 = Evidence(name="tests", passed=True, git_sha=sha, generated_at=now.isoformat() + "Z")
    ev2 = Evidence(name="tests", passed=True, git_sha=sha, generated_at=now.isoformat() + "Z")
    decision = evaluator.evaluate([ev1, ev2], evaluated_at=now)
    assert decision.status == "NOT_READY"
    assert any("Duplicate evidence name" in b for b in decision.blockers)

def test_adversarial_11_invalid_git_sha():
    with pytest.raises(ValueError, match="Invalid reference Git SHA format"):
        ReleaseGateEvaluator(ReleasePolicy(required_evidence=("tests",)), current_git_sha="not-a-sha")

def test_adversarial_13_missing_artifact(tmp_path):
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("tests",), evidence_root=str(tmp_path))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)
    missing_art = tmp_path / "nonexistent.json"
    ev = Evidence(name="tests", passed=True, git_sha=sha, generated_at=now.isoformat() + "Z", artifact_path=str(missing_art), artifact_sha256="abc123sha256")
    decision = evaluator.evaluate([ev], evaluated_at=now)
    assert decision.status == "NOT_READY"
    assert any("missing or unreadable" in b for b in decision.blockers)

def test_adversarial_14_artifact_hash_mismatch(tmp_path):
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("tests",), evidence_root=str(tmp_path))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)
    art = tmp_path / "art.json"
    art.write_text("content")
    ev = Evidence(name="tests", passed=True, git_sha=sha, generated_at=now.isoformat() + "Z", artifact_path=str(art), artifact_sha256="wronghash")
    decision = evaluator.evaluate([ev], evaluated_at=now)
    assert decision.status == "NOT_READY"
    assert any("hash mismatch" in b for b in decision.blockers)

def test_adversarial_15_missing_mandatory_evidence():
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("security_scan",))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)
    decision = evaluator.evaluate([], evaluated_at=now)
    assert decision.status == "NOT_READY"
    assert any("Evidence collection is empty" in b or "Missing required evidence item" in b for b in decision.blockers)

def test_adversarial_empty_required_evidence_policy():
    with pytest.raises(ValueError, match="Release policy cannot have empty required_evidence"):
        ReleasePolicy(required_evidence=())

def test_adversarial_naive_evidence_timestamp():
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("tests",))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)
    # Naive timestamp string without offset
    ev = Evidence(name="tests", passed=True, git_sha=sha, generated_at="2026-10-26T12:00:00")
    decision = evaluator.evaluate([ev], evaluated_at=now)
    assert decision.status == "NOT_READY"
    assert any("timezone-naive timestamp format" in b for b in decision.blockers)

def test_adversarial_18_real_trading_true_fails():
    with pytest.raises(ValueError):
        Settings(REAL_TRADING=True)

def test_atomic_write_decision(tmp_path):
    now = datetime.now(timezone.utc)
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    policy = ReleasePolicy(required_evidence=("tests",))
    evaluator = ReleaseGateEvaluator(policy, current_git_sha=sha)
    ev = Evidence(name="tests", passed=True, git_sha=sha, generated_at=now.isoformat())
    decision = evaluator.evaluate([ev], evaluated_at=now)
    out_file = tmp_path / "decision.json"
    evaluator.write_decision_atomic(decision, out_file)
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["status"] == "READY"
