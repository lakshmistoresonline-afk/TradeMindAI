"""
================================================================================
TradeMindAI: Hardened Fail-Closed Release Gate (REL-02 & TM-08)
================================================================================
Centralizes the final release decision so missing, stale, failed, naive-timestamp,
or unhashed evidence cannot produce a READY result. Deterministic and independent.
================================================================================
"""

from __future__ import annotations
import os
import hashlib
import json
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

GIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)

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
    maximum_future_skew: timedelta = timedelta(minutes=2)
    require_matching_git_sha: bool = True
    evidence_root: Optional[str] = None

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
        self.current_git_sha = (current_git_sha or "").strip().lower()
        if not GIT_SHA_PATTERN.match(self.current_git_sha):
            raise ValueError(f"Invalid reference Git SHA format: '{current_git_sha}'")

    def _normalize_timestamp(self, ts_str: str) -> Optional[datetime]:
        if not isinstance(ts_str, str):
            return None
        # Reject naive timestamp strings lacking explicit timezone offset (Z, +, or offset dash)
        has_tz = "Z" in ts_str or "+" in ts_str[10:] or (("-" in ts_str[10:]) and not ts_str.endswith("Z"))
        if not has_tz:
            return None
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                return None
            return dt.astimezone(timezone.utc)
        except Exception:
            return None

    def evaluate(self, evidence_items: Iterable[Evidence], evaluated_at: Optional[datetime] = None) -> ReleaseDecision:
        now = evaluated_at or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)

        blockers: list[str] = []
        collected_evidence: list[dict[str, Any]] = []
        seen_names: set[str] = set()

        root_path = Path(self.policy.evidence_root).resolve() if self.policy.evidence_root else Path.cwd().resolve()

        try:
            if not self.policy.required_evidence:
                blockers.append("CRITICAL RELEASE GATE FAILURE: Release policy defines zero required evidence items.")

            for ev in evidence_items:
                if not ev or not ev.name:
                    blockers.append("Encountered null or malformed evidence entry.")
                    continue

                if ev.name in seen_names:
                    blockers.append(f"Duplicate evidence name detected: '{ev.name}'")
                    continue
                seen_names.add(ev.name)
                collected_evidence.append(asdict(ev))

                # Validate evidence Git SHA format and match
                ev_sha = (ev.git_sha or "").strip().lower()
                if not GIT_SHA_PATTERN.match(ev_sha):
                    blockers.append(f"Evidence '{ev.name}' has malformed Git SHA '{ev.git_sha}'")
                elif self.policy.require_matching_git_sha and ev_sha != self.current_git_sha:
                    blockers.append(f"Evidence '{ev.name}' Git SHA mismatch (expected {self.current_git_sha}, got {ev.git_sha})")

                # Validate timezone-aware timestamp and age / future skew
                ev_time = self._normalize_timestamp(ev.generated_at)
                if not ev_time:
                    blockers.append(f"Evidence '{ev.name}' has invalid or timezone-naive timestamp format '{ev.generated_at}'")
                else:
                    if ev_time > now + self.policy.maximum_future_skew:
                        blockers.append(f"Evidence '{ev.name}' timestamp is future-dated ({ev.generated_at})")
                    if now - ev_time > self.policy.maximum_evidence_age:
                        blockers.append(f"Evidence '{ev.name}' has expired (generated at {ev.generated_at})")

                # Validate passed status
                if not ev.passed:
                    blockers.append(f"Evidence '{ev.name}' marked failed: {ev.details}")

                # Validate artifact integrity & mandatory hash
                if ev.artifact_path:
                    if not ev.artifact_sha256 or not ev.artifact_sha256.strip():
                        blockers.append(f"Evidence '{ev.name}' specifies artifact_path but lacks mandatory artifact_sha256 hash.")
                    else:
                        try:
                            art_path = Path(ev.artifact_path).resolve()
                            if not art_path.is_relative_to(root_path):
                                blockers.append(f"Evidence '{ev.name}' artifact path escapes evidence root: {ev.artifact_path}")
                            elif not art_path.exists() or not art_path.is_file():
                                blockers.append(f"Evidence '{ev.name}' artifact missing or unreadable at {ev.artifact_path}")
                            else:
                                file_bytes = art_path.read_bytes()
                                actual_sha = hashlib.sha256(file_bytes).hexdigest()
                                if actual_sha.lower() != ev.artifact_sha256.strip().lower():
                                    blockers.append(f"Evidence '{ev.name}' artifact SHA256 hash mismatch")
                        except Exception as ex:
                            blockers.append(f"Evidence '{ev.name}' artifact verification error: {ex}")

            # Check required evidence coverage
            for req in self.policy.required_evidence:
                if req not in seen_names:
                    blockers.append(f"Missing required evidence item: '{req}'")

        except Exception as e:
            blockers.append(f"CRITICAL RELEASE GATE EXCEPTION: {e}")

        status = "READY" if not blockers else "NOT_READY"

        return ReleaseDecision(
            status=status,
            git_sha=self.current_git_sha,
            evaluated_at=now.isoformat(),
            blockers=tuple(blockers),
            evidence=tuple(collected_evidence)
        )

    def write_decision_atomic(self, decision: ReleaseDecision, output_path: Path) -> None:
        """
        Writes the release decision atomically using a temporary file collision-safe replacement.
        """
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

        fd, temp_path = tempfile.mkstemp(dir=out.parent, text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(asdict(decision), f, indent=2)
            os.replace(temp_path, out)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
