"""Tests for pairwise scoring."""
from src.matcher.score import MATCH_THRESHOLD, score_pair

BASE = dict(name="Müller Baumaschinen GmbH", street="Hauptstraße 14",
            city="Stuttgart", postal_code="70173", phone="+49 711 550120",
            email="info@mueller-baumaschinen.de", tax_id="DE811230001")


def test_identical_records_score_one():
    assert score_pair(BASE, dict(BASE)) == 1.0


def test_variant_scores_above_threshold():
    variant = dict(BASE, name="Mueller Baumaschinen GmbH",
                   street="Hauptstr. 14", phone="0711 550120")
    assert score_pair(BASE, variant) >= MATCH_THRESHOLD


def test_different_company_scores_below_threshold():
    other = dict(name="Roth Sicherheitstechnik GmbH", street="Torweg 6",
                 city="Nürtingen", postal_code="72622", phone="+49 7022 88110",
                 email="service@roth-sicherheit.de", tax_id="DE811230014")
    assert score_pair(BASE, other) < MATCH_THRESHOLD


def test_missing_fields_are_skipped_not_penalized():
    sparse = dict(name="Mueller Baumaschinen GmbH", street="", city="Stuttgart",
                  postal_code="", phone="", email="info@mueller-baumaschinen.de",
                  tax_id="")
    assert score_pair(BASE, sparse) >= MATCH_THRESHOLD


def test_wrong_tax_id_pulls_score_down():
    variant = dict(BASE, tax_id="DE999999999")
    assert score_pair(BASE, variant) < 1.0


def test_same_email_domain_partial_credit():
    variant = dict(BASE, email="office@mueller-baumaschinen.de")
    s = score_pair(BASE, variant)
    assert MATCH_THRESHOLD <= s < 1.0
