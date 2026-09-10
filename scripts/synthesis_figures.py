"""Figure tokens for synthesis reports.

A synthesis may not hand-type a statistic. Report prose states figures only as
tokens - {median_gap}, {pattern_support:credit-misattribution} - which are
resolved at build time from the canonical engine. Two rules follow, and both are
enforced rather than remembered:

  * an unknown token fails validation, so a report cannot cite a figure the
    engine does not produce;
  * a bare number in report prose fails validation, so a figure cannot drift
    away from the corpus it came from. (Years are the one exception: a date is
    not a statistic.)

The model must yield to the evidence; this module is where that rule stops being
a principle and becomes a build error.
"""
from __future__ import annotations

import re
from typing import Any

from config import DOMAIN_DOD, DOMAINS, PATTERN_ESTABLISHED_MIN
from domain_comparison import _domain_awards, build_comparison

TOKEN_PATTERN = re.compile(r"\{([a-z0-9_]+)(?::([a-z0-9\-+]+))?\}")
# Digits that are allowed to appear literally: dates. A date says when the
# record was made or read; it is not a statistic about the corpus. Everything
# else numeric must come from a token.
DATE_PATTERN = re.compile(r"\b(?:1[5-9]\d{2}|20\d{2})(?:-\d{2}-\d{2}|s)?\b")
DIGITS_PATTERN = re.compile(r"\d+(?:\.\d+)?")


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return str(value)


def figure_map(domain: str) -> dict[str, str]:
    """Every figure a report may cite, keyed by token name. One flat vocabulary,
    all of it computed by the engine in this build."""
    result = build_comparison(domain)
    corpus = result["observations"]["corpus_distribution"]
    patterns = result["observations"]["structural_patterns"]
    systems = result["observations"]["recognition_system_profiles"]
    awards = result["observations"]["award_interactions"]
    spread = systems["dimension_spread"]
    widest = max(spread, key=lambda k: (spread[k]["spread"], k)) if spread else None

    figures: dict[str, str] = {
        "domain_label": DOMAINS.get(domain, domain),
        "corpus_snapshot": result["corpus_snapshot"],
        "data_through": str(result["population"]["data_through"]),
        "methodology_version": str(result["population"]["methodology_version"]),
        "rls_version": str(result["population"]["rls_version"]),
        "n_cases": _fmt(corpus["n_cases"]),
        "median_ddi": _fmt(corpus["median_ddi"]),
        "median_observed": _fmt(corpus["median_observed_recognition"]),
        "median_gap": _fmt(corpus["median_gap"]),
        "gap_min": _fmt(corpus["gap_min"]),
        "gap_max": _fmt(corpus["gap_max"]),
        "gap_q1": _fmt(corpus["gap_q1"]),
        "gap_q3": _fmt(corpus["gap_q3"]),
        "gap_iqr": _fmt(corpus["gap_iqr"]),
        "ddi_min": _fmt(corpus["ddi_min"]),
        "ddi_max": _fmt(corpus["ddi_max"]),
        "ddi_spread": _fmt(corpus["ddi_spread"]),
        "observed_min": _fmt(corpus["observed_min"]),
        "observed_max": _fmt(corpus["observed_max"]),
        "observed_spread": _fmt(corpus["observed_spread"]),
        "cases_without_mechanism": _fmt(patterns["n_cases_without_evidenced_pattern"]),
        "cases_audited": _fmt(patterns["n_cases_audited"]),
        "cases_accounted": _fmt(patterns["n_cases_accounted"]),
        "accounting_coverage": _fmt(patterns["accounting_coverage_percentage"]),
        "cases_unaudited": _fmt(len(patterns["cases_unaudited"])),
        "established_patterns": _fmt(patterns["established_count"]),
        "emergent_patterns": _fmt(sum(1 for p in patterns["patterns"] if p["status"] == "emergent")),
        "total_patterns": _fmt(len(patterns["patterns"])),
        "pattern_min": _fmt(PATTERN_ESTABLISHED_MIN),
        "pattern_threshold": _fmt(DOMAIN_DOD.get("patterns", 0)),
        "n_systems": _fmt(systems["n_systems"]),
        "rls_median": _fmt(systems["median_composite"]),
        "rls_min": _fmt(systems["composite_min"]),
        "rls_max": _fmt(systems["composite_max"]),
        "n_awards": _fmt(len(_domain_awards(domain))),
        "n_award_relations": _fmt(awards["denominator"]),
    }
    if widest:
        figures["rls_widest_dimension"] = widest.replace("_", " ")
        figures["rls_widest_spread"] = _fmt(spread[widest]["spread"])
        figures["rls_widest_min"] = _fmt(spread[widest]["min"])
        figures["rls_widest_max"] = _fmt(spread[widest]["max"])
    for pattern in patterns["patterns"]:
        figures[f"pattern_support:{pattern['pattern']}"] = _fmt(pattern["support"])
        figures[f"pattern_share:{pattern['pattern']}"] = _fmt(pattern["corpus_percentage"])
        figures[f"pattern_status:{pattern['pattern']}"] = pattern["status"]
    for pair in patterns["co_occurrence"]:
        figures[f"pattern_pair:{pair['pair'][0]}+{pair['pair'][1]}"] = _fmt(pair["count"])
    for row in awards["distribution"]:
        figures[f"award_count:{row['interaction_type']}"] = _fmt(row["count"])
    for band, count in corpus["ddi_band_counts"].items():
        figures[f"ddi_band:{band.lower()}"] = _fmt(count)
    return figures


def _token_key(match: re.Match[str]) -> str:
    name, arg = match.group(1), match.group(2)
    return f"{name}:{arg}" if arg else name


def unknown_tokens(text: str, figures: dict[str, str]) -> list[str]:
    return [_token_key(m) for m in TOKEN_PATTERN.finditer(text) if _token_key(m) not in figures]


def bare_numbers(text: str) -> list[str]:
    """Numbers typed directly into report prose (dates excluded). A statistic must
    arrive as a token so it can never drift from the corpus."""
    stripped = TOKEN_PATTERN.sub(" ", text)
    stripped = DATE_PATTERN.sub(" ", stripped)
    return DIGITS_PATTERN.findall(stripped)


def resolve(text: str, figures: dict[str, str]) -> str:
    """Substitute figure tokens. Unknown tokens are left visible rather than
    silently blanked; validation rejects them before a build ever renders."""
    return TOKEN_PATTERN.sub(lambda m: figures.get(_token_key(m), m.group(0)), text)


def cited_tokens(text: str) -> list[str]:
    return [_token_key(m) for m in TOKEN_PATTERN.finditer(text)]
