"""Tests for the similarity metrics."""
from src.matcher.similarity import (jaro, jaro_winkler, norm_digits,
                                    text_similarity, token_sort_similarity)


def test_jaro_identity_and_empty():
    assert jaro("abc", "abc") == 1.0
    assert jaro("", "abc") == 0.0


def test_jaro_classic_example():
    assert abs(jaro("MARTHA", "MARHTA") - 0.9444) < 0.001


def test_jaro_winkler_boosts_common_prefix():
    assert jaro_winkler("müller", "mueller") > jaro("müller", "mueller")


def test_token_sort_handles_word_order():
    assert token_sort_similarity("Schmidt & Co. KG", "KG Schmidt & Co") > 0.95


def test_text_similarity_umlaut_variant():
    assert text_similarity("Müller Baumaschinen GmbH", "Mueller Baumaschinen GmbH") > 0.9


def test_norm_digits_strips_formatting():
    assert norm_digits("+49 711 55 01 20") == "49711550120"


def test_norm_name_strips_legal_forms():
    from src.matcher.similarity import norm_name
    assert norm_name("Müller Baumaschinen GmbH") == norm_name("Müller Baumaschinen Ges.m.b.H.")
