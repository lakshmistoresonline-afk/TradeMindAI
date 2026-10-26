"""
================================================================================
TradeMindAI: Hardened Market-Data Certification Boundary (DAT-01 & TM-08)
================================================================================
Provides a robust, fail-closed certification boundary that checks expected symbol
coverage, per-symbol minimum valid history, strict source provenance trust policy,
data freshness, duplicate detection, and finite positive price range validation.
================================================================================
"""

from __future__ import annotations
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional, Set, Tuple

TRUSTED_PROVIDERS: Set[str] = {
    "YFINANCE_AUTHENTIC",
    "NSE_CANONICAL",
    "OFFICIAL_FEED",
    "VERIFIED_CANONICAL",
}

@dataclass(frozen=True)
class PriceRecord:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str

@dataclass(frozen=True)
class CertificationPolicy:
    minimum_records_per_symbol: int = 20
    maximum_age: timedelta = timedelta(days=3650) # Historical series tolerance by default
    maximum_future_skew: timedelta = timedelta(minutes=2)
    require_all_expected_symbols: bool = True
    require_non_empty_universe: bool = True

@dataclass(frozen=True)
class CertificationResult:
    certified: bool
    generated_at: str
    expected_symbol_count: int
    observed_symbol_count: int
    missing_symbols: tuple[str, ...]
    failures: tuple[str, ...] = ()


class MarketDataCertifier:
    def __init__(self, policy: CertificationPolicy = CertificationPolicy()):
        self.policy = policy

    def _normalize_timestamp(self, ts: datetime) -> Optional[datetime]:
        if not isinstance(ts, datetime):
            return None
        if ts.tzinfo is None:
            # Assume naive datetime is UTC
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)

    def certify(
        self,
        records: Iterable[PriceRecord],
        expected_symbols: Iterable[str],
        current_time: Optional[datetime] = None,
        is_live_check: bool = False
    ) -> CertificationResult:
        now = current_time or datetime.now(timezone.utc)
        now = self._normalize_timestamp(now) or now

        expected_set = set(s.strip().upper() for s in expected_symbols if s and isinstance(s, str) and s.strip())
        if self.policy.require_non_empty_universe and not expected_set:
            return CertificationResult(
                certified=False,
                generated_at=now.isoformat(),
                expected_symbol_count=0,
                observed_symbol_count=0,
                missing_symbols=tuple(),
                failures=("CRITICAL CERTIFICATION FAILURE: Expected symbol universe is empty.",)
            )

        valid_symbol_counts: dict[str, int] = {}
        seen_timestamps: dict[str, set[datetime]] = {}
        failures: list[str] = []

        for rec in records:
            if not rec or not rec.symbol:
                failures.append("Encountered null or malformed record entry.")
                continue

            sym = rec.symbol.strip().upper()
            if not sym:
                failures.append("Encountered record with blank symbol.")
                continue

            # Timestamp normalization and validation
            norm_ts = self._normalize_timestamp(rec.timestamp)
            if not norm_ts:
                failures.append(f"Malformed timestamp for symbol {sym}")
                continue

            # Duplicate check per symbol
            if sym not in seen_timestamps:
                seen_timestamps[sym] = set()
            if norm_ts in seen_timestamps[sym]:
                failures.append(f"Duplicate record timestamp for symbol {sym} at {norm_ts.isoformat()}")
                continue
            seen_timestamps[sym].add(norm_ts)

            # Future skew check
            if norm_ts > now + self.policy.maximum_future_skew:
                failures.append(f"Future-dated record for symbol {sym} at {norm_ts.isoformat()}")
                continue

            # Live freshness check if applicable
            if is_live_check and (now - norm_ts > timedelta(minutes=30)):
                failures.append(f"Stale live record for symbol {sym} at {norm_ts.isoformat()}")
                continue

            # General historical age check
            if not is_live_check and (now - norm_ts > self.policy.maximum_age):
                failures.append(f"Record too old for symbol {sym} at {norm_ts.isoformat()}")
                continue

            # Price finiteness and positivity
            prices = [rec.open, rec.high, rec.low, rec.close]
            if not all(isinstance(p, (int, float)) and math.isfinite(p) and p > 0 for p in prices):
                failures.append(f"Invalid non-finite or non-positive price for symbol {sym}")
                continue

            # OHLC range consistency
            if not (rec.low <= rec.open <= rec.high and rec.low <= rec.close <= rec.high and rec.low <= rec.high):
                failures.append(f"Invalid OHLC range for symbol {sym}")
                continue

            # Volume validity
            if not (isinstance(rec.volume, (int, float)) and math.isfinite(rec.volume) and rec.volume >= 0):
                failures.append(f"Invalid volume for symbol {sym}")
                continue

            # Source provenance trust policy
            source_label = str(rec.source).strip().upper()
            if not source_label or source_label not in TRUSTED_PROVIDERS:
                failures.append(f"Untrusted or missing source provenance '{rec.source}' for symbol {sym}")
                continue

            # Record passed all validation rules
            valid_symbol_counts[sym] = valid_symbol_counts.get(sym, 0) + 1

        observed_set = set(valid_symbol_counts.keys())
        missing = sorted(list(expected_set - observed_set))

        if self.policy.require_all_expected_symbols and missing:
            failures.append(f"Missing expected symbols failing validation: {tuple(missing)}")

        for sym in expected_set:
            cnt = valid_symbol_counts.get(sym, 0)
            if cnt < self.policy.minimum_records_per_symbol:
                failures.append(f"Symbol {sym} has insufficient valid records ({cnt} < {self.policy.minimum_records_per_symbol})")

        certified = len(failures) == 0

        return CertificationResult(
            certified=certified,
            generated_at=now.isoformat(),
            expected_symbol_count=len(expected_set),
            observed_symbol_count=len(observed_set),
            missing_symbols=tuple(missing),
            failures=tuple(failures)
        )
