from __future__ import annotations

from collections import Counter
from statistics import median
from typing import Any

import yaml

from config import (
    ASSESSMENT_CLUSTERS,
    DATA,
    DOMAIN_DOD,
    DOMAINS,
    PATTERN_ESTABLISHED_MIN,
    RLS_CLUSTERS,
    compute_ddi,
    compute_rls,
    is_published,
)


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_published(cluster: str) -> list[dict[str, Any]]:
    folder = DATA / cluster
    if not folder.exists():
        return []
    return [item for item in (load_yaml_file(p) for p in sorted(folder.glob("*.yaml"))) if is_published(item)]


def domain_report(domain: str) -> dict[str, Any]:
    ddi_scores: list[int] = []
    gaps: list[int] = []
    patterns: Counter[str] = Counter()

    for cluster in ASSESSMENT_CLUSTERS:
        for item in load_published(cluster):
            if item.get("domain") != domain:
                continue
            assessment = item.get("assessment")
            if not isinstance(assessment, dict):
                continue
            score = compute_ddi(assessment)
            ddi_scores.append(score)
            recognition = assessment.get("observed_recognition")
            if isinstance(recognition, (int, float)) and not isinstance(recognition, bool):
                gaps.append(score - recognition)
            # A case supports a pattern only when it carries explicit
            # pattern_evidence for it (source refs proving the mechanism).
            pattern_evidence = item.get("pattern_evidence") or {}
            for pat in item.get("patterns") or []:
                if pattern_evidence.get(pat):
                    patterns[pat] += 1

    rls_scores: list[int] = []
    for cluster in RLS_CLUSTERS:
        for item in load_published(cluster):
            if domain not in (item.get("domains") or []):
                continue
            assessment = item.get("rls_assessment")
            if isinstance(assessment, dict):
                rls_scores.append(compute_rls(assessment))

    return {
        "ddi_cases": len(ddi_scores),
        "median_ddi": round(median(ddi_scores)) if ddi_scores else None,
        "median_gap": round(median(gaps)) if gaps else None,
        "rls_systems": len(rls_scores),
        "median_rls": round(median(rls_scores)) if rls_scores else None,
        "patterns": patterns,
    }


def established_patterns(patterns: Counter[str]) -> list[str]:
    return [p for p, n in patterns.items() if n >= PATTERN_ESTABLISHED_MIN]


def dod_status(report: dict[str, Any]) -> tuple[bool, list[str]]:
    checks = {
        "ddi_cases": report["ddi_cases"],
        "rls_systems": report["rls_systems"],
        "patterns": len(established_patterns(report["patterns"])),
    }
    pending: list[str] = []
    for key, threshold in DOMAIN_DOD.items():
        have = checks.get(key, 0)
        if have < threshold:
            pending.append(f"{key}: {have}/{threshold}")
    return (not pending), pending


def main() -> None:
    print("ChampionsAwards - Domain maturity report\n" + "=" * 44)
    for slug, label in DOMAINS.items():
        r = domain_report(slug)
        mature, pending = dod_status(r)
        status = "MATURE v1.0" if mature else "in progress"
        print(f"\n{label}  [{slug}]  -  {status}")
        print(
            f"  DDI cases: {r['ddi_cases']}"
            f"  (median DDI {r['median_ddi']}, median gap {r['median_gap']})"
        )
        print(f"  RLS systems: {r['rls_systems']}  (median RLS {r['median_rls']})")
        if r["patterns"]:
            est = set(established_patterns(r["patterns"]))
            dist = ", ".join(
                f"{p} x{n} [{'established' if p in est else 'emergent'}]"
                for p, n in r["patterns"].most_common()
            )
            print(f"  Structural causes ({len(est)} established / {len(r['patterns'])} total): {dist}")
        else:
            print("  Structural causes (0): none tagged")
        if pending:
            print(f"  Definition of Done pending -> {', '.join(pending)}")
        else:
            print("  Definition of Done: all thresholds met")


if __name__ == "__main__":
    main()
