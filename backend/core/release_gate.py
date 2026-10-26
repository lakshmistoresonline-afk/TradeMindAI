"""
================================================================================
TradeMindAI: Fail-Closed Release Gate (REL-02 & TM-08)
================================================================================
Centralizes the final release decision so missing, stale, failed, or mismatched
evidence cannot produce a READY result. Deterministic and independent.
================================================================================
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

@dataclass(frozen=True)
class Evidence:
    name: str
    passed: bool
    git_sha: str
    generated_at: str
    artifact_path: Optional[str] = None
    artifact_sha256: Optional[str] = None
    details: str = ""

@dataclass(frozen=True)
class ReleasePolicy:
    required_evidence: tuple[str, ...]
    maximum_evidence_age: timedelta = timedelta(hours=24)
    require_matching_git_sha: bool = True

@dataclass(frozen=True)
class ReleaseDecision:
    status: str
    git_sha: str
    evaluated_at: str
    blockers: tuple[str, ...]
    evidence: tuple[dict[str, Any], ...]


class ReleaseGateEvaluator:
    def __init__(self, policy: ReleasePolicy, current_git_sha: str):
        self.policy = policy
        self.current_git_sha = current_git_sha.strip().lower()

    def evaluate(self, evidence_items: Iterable[Evidence], evaluated_at: Optional[datetime] = None) -> ReleaseDecision:
        now = evaluated_at or datetime.now(timezone.utc)
        blockers: list[str] = []
        collected_evidence: list[dict[str, Any]] = []
        seen_names: set[str] = set()

        for ev in evidence_items:
            seen_names.add(ev.name)
            collected_evidence.append(asdict(ev))

            # Validate git SHA
            if self.policy.require_matching_git_sha and ev.git_sha.strip().lower() != self.current_git_sha:
                blockers.append(f"Evidence '{ev.name}' Git SHA mismatch (expected {self.current_git_sha}, got {ev.git_sha})")

            # Validate evidence age
            try:
                ev_time = datetime.fromisoformat(ev.generated_at.replace("Z", "+00:00"))
                if now - ev_time > self.policy.maximum_evidence_age:
                    blockers.append(f"Evidence '{ev.name}' has expired (generated at {ev.generated_at})")
            except Exception:
                blockers.append(f"Evidence '{ev.name}' has invalid timestamp format '{ev.generated_at}'")

            # Validate passed status
            if not ev.passed:
                blockers.append(f"Evidence '{ev.name}' failed: {ev.details}")

            # Validate artifact if specified
            if ev.artifact_path:
                p = Path(ev.artifact_path)
                if not p.exists():
                    blockers.append(f"Evidence '{ev.name}' artifact missing at {ev.artifact_path}")
                elif ev.artifact_sha256:
                    sha = hashlib.sha256(p.read_bytes()).hexdigest()
                    if sha.lower() != ev.artifact_sha256.lower():
                        blockers.append(f"Evidence '{ev.name}' artifact SHA256 mismatch")

        # Check required evidence coverage
        for req in self.policy.required_evidence:
            if req not in seen_names:
                blockers.append(f"Missing required evidence item: '{req}'")

        status = "READY" if not blockers else "NOT_READY"

        return ReleaseDecision(
            status=status,
            git_sha=self.current_git_sha,
            evaluated_at=now.isoformat(),
            blockers=tuple(blockers),
            evidence=tuple(collected_evidence)
        )
