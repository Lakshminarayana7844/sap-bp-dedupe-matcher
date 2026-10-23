"""Pairwise match scoring: a simplified Fellegi-Sunter-style weighted sum.

Each field contributes its weight times a per-field similarity. Exact-key
fields (email, tax id) score 1.0 or 0.0; text fields use Jaro-Winkler.
The final score is normalized to [0, 1] by the total compared weight.
This is a pragmatic simplification of classic Fellegi-Sunter: weights
are hand-set from field reliability instead of estimated m/u ratios.
"""
from __future__ import annotations

from .similarity import jaro_winkler, norm_digits, norm_name, norm_text, text_similarity

FIELDS = [
    # (field, weight, comparator)
    ("name", 3.0, "name"),
    ("street", 1.5, "text"),
    ("city", 0.8, "text"),
    ("postal_code", 1.2, "plz"),
    ("phone", 2.5, "digits"),
    ("email", 3.5, "email"),
    ("tax_id", 4.0, "digits"),
]

MATCH_THRESHOLD = 0.78
REVIEW_THRESHOLD = 0.60


def _field_similarity(a: str, b: str, kind: str) -> float | None:
    """Similarity in [0,1] or None when either side is empty (field skipped)."""
    if not (a or "").strip() or not (b or "").strip():
        return None
    if kind == "name":
        return text_similarity(norm_name(a), norm_name(b))
    if kind == "text":
        return text_similarity(a, b)
    if kind == "plz":
        da, db = norm_digits(a), norm_digits(b)
        if not da or not db:
            return None
        if da == db:
            return 1.0
        return jaro_winkler(da, db) * 0.5  # close but not equal postcodes
    if kind == "digits":
        da, db = norm_digits(a), norm_digits(b)
        if not da or not db:
            return None
        return 1.0 if da == db or da.endswith(db[-7:]) or db.endswith(da[-7:]) else 0.0
    if kind == "exact_lower":
        return 1.0 if a.strip().lower() == b.strip().lower() else 0.0
    if kind == "email":
        ea, eb = a.strip().lower(), b.strip().lower()
        if ea == eb:
            return 1.0
        if "@" in ea and "@" in eb and ea.split("@", 1)[1] == eb.split("@", 1)[1]:
            return 0.5  # same company domain, different mailbox
        return 0.0
    raise ValueError(f"unknown comparator {kind!r}")


def score_pair(rec_a: dict, rec_b: dict) -> float:
    """Weighted match score in [0, 1] for two business-partner records."""
    total = 0.0
    weight = 0.0
    for field, w, kind in FIELDS:
        sim = _field_similarity(rec_a.get(field, ""), rec_b.get(field, ""), kind)
        if sim is None:
            continue
        total += w * sim
        weight += w
    if weight == 0.0:
        return 0.0
    return total / weight
