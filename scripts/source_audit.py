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


def entry_status(item: dict[str, Any], slots: dict[str, list[int]]) -> dict[str, Any]:
    """Per-claim audit result for one entry, with no printing, so the Definition
    of Done can read the same computation the report prints."""
    tmap = types_by_index(item)
    provenance = item.get("provenance") or {}
    exceptions = {d.get("claim"): d for d in (item.get("audit_exceptions") or []) if isinstance(d, dict)}
    rows: list[dict[str, str]] = []
    pending: list[str] = []
    excepted: list[str] = []

    for name, refs in slots.items():
        prov = provenance.get(name)
        exc = exceptions.get(name)
        if isinstance(prov, dict) and prov.get("record_anchor"):
            anchors = ", ".join(f"[{r}]" for r in prov["record_anchor"])
            mark = f"CLOSED via {anchors} ({prov.get('basis', '?')})"
        elif exc:
            mark = f"secondary-record-sufficient (searched {exc.get('search_date', '?')}, best [{exc.get('best_source', '?')}])"
            excepted.append(name)
        else:
            mark = f"needs-primary-strengthening (evidence: {evidence_label(refs, tmap)})"
            pending.append(name)
        rows.append({"claim": name, "mark": mark})

    if pending:
        status = "needs-primary-strengthening"
    elif excepted:
        status = "source-grade closed (with documented secondary-sufficient exceptions)"
    else:
        status = "source-grade closed"
    return {"title": item.get("title", item.get("slug")), "rows": rows,
            "pending": pending, "excepted": excepted, "status": status}


def audit_entry(item: dict[str, Any], slots: dict[str, list[int]]) -> dict[str, Any]:
    result = entry_status(item, slots)
    print(f"\n{result['title']}")
    for row in result["rows"]:
        print(f"  {row['claim']:34} -> {row['mark']}")
    print(f"  audit status -> {result['status']}")
    return result


def case_slots(item: dict[str, Any]) -> dict[str, list[int]]:
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
    return slots


def domain_entries(domain: str) -> list[tuple[dict[str, Any], dict[str, list[int]]]]:
    """Every audited entry in a domain with its claim slots: cases (claims and
    pattern claims) and systems (the constitutive system facts)."""
    entries: list[tuple[dict[str, Any], dict[str, list[int]]]] = []
    for cluster in ASSESSMENT_CLUSTERS:
        folder = DATA / cluster
        if folder.exists():
            for path in sorted(folder.glob("*.yaml")):
                item = load_yaml_file(path)
                if is_published(item) and item.get("domain") == domain:
                    entries.append((item, case_slots(item)))
    for cluster in RLS_CLUSTERS:
        folder = DATA / cluster
        if folder.exists():
            for path in sorted(folder.glob("*.yaml")):
                item = load_yaml_file(path)
                if is_published(item) and domain in (item.get("domains") or []):
                    slots = {"system-facts": list(
                        (item.get("rls_assessment") or {}).get("evidence", {}).get("process", []) or []
                    )}
                    entries.append((item, slots))
    return entries


def domain_audit_status(domain: str) -> dict[str, Any]:
    """Domain-level closure: how many entries are closed, and which claims are
    still open. "Known-status" counts as closed only where the exception is a
    documented decision, which validation already enforces."""
    results = [entry_status(item, slots) for item, slots in domain_entries(domain)]
    open_claims = [f"{r['title']}: {c}" for r in results for c in r["pending"]]
    return {
        "n_entries": len(results),
        "n_closed": sum(1 for r in results if not r["pending"]),
        "open_claims": open_claims,
        "closed": not open_claims,
    }


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
