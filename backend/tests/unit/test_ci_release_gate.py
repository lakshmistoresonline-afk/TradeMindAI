import os
import sys
import json
import pytest
import subprocess
from pathlib import Path
from datetime import datetime, timezone

def test_ci_release_gate_cli_success(tmp_path):
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    ev_dir = tmp_path / "evidence"
    ev_dir.mkdir()
    out_file = tmp_path / "decision.json"

    now = datetime.now(timezone.utc).isoformat()
    (ev_dir / "backend_tests.json").write_text(json.dumps({
        "name": "backend_tests", "passed": True, "git_sha": sha, "generated_at": now
    }))

    script_path = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "ci_release_gate.py"
    cmd = [
        sys.executable, str(script_path),
        "--git-sha", sha,
        "--evidence-dir", str(ev_dir),
        "--output-path", str(out_file),
        "--required-evidence", "backend_tests"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert "APPROVED" in res.stdout
    assert out_file.exists()
    decision = json.loads(out_file.read_text())
    assert decision["status"] == "READY"

def test_ci_release_gate_cli_string_passed_fails(tmp_path):
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    ev_dir = tmp_path / "string_passed_evidence"
    ev_dir.mkdir()
    out_file = tmp_path / "decision.json"

    now = datetime.now(timezone.utc).isoformat()
    (ev_dir / "backend_tests.json").write_text(json.dumps({
        "name": "backend_tests", "passed": "false", "git_sha": sha, "generated_at": now
    }))

    script_path = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "ci_release_gate.py"
    cmd = [
        sys.executable, str(script_path),
        "--git-sha", sha,
        "--evidence-dir", str(ev_dir),
        "--output-path", str(out_file),
        "--required-evidence", "backend_tests"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "must be a boolean" in res.stdout or "DENIED" in res.stdout

def test_ci_release_gate_cli_missing_evidence_fails(tmp_path):
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    ev_dir = tmp_path / "empty_evidence"
    ev_dir.mkdir()
    out_file = tmp_path / "decision.json"

    script_path = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "ci_release_gate.py"
    cmd = [
        sys.executable, str(script_path),
        "--git-sha", sha,
        "--evidence-dir", str(ev_dir),
        "--output-path", str(out_file),
        "--required-evidence", "backend_tests"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "FATAL: No evidence JSON files found" in res.stdout or "DENIED" in res.stdout

def test_ci_release_gate_cli_malformed_json_fails(tmp_path):
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    ev_dir = tmp_path / "corrupt_evidence"
    ev_dir.mkdir()
    out_file = tmp_path / "decision.json"

    (ev_dir / "backend_tests.json").write_text("NOT_VALID_JSON{")

    script_path = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "ci_release_gate.py"
    cmd = [
        sys.executable, str(script_path),
        "--git-sha", sha,
        "--evidence-dir", str(ev_dir),
        "--output-path", str(out_file),
        "--required-evidence", "backend_tests"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "Malformed JSON" in res.stdout or "DENIED" in res.stdout

def test_ci_release_gate_cli_unexpected_evidence_name_fails(tmp_path):
    sha = "1bd7478bce2df25fd9bc224a956eaad11e6ff539"
    ev_dir = tmp_path / "unexpected_evidence"
    ev_dir.mkdir()
    out_file = tmp_path / "decision.json"

    now = datetime.now(timezone.utc).isoformat()
    (ev_dir / "unrelated.json").write_text(json.dumps({
        "name": "unrelated_check", "passed": True, "git_sha": sha, "generated_at": now
    }))

    script_path = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "ci_release_gate.py"
    cmd = [
        sys.executable, str(script_path),
        "--git-sha", sha,
        "--evidence-dir", str(ev_dir),
        "--output-path", str(out_file),
        "--required-evidence", "backend_tests"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "Unexpected evidence name" in res.stdout or "DENIED" in res.stdout

def test_workflows_contain_full_mandatory_release_gate_policy():
    root = Path(__file__).resolve().parent.parent.parent.parent
    backend_wf = (root / ".github" / "workflows" / "deploy-backend.yml").read_text()
    frontend_wf = (root / ".github" / "workflows" / "deploy-frontend.yml").read_text()

    expected_req = "backend_tests,frontend_lint,frontend_tests,frontend_build"
    assert f'--required-evidence "{expected_req}"' in backend_wf
    assert f'--required-evidence "{expected_req}"' in frontend_wf

    bg_gate_idx = backend_wf.index("Run Mandatory Full CI Release Gate")
    bg_deploy_idx = backend_wf.index("gcloud run deploy")
    assert bg_gate_idx < bg_deploy_idx

    fe_gate_idx = frontend_wf.index("Run Mandatory Full CI Release Gate")
    fe_deploy_idx = frontend_wf.index("Deploy to Firebase")
    assert fe_gate_idx < fe_deploy_idx
