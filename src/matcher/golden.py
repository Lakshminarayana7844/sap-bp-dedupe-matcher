"""Golden record: one best record per duplicate cluster."""
from __future__ import annotations

from collections import Counter

FIELDS = ["name", "street", "city", "postal_code", "phone", "email", "tax_id",
          "country", "industry"]


def _completeness(record: dict) -> int:
    return sum(1 for f in FIELDS if (record.get(f) or "").strip())


def golden_record(records: list[dict], cluster: list[int]) -> dict:
    """Merge a cluster: per field take the majority value; ties go to the
    most complete record's value. Cluster of one passes through."""
    members = [records[i] for i in cluster]
    best = max(members, key=_completeness)
    merged = {"source_ids": ",".join(r["bp_id"] for r in members),
              "cluster_size": len(members)}
    for field in FIELDS:
        values = [(r.get(field) or "").strip() for r in members]
        values = [v for v in values if v]
        if not values:
            merged[field] = ""
            continue
        top = Counter(values).most_common()
        if len(top) == 1 or top[0][1] > top[1][1]:
            merged[field] = top[0][0]
        else:
            merged[field] = (best.get(field) or "").strip()
    return merged
