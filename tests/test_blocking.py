"""Tests for candidate blocking."""
from src.matcher.blocking import candidate_pairs
from src.matcher.pipeline import load_records


def test_blocking_finds_planted_duplicates():
    records = load_records("data/business_partners.csv")
    pairs = candidate_pairs(records)
    assert pairs, "expected some candidate pairs"
    # every planted duplicate pair must be a candidate
    from src.matcher.pipeline import truth_pairs
    assert truth_pairs(records) <= set(pairs)


def test_blocking_is_selective():
    records = load_records("data/business_partners.csv")
    n = len(records)
    assert len(candidate_pairs(records)) < n * (n - 1) / 2
