"""End-to-end pipeline tests on the sample data."""
from src.matcher.cluster import build_clusters
from src.matcher.golden import golden_record
from src.matcher.pipeline import evaluate, load_records, run


def test_pipeline_metrics_meet_bar(tmp_path):
    records = load_records("data/business_partners.csv")
    metrics = run(records, str(tmp_path))
    assert metrics["precision"] >= 0.9
    assert metrics["recall"] >= 0.9


def test_outputs_written(tmp_path):
    import json
    records = load_records("data/business_partners.csv")
    run(records, str(tmp_path))
    clusters = json.loads((tmp_path / "clusters.json").read_text())
    assert len(clusters) == 10  # 10 planted duplicate groups
    lines = (tmp_path / "golden_records.csv").read_text().strip().splitlines()
    assert len(lines) == 1 + 14  # header + 14 unique businesses


def test_golden_record_majority_and_completeness():
    records = [
        dict(bp_id="BP1", name="Müller GmbH", street="Hauptstr. 1", city="",
             postal_code="70173", phone="0711 1", email="", tax_id="DE1",
             country="DE", industry="Machinery"),
        dict(bp_id="BP2", name="Müller GmbH", street="Hauptstraße 1", city="Stuttgart",
             postal_code="70173", phone="+49 711 1", email="info@mueller.de",
             tax_id="DE1", country="DE", industry="Machinery"),
    ]
    merged = golden_record(records, [0, 1])
    assert merged["name"] == "Müller GmbH"
    assert merged["city"] == "Stuttgart"  # only one non-empty value
    assert merged["email"] == "info@mueller.de"
    assert merged["cluster_size"] == 2


def test_clusters_transitive():
    assert build_clusters([(0, 1), (1, 2)]) == [[0, 1, 2]]
