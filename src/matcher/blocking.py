"""Candidate blocking: only compare record pairs that share a block key."""
from __future__ import annotations

from .similarity import norm_digits, norm_text

MAX_BLOCK = 12


def block_keys(record: dict) -> set[str]:
    """All block keys a record belongs to."""
    keys = set()
    city = norm_text(record.get("city", ""))
    if city:
        keys.add(f"city:{city}")
    postal = norm_digits(record.get("postal_code", ""))
    if len(postal) >= 2:
        keys.add(f"plz2:{postal[:2]}")
    phone = norm_digits(record.get("phone", ""))
    if len(phone) >= 5:
        keys.add(f"tel:{phone[-5:]}")
    email = (record.get("email") or "").strip().lower()
    if "@" in email:
        keys.add(f"edom:{email.split('@', 1)[1]}")
    return keys


def candidate_pairs(records: list[dict]) -> list[tuple[int, int]]:
    """Index pairs sharing at least one block key, big blocks skipped."""
    blocks: dict[str, list[int]] = {}
    for idx, rec in enumerate(records):
        for key in block_keys(rec):
            blocks.setdefault(key, []).append(idx)
    pairs: set[tuple[int, int]] = set()
    for members in blocks.values():
        if len(members) > MAX_BLOCK:
            continue  # block too coarse to be useful
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = sorted((members[i], members[j]))
                pairs.add((a, b))
    return sorted(pairs)
