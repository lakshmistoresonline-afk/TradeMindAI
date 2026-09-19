import datetime
from datetime import timezone
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.freshness_policy import FreshnessPolicy

def test_policy():
    now = datetime.datetime.now(timezone.utc)

    cases = [
        ("Now", now, "FRESH"),
        ("14m ago", now - datetime.timedelta(minutes=14), "FRESH"),
        ("15m ago", now - datetime.timedelta(minutes=15), "AGING"),
        ("119m ago", now - datetime.timedelta(minutes=119), "AGING"),
        ("120m ago", now - datetime.timedelta(minutes=120), "STALE"),
        ("121m ago", now - datetime.timedelta(minutes=121), "STALE"),
        ("None", None, "UNAVAILABLE"),
        ("Future", now + datetime.timedelta(minutes=5), "INVALID_FUTURE"),
    ]

    print("CLAIM: FRESH < 15m, AGING 15-120m, STALE > 120m")
    print("-" * 60)
    print(f"{'Case':<15} | {'Expected':<15} | {'Actual':<15} | {'Result'}")
    print("-" * 60)

    for label, ts, expected in cases:
        actual = FreshnessPolicy.get_status(ts)
        res = "PASS" if actual == expected else "FAIL"
        print(f"{label:<15} | {expected:<15} | {actual:<15} | {res}")

if __name__ == "__main__":
    test_policy()
