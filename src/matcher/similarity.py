"""String similarity metrics, no external dependencies."""
from __future__ import annotations


def jaro(s: str, t: str) -> float:
    """Classic Jaro similarity in [0, 1]."""
    if s == t:
        return 1.0
    if not s or not t:
        return 0.0
    match_dist = max(len(s), len(t)) // 2 - 1
    match_dist = max(match_dist, 0)
    s_matches = [False] * len(s)
    t_matches = [False] * len(t)
    matches = 0
    for i, ch in enumerate(s):
        lo = max(0, i - match_dist)
        hi = min(len(t), i + match_dist + 1)
        for j in range(lo, hi):
            if not t_matches[j] and t[j] == ch:
                s_matches[i] = True
                t_matches[j] = True
                matches += 1
                break
    if matches == 0:
        return 0.0
    transpositions = 0
    k = 0
    for i in range(len(s)):
        if s_matches[i]:
            while not t_matches[k]:
                k += 1
            if s[i] != t[k]:
                transpositions += 1
            k += 1
    transpositions //= 2
    return (matches / len(s) + matches / len(t)
            + (matches - transpositions) / matches) / 3


def jaro_winkler(s: str, t: str, prefix_weight: float = 0.1, max_prefix: int = 4) -> float:
    """Jaro-Winkler similarity: boosts Jaro for a common prefix."""
    base = jaro(s, t)
    prefix = 0
    for a, b in zip(s, t):
        if a == b and prefix < max_prefix:
            prefix += 1
        else:
            break
    return base + prefix * prefix_weight * (1 - base)


def norm_text(value: str) -> str:
    """Lowercase, strip punctuation-ish noise, collapse spaces."""
    out = []
    for ch in (value or "").lower():
        out.append(ch if ch.isalnum() else " ")
    return " ".join("".join(out).split())


LEGAL_TOKENS = {
    "gmbh", "ag", "kg", "ohg", "mbh", "eg", "ek", "ug", "se", "kg aa",
    "ges", "gesellschaft", "co", "und", "gbr",
}


def norm_name(value: str) -> str:
    """Normalize a business name: drop legal-form tokens so that
    'Müller GmbH' and 'Müller Ges.m.b.H.' compare on the real name."""
    tokens = [t for t in norm_text(value).split()
              if t not in LEGAL_TOKENS and len(t) > 1]
    return " ".join(tokens)


def token_sort_similarity(a: str, b: str) -> float:
    """Jaro-Winkler over alphabetically sorted token strings.

    Handles word-order variants like 'Schmidt & Co. KG' vs 'KG Schmidt & Co'.
    """
    ta = " ".join(sorted(norm_text(a).split()))
    tb = " ".join(sorted(norm_text(b).split()))
    return jaro_winkler(ta, tb)


def norm_digits(value: str) -> str:
    """Keep only digits, for phone and tax id comparison."""
    return "".join(ch for ch in (value or "") if ch.isdigit())


def text_similarity(a: str, b: str) -> float:
    """Best of plain and token-sorted Jaro-Winkler on normalized text."""
    na, nb = norm_text(a), norm_text(b)
    if not na or not nb:
        return 0.0
    return max(jaro_winkler(na, nb), token_sort_similarity(a, b))
