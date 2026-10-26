"""
================================================================================
TradeMindAI: Hardened Fail-Closed CI/CD Release Gate CLI (SAF-01 & REL-02)
================================================================================
Invokes ReleaseGateEvaluator to enforce mandatory fail-closed release gate
verification in CI/CD deployment workflows.
Exits 0 ONLY when ReleaseDecision status is READY and zero blockers exist;
exits 1 on NOT_READY, malformed evidence, non-boolean values, or failure.
================================================================================
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.core.release_gate import (
    ReleaseGateEvaluator,
    ReleasePolicy,
    Evidence,
    ReleaseDecision
)

def get_current_git_sha() -> str:
    sha = os.getenv("GITHUB_SHA") or os.getenv("GIT_SHA")
    if sha and sha.strip():
        return sha.strip().lower()
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip().lower()
    except Exception:
        return ""

def main():
    parser = argparse.ArgumentParser(description="TradeMindAI CI/CD Release Gate CLI")
    parser.add_argument("--git-sha", type=str, default="", help="Current Git SHA (defaults to GITHUB_SHA or HEAD)")
    parser.add_argument("--evidence-dir", type=str, default="reports/ci_evidence", help="Directory containing evidence JSON files")
    parser.add_argument("--output-path", type=str, default="reports/release_decision.json", help="Path to write ReleaseDecision JSON")
    parser.add_argument("--required-evidence", type=str, default="backend_tests,frontend_lint,frontend_build", help="Comma-separated required evidence names")

    args = parser.parse_args()

    git_sha = (args.git_sha or get_current_git_sha()).strip().lower()
    if not git_sha:
        print("[!] FATAL: Current Git SHA could not be determined.")
        sys.exit(1)

    req_list = [r.strip() for r in args.required_evidence.split(",") if r.strip()]
    if not req_list:
        print("[!] FATAL: At least one required evidence item must be specified.")
        sys.exit(1)

    try:
        policy = ReleasePolicy(required_evidence=tuple(req_list), evidence_root=str(root_dir))
        evaluator = ReleaseGateEvaluator(policy, current_git_sha=git_sha)
    except Exception as e:
        print(f"[!] FATAL: Failed to initialize ReleaseGateEvaluator: {e}")
        sys.exit(1)

    evidence_items = []
    parsing_errors = []
    ev_dir = Path(args.evidence_dir).resolve()

    if not ev_dir.exists() or not ev_dir.is_dir():
        print(f"[!] FATAL: Evidence directory missing or invalid at {ev_dir}")
        sys.exit(1)

    json_files = list(ev_dir.glob("*.json"))
    if not json_files:
        print(f"[!] FATAL: No evidence JSON files found in {ev_dir}")
        sys.exit(1)

    for fpath in json_files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                parsing_errors.append(f"Evidence file {fpath.name} is not a valid JSON object.")
                continue

            name = data.get("name")
            if not name or not isinstance(name, str):
                parsing_errors.append(f"Evidence file {fpath.name} missing 'name' field.")
                continue

            if name not in req_list:
                parsing_errors.append(f"Unexpected evidence name '{name}' in {fpath.name} not in required list.")
                continue

            # STRICT TYPE VALIDATION: passed MUST be an explicit bool, not string "false" or number
            passed_val = data.get("passed")
            if not isinstance(passed_val, bool):
                parsing_errors.append(f"Evidence file {fpath.name} field 'passed' must be a boolean (got {type(passed_val).__name__}: {passed_val}).")
                continue

            git_sha_val = data.get("git_sha")
            if not git_sha_val or not isinstance(git_sha_val, str):
                parsing_errors.append(f"Evidence file {fpath.name} missing or invalid 'git_sha' field.")
                continue

            generated_at_val = data.get("generated_at")
            if not generated_at_val or not isinstance(generated_at_val, str):
                parsing_errors.append(f"Evidence file {fpath.name} missing or invalid 'generated_at' field.")
                continue

            evidence_items.append(Evidence(
                name=name,
                passed=passed_val,
                git_sha=git_sha_val,
                generated_at=generated_at_val,
                artifact_path=data.get("artifact_path"),
                artifact_sha256=data.get("artifact_sha256"),
                details=str(data.get("details", ""))
            ))
        except Exception as e:
            parsing_errors.append(f"Malformed JSON or unreadable evidence file {fpath.name}: {e}")

    # Evaluate decision
    decision = evaluator.evaluate(evidence_items)

    # Append any CLI-level parsing errors to decision blockers
    all_blockers = list(decision.blockers) + parsing_errors
    if parsing_errors:
        final_status = "NOT_READY"
    else:
        final_status = decision.status

    final_decision = ReleaseDecision(
        status=final_status,
        git_sha=decision.git_sha,
        evaluated_at=decision.evaluated_at,
        blockers=tuple(all_blockers),
        evidence=decision.evidence
    )

    out_path = Path(args.output_path).resolve()
    try:
        evaluator.write_decision_atomic(final_decision, out_path)
    except Exception as e:
        print(f"[!] FATAL: Failed to write decision file atomically: {e}")
        sys.exit(1)

    print("\n================================================================================")
    print(f"  TRADEMIND AI CI/CD RELEASE GATE DECISION: {final_decision.status}")
    print("================================================================================")
    print(f"  Git SHA       : {final_decision.git_sha}")
    print(f"  Evaluated At  : {final_decision.evaluated_at}")
    print(f"  Evidence Count: {len(final_decision.evidence)}")

    if final_decision.blockers or final_decision.status != "READY":
        print("\n[!] RELEASE BLOCKERS DETECTED:")
        for b in final_decision.blockers:
            print(f"    - {b}")
        print("\n[FAIL] Release Gate DENIED approval. Failing CI step.")
        sys.exit(1)

    print("\n[SUCCESS] Release Gate APPROVED deployment.")
    sys.exit(0)

if __name__ == "__main__":
    main()
