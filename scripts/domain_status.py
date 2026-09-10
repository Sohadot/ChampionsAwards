"""Domain maturity report (DoD v1.1). All aggregation comes from the canonical
engine (domain_comparison.py) and the provenance audit (source_audit.py); this
module only applies the Definition of Done and prints the status.

DoD v1.1 asks whether the inquiry is complete, not whether the findings came out
a particular way. Pattern counts are printed as observations and are not gates -
see the rationale in config.py.
"""
from __future__ import annotations

from typing import Any

import yaml

from config import (
    DATA,
    DOD_VERSION,
    DOMAIN_DOD,
    DOMAIN_DOD_ACCOUNTING,
    DOMAINS,
    is_published,
)
from domain_comparison import (
    _domain_awards,
    corpus_distribution,
    pattern_distribution,
    rls_profiles,
)
from source_audit import domain_audit_status


def _has_synthesis(domain: str) -> bool:
    folder = DATA / "reports"
    if not folder.exists():
        return False
    for path in sorted(folder.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            item = yaml.safe_load(f) or {}
        if is_published(item) and item.get("derives_from") == domain:
            return True
    return False


def _has_award_anatomy(domain: str) -> bool:
    """An award is mapped in full when its formal architecture and its corpus
    relations both exist - rules plus where the cases meet them."""
    return any(
        isinstance(award.get("architecture"), dict) and award.get("architecture")
        and isinstance(award.get("corpus_relations"), list) and award.get("corpus_relations")
        for award in _domain_awards(domain)
    )


def dod_rows(domain: str) -> list[dict[str, Any]]:
    """The Definition of Done, as measured. One source of truth for the status
    report and for the sector page."""
    corpus = corpus_distribution(domain)
    patterns = pattern_distribution(domain)
    systems = rls_profiles(domain)
    audit = domain_audit_status(domain)

    measured = {"ddi_cases": corpus["n_cases"], "rls_systems": systems["n_systems"]}
    labels = {"ddi_cases": "DDI cases", "rls_systems": "RLS systems"}
    rows: list[dict[str, Any]] = [
        {"requirement": labels.get(key, key.replace("_", " ")), "have": measured[key], "need": need,
         "met": measured[key] >= need, "kind": "threshold"}
        for key, need in DOMAIN_DOD.items()
    ]
    rows.append({
        "requirement": "mechanism accounting",
        "have": f"{patterns['accounting_coverage_percentage']}%",
        "need": f"{DOMAIN_DOD_ACCOUNTING['mechanism_accounting_percentage']}%",
        "met": patterns["accounting_coverage_percentage"] >= DOMAIN_DOD_ACCOUNTING["mechanism_accounting_percentage"],
        "kind": "accounting",
    })
    rows.append({
        "requirement": "cases unaudited",
        "have": len(patterns["cases_unaudited"]),
        "need": DOMAIN_DOD_ACCOUNTING["cases_unaudited"],
        "met": len(patterns["cases_unaudited"]) <= DOMAIN_DOD_ACCOUNTING["cases_unaudited"],
        "kind": "accounting",
    })
    rows.append({
        "requirement": "source-grade closure",
        "have": f"{audit['n_closed']}/{audit['n_entries']}",
        "need": "all", "met": audit["closed"], "kind": "layer",
    })
    rows.append({
        "requirement": "award anatomy",
        "have": "mapped" if _has_award_anatomy(domain) else "none",
        "need": "mapped", "met": _has_award_anatomy(domain), "kind": "layer",
    })
    rows.append({
        "requirement": "synthesis",
        "have": "published" if _has_synthesis(domain) else "none",
        "need": "published", "met": _has_synthesis(domain), "kind": "layer",
    })
    return rows


def observed_rows(domain: str) -> list[dict[str, Any]]:
    """Reported, never required. These describe what the corpus turned out to
    contain; none of them gates maturity under DoD v1.1."""
    patterns = pattern_distribution(domain)
    return [
        {"observation": "evidenced mechanisms", "value": len(patterns["patterns"])},
        {"observation": "established mechanisms", "value": patterns["established_count"]},
        {"observation": "emergent mechanisms",
         "value": sum(1 for p in patterns["patterns"] if p["status"] == "emergent")},
        {"observation": "cases unexplained after audit",
         "value": f"{patterns['n_cases_without_evidenced_pattern']}/{patterns['denominator']}"},
    ]


def dod_status(domain: str) -> tuple[bool, list[str]]:
    rows = dod_rows(domain)
    pending = [f"{r['requirement']}: {r['have']}/{r['need']}" for r in rows if not r["met"]]
    return (not pending), pending


def main() -> None:
    print(f"ChampionsAwards - Domain maturity report ({DOD_VERSION})\n" + "=" * 48)
    for slug, label in DOMAINS.items():
        corpus = corpus_distribution(slug)
        patterns = pattern_distribution(slug)
        systems = rls_profiles(slug)
        mature, pending = dod_status(slug)
        print(f"\n{label}  [{slug}]  -  {'MATURE v1.0' if mature else 'in progress'}")
        print(f"  DDI cases: {corpus['n_cases']}  (median DDI {corpus['median_ddi']}, median gap {corpus['median_gap']})")
        print(f"  RLS systems: {systems['n_systems']}  (median RLS {systems['median_composite']})")
        print(f"  Mechanism accounting: {patterns['n_cases_accounted']}/{patterns['denominator']} "
              f"({patterns['accounting_coverage_percentage']}%), unaudited {len(patterns['cases_unaudited'])}")
        print("  Observed (not required): " + ", ".join(
            f"{row['observation']} {row['value']}" for row in observed_rows(slug)))
        if pending:
            print(f"  Definition of Done pending -> {', '.join(pending)}")
        else:
            print("  Definition of Done: every criterion met")


if __name__ == "__main__":
    main()
