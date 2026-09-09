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


def slot_line(refs: list[int], tmap: dict[int, str]) -> tuple[str, bool]:
    kinds = [tmap.get(r, "?") for r in refs]
    record_grade = any(k in RECORD_GRADE_SOURCE_TYPES for k in kinds)
    label = ", ".join(f"[{r}]{tmap.get(r, '?')}" for r in refs) or "(no evidence)"
    return label, record_grade


def audit_entry(item: dict[str, Any], slots: dict[str, list[int]]) -> None:
    tmap = types_by_index(item)
    exceptions = set(item.get("audit_exceptions") or [])
    pending: list[str] = []
    excepted: list[str] = []

    print(f"\n{item.get('title', item.get('slug'))}")
    for name, refs in slots.items():
        label, record_grade = slot_line(refs, tmap)
        if record_grade:
            mark = "record-grade OK"
        elif name in exceptions:
            mark = "primary-not-found / secondary-record-sufficient"
            excepted.append(name)
        else:
            mark = "needs-primary-strengthening"
            pending.append(name)
        print(f"  {name:32} {label:24} -> {mark}")

    if pending:
        status = "needs-primary-strengthening"
    elif excepted:
        status = "source-grade closed (with reviewed secondary exceptions)"
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
            evidence = (item.get("rls_assessment") or {}).get("evidence") or {}
            slots = {f"rls:{k}": list(evidence.get(k, []) or []) for k in RLS_KEYS}
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
