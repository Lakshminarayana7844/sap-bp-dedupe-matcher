"""End-to-end dedupe pipeline: load -> block -> score -> cluster -> golden.

Usage:
  python -m src.matcher.pipeline --input data/business_partners.csv --out out/

Writes to --out:
  scored_pairs.csv     every candidate pair above the review threshold
  clusters.json        duplicate clusters with member bp_ids
  golden_records.csv   one merged record per cluster (plus singletons)
  metrics.json         precision/recall vs the truth column true_group_id
"""
from __future__ import annotations

import argparse
import csv
import json
import os

from .blocking import candidate_pairs
from .cluster import build_clusters
from .golden import golden_record
from .score import MATCH_THRESHOLD, REVIEW_THRESHOLD, score_pair


def load_records(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def truth_pairs(records: list[dict]) -> set[tuple[int, int]]:
    """All index pairs that share a non-empty true_group_id."""
    groups: dict[str, list[int]] = {}
    for i, rec in enumerate(records):
        gid = (rec.get("true_group_id") or "").strip()
        if gid:
            groups.setdefault(gid, []).append(i)
    pairs = set()
    for members in groups.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                pairs.add(tuple(sorted((members[i], members[j]))))
    return pairs


def run(records: list[dict], out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    pairs = candidate_pairs(records)
    scored = [(a, b, score_pair(records[a], records[b])) for a, b in pairs]
    matched = [(a, b) for a, b, s in scored if s >= MATCH_THRESHOLD]
    clusters = build_clusters(matched)

    with open(os.path.join(out_dir, "scored_pairs.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["bp_id_a", "bp_id_b", "score", "decision"])
        for a, b, s in sorted(scored, key=lambda x: -x[2]):
            if s < REVIEW_THRESHOLD:
                continue
            w.writerow([records[a]["bp_id"], records[b]["bp_id"],
                        f"{s:.3f}", "match" if s >= MATCH_THRESHOLD else "review"])

    cluster_payload = [
        {"cluster_id": n + 1, "bp_ids": [records[i]["bp_id"] for i in cluster]}
        for n, cluster in enumerate(clusters)
    ]
    with open(os.path.join(out_dir, "clusters.json"), "w", encoding="utf-8") as fh:
        json.dump(cluster_payload, fh, indent=2)

    clustered = {i for c in clusters for i in c}
    golden = [golden_record(records, c) for c in clusters]
    golden += [golden_record(records, [i]) for i in range(len(records)) if i not in clustered]
    fieldnames = ["source_ids", "cluster_size", "name", "street", "city",
                  "postal_code", "phone", "email", "tax_id", "country", "industry"]
    with open(os.path.join(out_dir, "golden_records.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(golden)

    metrics = evaluate(records, set(matched))
    with open(os.path.join(out_dir, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    return metrics


def evaluate(records: list[dict], matched: set[tuple[int, int]]) -> dict:
    truth = truth_pairs(records)
    tp = len(matched & truth)
    precision = tp / len(matched) if matched else 0.0
    recall = tp / len(truth) if truth else 0.0
    return {
        "candidate_pairs": len(candidate_pairs(records)),
        "matched_pairs": len(matched),
        "truth_pairs": len(truth),
        "true_positives": tp,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/business_partners.csv")
    parser.add_argument("--out", default="out")
    args = parser.parse_args()
    records = load_records(args.input)
    metrics = run(records, args.out)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
