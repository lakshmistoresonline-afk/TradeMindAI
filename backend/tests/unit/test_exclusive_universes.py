import pytest
from backend.services.exclusive_universe_service import ExclusiveUniverseService

def test_exclusive_partitions_invariants():
    partitions = ExclusiveUniverseService.get_exclusive_partitions()

    assert "NIFTY_50" in partitions
    assert "NIFTY_100_EXCL" in partitions
    assert "NIFTY_200_EXCL" in partitions
    assert "NIFTY_500_EXCL" in partitions

    u50 = set(partitions["NIFTY_50"])
    u100 = set(partitions["NIFTY_100_EXCL"])
    u200 = set(partitions["NIFTY_200_EXCL"])
    u500 = set(partitions["NIFTY_500_EXCL"])

    # Mandatory mathematical invariants: pairwise intersections must be empty sets
    assert len(u50 & u100) == 0, "Intersection of U50 and U100 must be empty"
    assert len(u50 & u200) == 0, "Intersection of U50 and U200 must be empty"
    assert len(u50 & u500) == 0, "Intersection of U50 and U500 must be empty"
    assert len(u100 & u200) == 0, "Intersection of U100 and U200 must be empty"
    assert len(u100 & u500) == 0, "Intersection of U100 and U500 must be empty"
    assert len(u200 & u500) == 0, "Intersection of U200 and U500 must be empty"

    meta = ExclusiveUniverseService.get_universe_metadata()
    for m in meta:
        uid = m["id"]
        assert m["count"] == len(partitions[uid])
        assert m["count"] >= 0
        assert m["status"] == "UNVERIFIED"

def test_controlled_fixture_partitioning():
    # Independent controlled fixtures
    n50_fix = ["RELIANCE", "TCS", "INFY"]
    n100_fix = ["RELIANCE", "TCS", "INFY", "ABB", "ACC"]
    n200_fix = ["RELIANCE", "TCS", "ABB", "APOLLOTYRE", "ASHOKLEY"]
    n500_fix = ["RELIANCE", "ABB", "APOLLOTYRE", "ZOMATO", "SUZLON"]

    parts = ExclusiveUniverseService.compute_partitions(n50_fix, n100_fix, n200_fix, n500_fix)

    assert set(parts["NIFTY_50"]) == {"INFY", "RELIANCE", "TCS"}
    assert set(parts["NIFTY_100_EXCL"]) == {"ABB", "ACC"}
    assert set(parts["NIFTY_200_EXCL"]) == {"APOLLOTYRE", "ASHOKLEY"}
    assert set(parts["NIFTY_500_EXCL"]) == {"SUZLON", "ZOMATO"}

def test_explicit_validation_rejection():
    # Non-list input
    with pytest.raises(ValueError, match="must be a list"):
        ExclusiveUniverseService.compute_partitions("not-a-list", [], [], [])

    # Non-string item
    with pytest.raises(ValueError, match="contains non-string item"):
        ExclusiveUniverseService.compute_partitions(["RELIANCE", 123], [], [], [])

    # Blank symbol
    with pytest.raises(ValueError, match="contains blank symbol"):
        ExclusiveUniverseService.compute_partitions(["RELIANCE", "   "], [], [], [])

    # Duplicate entry within source list
    with pytest.raises(ValueError, match="contains duplicate entry"):
        ExclusiveUniverseService.compute_partitions(["RELIANCE", "RELIANCE"], [], [], [])
