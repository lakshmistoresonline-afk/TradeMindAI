"""
================================================================================
TradeMindAI: Market-Data Certification Boundary (DAT-01 & TM-08)
================================================================================
Provides a reusable certification boundary that checks expected symbol coverage,
per-symbol minimum history, source provenance, data freshness, duplicate records,
and finite positive prices. Produces an explicit certification result and never treats missing data as valid.
================================================================================
"""

from __future__ import annotations
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

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
    maximum_age: timedelta = timedelta(minutes=30)
    maximum_future_skew: timedelta = timedelta(minutes=2)
    require_all_expected_symbols: bool = True

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

    def certify(self, records: Iterable[PriceRecord], expected_symbols: Iterable[str], current_time: Optional[datetime] = None) -> CertificationResult:
        now = current_time or datetime.now(timezone.utc)
        expected_set = set(s.strip().upper() for s in expected_symbols)

        symbol_counts: dict[str, int] = {}
        seen_timestamps: dict[str, set[datetime]] = {}
        failures: list[str] = []

        for rec in records:
            sym = rec.symbol.strip().upper()
            symbol_counts[sym] = symbol_counts.get(sym, 0) + 1

            if sym not in seen_timestamps:
                seen_timestamps[sym] = set()
            if rec.timestamp in seen_timestamps[sym]:
                failures.append(f"Duplicate record timestamp for symbol {sym} at {rec.timestamp}")
            seen_timestamps[sym].add(rec.timestamp)

            # Check finiteness and price validity
            prices = [rec.open, rec.high, rec.low, rec.close]
            if not all(math.isfinite(p) and p > 0 for p in prices):
                failures.append(f"Invalid non-finite or non-positive price for symbol {sym}")
            if not (math.isfinite(rec.volume) and rec.volume >= 0):
                failures.append(f"Invalid volume for symbol {sym}")
            if not (rec.low <= rec.open <= rec.high and rec.low <= rec.close <= rec.high):
                failures.append(f"Invalid OHLC range for symbol {sym}")

            # Check freshness / future skew
            if rec.timestamp > now + self.policy.maximum_future_skew:
                failures.append(f"Future-dated record for symbol {sym} at {rec.timestamp}")
            if now - rec.timestamp > self.policy.maximum_age:
                failures.append(f"Stale record for symbol {sym} at {rec.timestamp}")

            # Check source provenance
            if not rec.source or not rec.source.strip():
                failures.append(f"Missing source provenance for symbol {sym}")

        observed_set = set(symbol_counts.keys())
        missing = sorted(list(expected_set - observed_set))

        if self.policy.require_all_expected_symbols and missing:
            failures.append(f"Missing expected symbols: {missing}")

        for sym, cnt in symbol_counts.items():
            if cnt < self.policy.minimum_records_per_symbol:
                failures.append(f"Symbol {sym} has insufficient records ({cnt} < {self.policy.minimum_records_per_symbol})")

        certified = len(failures) == 0

        return CertificationResult(
            certified=certified,
            generated_at=now.isoformat(),
            expected_symbol_count=len(expected_set),
            observed_symbol_count=len(observed_set),
            missing_symbols=tuple(missing),
            failures=tuple(failures)
        )
