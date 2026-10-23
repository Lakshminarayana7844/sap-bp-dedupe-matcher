# sap-bp-dedupe-matcher

Duplicate detection (record linkage) for SAP business partners, the way an
MDM team approaches it: block candidate pairs, score them field by field,
cluster the matches, and merge each cluster into one golden record.

SAP landscapes accumulate duplicate customer and vendor masters fast (every
interface and every sales org creates its own). This project shows the full
dedupe flow on a realistic German business-partner table with planted
duplicates: umlaut variants, legal-form differences (`GmbH` vs
`Ges.m.b.H.`), street abbreviations, phone formats, and changed mailboxes.

## How it works

```
business_partners.csv
      |  blocking: city, postcode prefix, phone suffix, email domain
      v
  candidate pairs (54 from 26 records, not all 325)
      |  scoring: weighted field similarities, simplified Fellegi-Sunter
      v
  matched pairs (score >= 0.78, review band 0.60-0.78)
      |  union-find clustering (transitive duplicates land in one group)
      v
  golden records: majority value per field, ties to the most complete record
```

- **Blocking** (`blocking.py`): keys from city, postcode prefix, phone
  suffix and email domain; oversized blocks are skipped.
- **Scoring** (`score.py`): weights by field reliability (tax id 4.0,
  email 3.5, name 3.0, ...). Names are normalized for German legal forms
  before comparison. Same email domain with a different mailbox earns
  partial credit, a standard heuristic for B2B company matching.
- **Clustering** (`cluster.py`): union-find, so A-B and B-C put A, B, C in
  one duplicate group.
- **Golden record** (`golden.py`): majority per field, ties resolved by the
  most complete member.
- **Measured, not asserted**: the sample data carries a `true_group_id`
  column, and the pipeline reports precision and recall against it
  (`metrics.json`). On the sample: 1.0 / 1.0.

## Run it

```bash
pip install -r requirements.txt   # only pytest; the matcher itself is stdlib
python -m src.matcher.pipeline --input data/business_partners.csv --out out/
```

Outputs in `out/`: `scored_pairs.csv` (with match/review decisions),
`clusters.json`, `golden_records.csv`, `metrics.json`.

Tests (19, pure Python):

```bash
python -m pytest tests/ -q
```

Docker:

```bash
docker build -t sap-bp-dedupe-matcher .
docker run --rm sap-bp-dedupe-matcher
```

## Repository layout

```
data/business_partners.csv   26 SAP-style BPs: 10 duplicate groups, 4 singletons, truth labels
src/matcher/similarity.py    Jaro/Jaro-Winkler, token-sort, name and phone normalization
src/matcher/blocking.py      candidate pair generation
src/matcher/score.py         weighted field scoring (match threshold 0.78)
src/matcher/cluster.py       union-find clustering
src/matcher/golden.py        golden-record merge
src/matcher/pipeline.py      CLI orchestration + precision/recall vs truth
tests/                       19 tests across all stages
.github/workflows/ci.yml     runs the tests on every push
```

## Honest limits

- Weights are hand-set, not estimated from labeled data (real
  Fellegi-Sunter estimates m/u probabilities; a future step is EM training
  on a larger labeled set).
- Blocking recalls every planted duplicate here, but very different
  spellings of the same company with no shared key would be missed; a
  phonetic key (Cologne phonetics / Soundex) is the usual next addition.
- 26 records is a demo set. The pipeline is O(pairs in blocks) and the
  same stages run on Spark for millions of records, but this code is
  single-machine Python on purpose: the semantics stay readable.
- Threshold 0.78 is tuned on this sample and documented in `score.py`;
  the review band (0.60-0.78) is where a steward would decide in
  production.
