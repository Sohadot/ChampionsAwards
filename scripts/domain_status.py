"""Domain maturity report. All aggregation comes from the canonical engine
(domain_comparison.py); this module only applies the Definition of Done and
prints the status. One corpus, one aggregation engine, many representations.
"""
from __future__ import annotations

from typing import Any

from config import DOMAIN_DOD, DOMAINS
from domain_comparison import corpus_distribution, pattern_distribution, rls_profiles


def dod_status(corpus: dict[str, Any], patterns: dict[str, Any], systems: dict[str, Any]) -> tuple[bool, list[str]]:
    checks = {
        "ddi_cases": corpus["n_cases"],
        "rls_systems": systems["n_systems"],
        "patterns": patterns["established_count"],
    }
    pending = [f"{k}: {checks.get(k, 0)}/{t}" for k, t in DOMAIN_DOD.items() if checks.get(k, 0) < t]
    return (not pending), pending


def main() -> None:
    print("ChampionsAwards - Domain maturity report\n" + "=" * 44)
    for slug, label in DOMAINS.items():
        corpus = corpus_distribution(slug)
        patterns = pattern_distribution(slug)
        systems = rls_profiles(slug)
        mature, pending = dod_status(corpus, patterns, systems)
        status = "MATURE v1.0" if mature else "in progress"
        print(f"\n{label}  [{slug}]  -  {status}")
        print(f"  DDI cases: {corpus['n_cases']}  (median DDI {corpus['median_ddi']}, median gap {corpus['median_gap']})")
        print(f"  RLS systems: {systems['n_systems']}  (median RLS {systems['median_composite']})")
        if patterns["patterns"]:
            dist = ", ".join(f"{p['pattern']} x{p['support']} [{p['status']}]" for p in patterns["patterns"])
            print(f"  Structural causes ({patterns['established_count']} established / {len(patterns['patterns'])} total): {dist}")
        else:
            print("  Structural causes (0): none tagged")
        if pending:
            print(f"  Definition of Done pending -> {', '.join(pending)}")
        else:
            print("  Definition of Done: all thresholds met")


if __name__ == "__main__":
    main()
