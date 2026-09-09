from __future__ import annotations

from typing import Any

import yaml

from config import (
    ASSESSMENT_CLUSTERS,
    DATA,
    RECORD_GRADE_SOURCE_TYPES,
    RLS_CLUSTERS,
    RLS_KEYS,
    is_published,
)

# The load-bearing claim slots the audit inspects, mapped to the DDI evidence
# keys that back each. Pattern claims are added per-case from pattern_evidence.
CASE_CLAIM_SLOTS: dict[str, tuple[str, ...]] = {
    "contribution": ("impact", "verification"),
    "attribution": ("attribution",),
    "observed-recognition": ("observed_recognition",),
}


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def types_by_index(item: dict[str, Any]) -> dict[int, str]:
    return {i: (s.get("type") or "?") for i, s in enumerate(item.get("sources") or [], start=1)}


def evidence_label(refs: list[int], tmap: dict[int, str]) -> str:
    return ", ".join(f"[{r}]{tmap.get(r, '?')}" for r in refs) or "(no evidence)"


def audit_entry(item: dict[str, Any], slots: dict[str, list[int]]) -> None:
    tmap = types_by_index(item)
    provenance = item.get("provenance") or {}
    exceptions = {d.get("claim"): d for d in (item.get("audit_exceptions") or []) if isinstance(d, dict)}
    pending: list[str] = []
    excepted: list[str] = []

    print(f"\n{item.get('title', item.get('slug'))}")
    for name, refs in slots.items():
        prov = provenance.get(name)
        exc = exceptions.get(name)
        context = evidence_label(refs, tmap)
        if isinstance(prov, dict) and prov.get("record_anchor"):
            anchors = ", ".join(f"[{r}]" for r in prov["record_anchor"])
            mark = f"CLOSED via {anchors} ({prov.get('basis', '?')})"
        elif exc:
            mark = f"secondary-record-sufficient (searched {exc.get('search_date', '?')}, best [{exc.get('best_source', '?')}])"
            excepted.append(name)
        else:
            mark = f"needs-primary-strengthening (evidence: {context})"
            pending.append(name)
        print(f"  {name:34} -> {mark}")

    if pending:
        status = "needs-primary-strengthening"
    elif excepted:
        status = "source-grade closed (with documented secondary-sufficient exceptions)"
    else:
        status = "source-grade closed"
    print(f"  audit status -> {status}")


def audit_cases(domain: str) -> None:
    for cluster in ASSESSMENT_CLUSTERS:
        folder = DATA / cluster
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.yaml")):
            item = load_yaml_file(path)
            if not is_published(item) or item.get("domain") != domain:
                continue
            assessment = item.get("assessment") or {}
            evidence = assessment.get("evidence") or {}
            slots: dict[str, list[int]] = {}
            for name, keys in CASE_CLAIM_SLOTS.items():
                refs: list[int] = []
                for k in keys:
                    for r in evidence.get(k, []) or []:
                        if r not in refs:
                            refs.append(r)
                slots[name] = refs
            for pat, refs in (item.get("pattern_evidence") or {}).items():
                slots[f"pattern:{pat}"] = list(refs)
            audit_entry(item, slots)


def audit_systems(domain: str) -> None:
    for cluster in RLS_CLUSTERS:
        folder = DATA / cluster
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.yaml")):
            item = load_yaml_file(path)
            if not is_published(item) or domain not in (item.get("domains") or []):
                continue
            # The source-grade audit targets factual claims, not the evaluative
            # RLS dimensions (those are assessments governed by rationale +
            # evidence). For a system, the load-bearing fact is how the award is
            # constituted and administered - which its own institution documents.
            slots = {"system-facts": list((item.get("rls_assessment") or {}).get("evidence", {}).get("process", []) or [])}
            audit_entry(item, slots)


def main() -> None:
    domain = "physics-astronomy"
    print("ChampionsAwards - Source-grade provenance audit")
    print(f"Domain: {domain}")
    print("Legend: [n]<type> per claim; record-grade = primary/archival/institutional")
    print("=" * 60)
    print("\n### Individuals")
    audit_cases(domain)
    print("\n### Recognition systems")
    audit_systems(domain)


if __name__ == "__main__":
    main()
