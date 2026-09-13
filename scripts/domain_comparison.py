"""Canonical aggregation engine for a recognition domain.

One corpus -> one aggregation engine -> many representations. domain_status.py,
the (future) sector page, the synthesis, and any export all read from here, so
the same numbers are never computed twice.

The engine returns OBSERVATIONS only - medians, distributions, counts, ranges,
evidenced pattern support. It never emits causal conclusions, and every count
carries an explicit denominator. Corpus frequency is not field prevalence.

Determinism: all inputs are sorted by slug before aggregation, quartiles use a
single fixed (inclusive) definition, and a data-derived snapshot id identifies
the corpus a result was computed from. Nothing in the result depends on wall
clock time. The corpus is dated by `data_through` - the most recent
`last_reviewed` among the inputs actually included - not by build time. Build
time is available separately (`generated_at()`), is operational metadata only,
and is excluded from the identity and from every stable output.

Publication boundary: this module writes no file into the site output directory.
The JSON report is a build-internal artifact under `reports/`; published
representations call `build_comparison()` at build time and render HTML. This
began as a Cycle 01 deferral of public data export and outlived it: closing the
cycle lapsed the deferral but enabled nothing. Publishing a machine-readable
endpoint stays a separate decision, and until it is taken, nothing here creates one.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from config import (
    ASSESSMENT_CLUSTERS,
    PUBLISHED_SECTORS,
    AUDIT_ELIGIBLE_CONCEPT_TYPES,
    CURRENT_ONTOLOGY_REVISION,
    DATA,
    MECHANISM_ACCOUNTING_MEANING,
    audit_is_complete_at_revision,
    audit_is_current,
    revision_mechanisms,
    domain_subfields,
    OUT,
    ROOT,
    PATTERN_ESTABLISHED_MIN,
    pattern_context_key,
    RLS_CLUSTERS,
    RLS_DIMENSIONS,
    compute_ddi,
    compute_rls,
    ddi_band,
    is_published,
    UNDER_RECOGNITION_MIN_GAP,
    is_under_recognized,
    recognition_gap_label,
    rls_band,
)

RLS_KEYS = tuple(k for k, _label, _w in RLS_DIMENSIONS)


# --------------------------------------------------------------------------
# Deterministic statistics (no external stats library; frozen definitions)
# --------------------------------------------------------------------------
def median(values: list[float]) -> float | None:
    """Median. Even n -> mean of the two central values. Deterministic."""
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return (s[mid - 1] + s[mid]) / 2


def quartiles(values: list[float]) -> dict[str, float | None]:
    """Inclusive quartiles (frozen definition, tested in test_domain_comparison.py).

    Sort; split at the median. For odd n the median element is included in BOTH
    halves; for even n the halves are the two contiguous halves. Q1/Q3 are the
    medians of the lower/upper halves. Example: [1,2,3,4,5] -> Q1=2, Q3=4.
    """
    if not values:
        return {"q1": None, "q3": None, "iqr": None, "min": None, "max": None}
    s = sorted(values)
    n = len(s)
    if n == 1:
        return {"q1": float(s[0]), "q3": float(s[0]), "iqr": 0.0, "min": float(s[0]), "max": float(s[0])}
    if n % 2 == 1:
        lower = s[: n // 2 + 1]
        upper = s[n // 2:]
    else:
        lower = s[: n // 2]
        upper = s[n // 2:]
    q1 = median(lower)
    q3 = median(upper)
    return {"q1": q1, "q3": q3, "iqr": (q3 - q1), "min": float(s[0]), "max": float(s[-1])}


# --------------------------------------------------------------------------
# Loading (sorted by slug -> order independent)
# --------------------------------------------------------------------------
def _load_cluster(cluster: str) -> list[dict[str, Any]]:
    folder = DATA / cluster
    if not folder.exists():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(folder.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            item = yaml.safe_load(f) or {}
        if is_published(item) and item.get("slug"):
            items.append(item)
    # dedupe by slug (no duplicate case counting) and sort deterministically
    by_slug: dict[str, dict[str, Any]] = {}
    for it in items:
        by_slug[str(it["slug"]).strip().strip("/")] = it
    return [by_slug[s] for s in sorted(by_slug)]


def _load_site() -> dict[str, Any]:
    with (DATA / "site.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _domain_cases(domain: str) -> list[dict[str, Any]]:
    cases = []
    for cluster in sorted(ASSESSMENT_CLUSTERS):
        for item in _load_cluster(cluster):
            if item.get("domain") == domain and isinstance(item.get("assessment"), dict):
                cases.append(item)
    return sorted(cases, key=lambda c: c["slug"])


def _domain_systems(domain: str) -> list[dict[str, Any]]:
    systems = []
    for cluster in sorted(RLS_CLUSTERS):
        for item in _load_cluster(cluster):
            if domain in (item.get("domains") or []) and isinstance(item.get("rls_assessment"), dict):
                systems.append(item)
    return sorted(systems, key=lambda s: s["slug"])


def _award_domains(item: dict[str, Any]) -> list[str]:
    """An award anatomy may serve one domain or several. Recognition systems have
    always carried `domains`; awards carried a single `domain` because every
    anatomy so far was a single-field prize. A multi-field award - one whose own
    fields span this project's governance domains - needs the plural, or its
    relations in one domain become invisible and its relations in another become
    mis-attributed."""
    if isinstance(item.get("domain"), str):
        return [item["domain"]]
    return [d for d in (item.get("domains") or []) if isinstance(d, str)]


def _domain_awards(domain: str) -> list[dict[str, Any]]:
    return [item for item in _load_cluster("awards") if domain in _award_domains(item)]


def _domain_award_relations(domain: str) -> list[dict[str, Any]]:
    """Hardened corpus relations only: interaction_type + claim + (anchor XOR exception).

    A relation is counted in the domain of the CASE it names, not of the award
    that carries it. For a single-domain award the two are the same. For an award
    whose fields cross domains they are not, and attributing a physics laureate's
    award outcome to a mathematics corpus would be a false count.
    """
    case_slugs = {c["slug"] for c in _domain_cases(domain)}
    rels = []
    for item in _load_cluster("awards"):
        if domain not in _award_domains(item):
            continue
        award = item["slug"]
        for rel in item.get("corpus_relations") or []:
            hardened = (
                isinstance(rel.get("interaction_type"), str)
                and isinstance(rel.get("claim"), str)
                and ((rel.get("record_anchor") is None) != (rel.get("exception") is None))
            )
            if hardened and rel.get("case") in case_slugs:
                rels.append({"award": award, **rel})
    return sorted(rels, key=lambda r: (r["award"], r["case"], r["interaction_type"]))


def _as_iso_date(value: Any) -> str | None:
    """Normalise a last_reviewed value (str or datetime.date) to YYYY-MM-DD."""
    if isinstance(value, str):
        v = value.strip()
        return v if len(v) == 10 and v[4] == "-" and v[7] == "-" else None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if hasattr(value, "isoformat") and not isinstance(value, (int, float)):
        try:
            return value.isoformat()[:10]
        except Exception:
            return None
    return None


def data_through(domain: str) -> str | None:
    """The corpus date: the most recent `last_reviewed` among the inputs actually
    included in this comparison (DDI cases, RLS systems, award entries).

    This is derived from the data, never from the clock: re-running the build on
    a later day cannot change it, and a changed date always means a changed
    review. Absent any dated input it is None rather than an invented date.
    """
    dates = []
    for item in (*_domain_cases(domain), *_domain_systems(domain), *_domain_awards(domain)):
        iso = _as_iso_date(item.get("last_reviewed"))
        if iso:
            dates.append(iso)
    return max(dates) if dates else None


def generated_at() -> str:
    """Operational metadata: when this process ran. Deliberately NOT part of the
    result, the snapshot identity, or any stable output - it is returned only on
    request, so a wall-clock value can never leak into a reproducible figure.
    """
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------------
# Aggregations (observations only)
# --------------------------------------------------------------------------
def corpus_distribution(domain: str) -> dict[str, Any]:
    cases = _domain_cases(domain)
    rows = []
    ddi_vals: list[float] = []
    obs_vals: list[float] = []
    gap_vals: list[float] = []
    ddi_bands: dict[str, int] = {}
    gap_bands: dict[str, int] = {}
    for c in cases:
        a = c["assessment"]
        ddi = compute_ddi(a)
        ddi_vals.append(ddi)
        ddi_bands[ddi_band(ddi)] = ddi_bands.get(ddi_band(ddi), 0) + 1
        obs = a.get("observed_recognition")
        row = {"slug": c["slug"], "title": c.get("title", c["slug"]),
               "url": f"/unawarded/{c['slug']}", "ddi": ddi, "band": ddi_band(ddi)}
        if isinstance(obs, (int, float)) and not isinstance(obs, bool):
            gap = ddi - obs
            obs_vals.append(obs)
            gap_vals.append(gap)
            row.update({"observed": obs, "gap": gap, "gap_reading": recognition_gap_label(gap)})
            gap_bands[recognition_gap_label(gap)] = gap_bands.get(recognition_gap_label(gap), 0) + 1
        rows.append(row)

    # Invariant: the gate requires observed_recognition on published DDI cases,
    # so every case must have a computable gap. Guard against silent drift.
    if len(gap_vals) != len(cases):
        raise AssertionError("gap denominator != case denominator (a case lacks a computable gap)")

    ranked = sorted(rows, key=lambda r: (-r.get("gap", float("-inf")), -r["ddi"], r["slug"]))
    gq = quartiles(gap_vals)
    # The two sides of the gap are reported separately, each with its own spread:
    # a gap can widen because assessments differ or because recognition differs,
    # and only the separated ranges let a reader see which varies in this corpus.
    return {
        "n_cases": len(cases),
        "median_ddi": median(ddi_vals),
        "median_observed_recognition": median(obs_vals),
        "median_gap": median(gap_vals),
        "ddi_min": min(ddi_vals) if ddi_vals else None,
        "ddi_max": max(ddi_vals) if ddi_vals else None,
        "ddi_spread": (max(ddi_vals) - min(ddi_vals)) if ddi_vals else None,
        "observed_min": min(obs_vals) if obs_vals else None,
        "observed_max": max(obs_vals) if obs_vals else None,
        "observed_spread": (max(obs_vals) - min(obs_vals)) if obs_vals else None,
        "gap_min": gq["min"], "gap_max": gq["max"],
        "gap_q1": gq["q1"], "gap_q3": gq["q3"], "gap_iqr": gq["iqr"],
        "ddi_band_counts": dict(sorted(ddi_bands.items())),
        "gap_band_counts": dict(sorted(gap_bands.items())),
        "ranked_cases": ranked,
    }


def pattern_distribution(domain: str) -> dict[str, Any]:
    cases = _domain_cases(domain)
    denom = len(cases)  # denominator = all DDI cases in the domain
    support: dict[str, list[dict[str, str]]] = {}
    for c in cases:
        evidence = c.get("pattern_evidence") or {}
        declared = c.get("pattern_context") or {}
        for pat in c.get("patterns") or []:
            if evidence.get(pat):  # evidence-backed only
                support.setdefault(pat, []).append({
                    "slug": c["slug"], "title": c.get("title", c["slug"]),
                    "url": f"/unawarded/{c['slug']}",
                    "context": pattern_context_key(c["slug"], declared.get(pat)),
                })
    patterns = []
    for pat in sorted(support):
        cs = sorted(support[pat], key=lambda x: x["slug"])
        n = len(cs)
        # Two observations are not two replications. Status is decided by how many
        # INDEPENDENT CONTEXTS exhibit the pattern, not by how many cases do; a
        # case that declares no shared context is its own context, so nothing
        # written before this rule moves.
        contexts = sorted({row["context"] for row in cs})
        shared = sorted({c for c in contexts if not c.startswith("case:")})
        independent = len(contexts)
        patterns.append({
            "pattern": pat,
            "support": n,
            "independent_support": independent,
            "contexts": contexts,
            "shared_contexts": shared,
            "regime_bounded": bool(shared) and independent < PATTERN_ESTABLISHED_MIN <= n,
            "denominator": denom,
            "corpus_percentage": round(100 * n / denom) if denom else 0,
            "status": "established" if independent >= PATTERN_ESTABLISHED_MIN else "emergent",
            "cases": cs,
        })
    patterns.sort(key=lambda p: (-p["support"], p["pattern"]))

    # Cases with a documented gap but no evidenced mechanism are counted, not
    # hidden: absence of evidence here means none was recorded in this corpus,
    # never that no mechanism operated.
    with_evidence = {c["slug"] for p in patterns for c in p["cases"]}
    without = sorted(
        (
            {"slug": c["slug"], "title": c.get("title", c["slug"]), "url": f"/unawarded/{c['slug']}",
             "audited": bool(c.get("mechanism_audit"))}
            for c in cases
            if c["slug"] not in with_evidence
        ),
        key=lambda x: x["slug"],
    )

    # Mechanism accounting: a case is *accounted for* when the corpus can say
    # something dated about its mechanism - either evidence for one, or a
    # documented audit that searched and found none. Cases that are neither are
    # simply not yet audited, and are reported as such rather than absorbed into
    # the "no mechanism" count. This measures how thoroughly the corpus has been
    # examined, which is a different question from how many mechanisms recur.
    audited = {c["slug"] for c in cases if isinstance(c.get("mechanism_audit"), dict)}
    accounted = sorted(with_evidence | audited)
    unaudited = sorted(
        (
            {"slug": c["slug"], "title": c.get("title", c["slug"]), "url": f"/unawarded/{c['slug']}"}
            for c in cases
            if c["slug"] not in with_evidence and c["slug"] not in audited
        ),
        key=lambda x: x["slug"],
    )

    # Two figures about the audits themselves, which the accounting percentage
    # above deliberately does not answer. Accounting asks whether each case was
    # examined at all. These ask how well:
    #
    #   * complete at revision - did the audit test everything that was
    #     audit-eligible on the day it ran? A "no" is a defect in the audit, and
    #     it is declared in the case file rather than inferred here.
    #   * current - does it cover the mechanism set in force today? A "no" is not
    #     a defect: the ontology grew afterwards. It is reported so that a reader
    #     can see how much of the corpus predates the present vocabulary, and it
    #     gates nothing. A closed domain does not reopen because a word was added.
    # Completeness is a fact about the ORIGINAL audit and never moves: it records
    # whether that search, on its day, tested everything then eligible. Currency
    # reads the latest statement of record, which is the re-audit where one
    # exists. Remediation is counted as its own third figure rather than folded
    # into either, because "was incomplete, later repaired" is a different claim
    # from "was complete" and the corpus must be able to say which it means.
    current_set = revision_mechanisms(CURRENT_ONTOLOGY_REVISION)
    audit_rows = []
    for c in cases:
        a = c.get("mechanism_audit")
        if not isinstance(a, dict):
            continue
        considered = [m for m in (a.get("considered") or []) if isinstance(m, str)]
        reaudit = c.get("mechanism_reaudit") if isinstance(c.get("mechanism_reaudit"), dict) else None
        latest = [m for m in ((reaudit or {}).get("considered") or considered) if isinstance(m, str)]
        untested_then = sorted(a.get("incomplete_at_revision") or [])
        audit_rows.append({
            "slug": c["slug"], "title": c.get("title", c["slug"]),
            "url": f"/unawarded/{c['slug']}",
            "ontology_revision": a.get("ontology_revision"),
            "complete_at_revision": audit_is_complete_at_revision(considered, a.get("ontology_revision")),
            "untested_at_revision": untested_then,
            "remediated": bool(untested_then and reaudit),
            "reaudit_date": (reaudit or {}).get("search_date"),
            "reaudit_revision": (reaudit or {}).get("ontology_revision"),
            "current": audit_is_current(latest),
            "untested_since_revision": sorted(current_set - set(latest)),
        })
    audit_rows.sort(key=lambda r: r["slug"])
    n_audits = len(audit_rows)
    n_complete = sum(1 for r in audit_rows if r["complete_at_revision"])
    n_current = sum(1 for r in audit_rows if r["current"])
    defects = [r for r in audit_rows if r["untested_at_revision"]]
    n_defects_remediated = sum(1 for r in defects if r["remediated"])

    # Co-occurrence: how often two evidenced mechanisms appear in the same case.
    # Descriptive only - a pair count says the record documents both in one case,
    # never that one mechanism produced the other.
    by_case: dict[str, list[str]] = {}
    for p in patterns:
        for c in p["cases"]:
            by_case.setdefault(c["slug"], []).append(p["pattern"])
    pair_counts: dict[tuple[str, str], int] = {}
    for pats in by_case.values():
        ordered = sorted(pats)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1
    co_occurrence = [
        {"pair": [a, b], "count": n, "denominator": denom}
        for (a, b), n in sorted(pair_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    return {
        "denominator": denom,
        "denominator_meaning": "DDI cases in this domain",
        "established_count": sum(1 for p in patterns if p["status"] == "established"),
        "patterns": patterns,
        "cases_without_evidenced_pattern": without,
        "n_cases_without_evidenced_pattern": len(without),
        "n_cases_audited": len(audited),
        "n_cases_accounted": len(accounted),
        "accounting_coverage_percentage": round(100 * len(accounted) / denom) if denom else 0,
        "cases_unaudited": unaudited,
        "accounting_meaning": MECHANISM_ACCOUNTING_MEANING,
        "audit_revisions": audit_rows,
        "n_audits": n_audits,
        "n_audits_complete_at_revision": n_complete,
        "n_audits_current": n_current,
        "current_ontology_revision": CURRENT_ONTOLOGY_REVISION,
        "audits_incomplete_at_revision": [r for r in audit_rows if not r["complete_at_revision"]],
        "audits_not_current": [r for r in audit_rows if not r["current"]],
        "n_historical_audit_defects": len(defects),
        "n_historical_audit_defects_remediated": n_defects_remediated,
        "audit_defects_outstanding": [r for r in defects if not r["remediated"]],
        "co_occurrence": co_occurrence,
    }



def concept_corpus_support(concept: str) -> dict[str, Any]:
    """How much of the governed corpus actually evidences one concept, measured
    across every aggregating domain.

    A concept page is the project's semantic authority, and until now nothing
    connected what it claimed to what the corpus held. A page could assert
    documented cases while the engine counted none, and the assertion was as
    permanent as the boilerplate that produced it. This function is what a page
    and the gate both read, so the claim and the count cannot drift apart.

    Only mechanisms can be evidenced by a case, so a concept of any other type
    returns zero by construction rather than by accident.
    """
    cases: list[dict[str, str]] = []
    domains: list[str] = []
    contexts: set[str] = set()
    for domain in PUBLISHED_SECTORS:
        for pattern in pattern_distribution(domain)["patterns"]:
            if pattern["pattern"] != concept:
                continue
            domains.append(domain)
            contexts |= set(pattern.get("contexts") or [])
            for case in pattern["cases"]:
                cases.append({**case, "domain": domain})
    cases.sort(key=lambda c: c["slug"])
    return {
        "concept": concept,
        "cases": cases,
        "n_cases": len(cases),
        "n_contexts": len(contexts),
        "contexts": sorted(contexts),
        "domains": sorted(set(domains)),
        "status": ("established" if len(contexts) >= PATTERN_ESTABLISHED_MIN
                   else "emergent" if cases else "unevidenced"),
    }

def rls_profiles(domain: str) -> dict[str, Any]:
    systems = _domain_systems(domain)
    profiles = []
    composites: list[float] = []
    for s in systems:
        a = s["rls_assessment"]
        composite = compute_rls(a)
        composites.append(composite)
        dims = {k: a.get(k) for k in RLS_KEYS}
        hi = max(dims, key=lambda k: dims[k]) if dims else None
        lo = min(dims, key=lambda k: dims[k]) if dims else None
        profiles.append({
            "slug": s["slug"], "title": s.get("title", s["slug"]),
            "composite": composite, "band": rls_band(composite),
            "dimensions": dims, "highest_dimension": hi, "lowest_dimension": lo,
        })
    dim_spread = {}
    for k in RLS_KEYS:
        vals = [p["dimensions"][k] for p in profiles if isinstance(p["dimensions"].get(k), (int, float))]
        if vals:
            dim_spread[k] = {"min": min(vals), "max": max(vals), "median": median(vals),
                             "spread": max(vals) - min(vals)}
    return {
        "n_systems": len(systems),
        "median_composite": median(composites),
        "composite_min": min(composites) if composites else None,
        "composite_max": max(composites) if composites else None,
        "dimension_spread": dim_spread,
        "profiles": profiles,
        "note": "Model results within the RLS v1.0 instrument, not absolute judgments of legitimacy.",
    }


def audit_eligible_concepts() -> list[str]:
    """Published concepts that can actually be tested against a case. An umbrella
    tendency or a framework distinction is not a candidate mechanism, so it must
    not be counted when reporting how much of the ontology a domain evidences."""
    return sorted(
        item["slug"] for item in _load_cluster("concepts")
        if item.get("concept_type") in AUDIT_ELIGIBLE_CONCEPT_TYPES
    )


_BAND_ORDER = [
    "significantly under-recognized",
    "under-recognized",
    "recognition roughly matches assessed merit",
    "recognition exceeds assessed merit",
    "recognition far exceeds assessed merit",
]


def explanatory_coverage(domain: str) -> dict[str, Any]:
    """How much of what needs explaining has been explained.

    "No evidenced mechanism" is the raw audit result, and on its own it is a poor
    measure: a case whose recognition roughly matches assessed merit has no
    deficit outstanding, so finding no mechanism there is the expected result,
    not a failure. This splits the corpus by the gap bands the site already
    publishes and reports mechanism coverage inside each - so the number that
    matters, unexplained UNDER-recognition, can never be inflated by cases that
    had nothing to explain.
    """
    cases = _domain_cases(domain)
    patterns = pattern_distribution(domain)
    with_mechanism = {c["slug"] for p in patterns["patterns"] for c in p["cases"]}

    rows: dict[str, dict[str, Any]] = {}
    unexplained_deficit: list[dict[str, str]] = []
    aligned_without_mechanism: list[dict[str, str]] = []
    n_under = 0
    for case in cases:
        assessment = case["assessment"]
        gap = compute_ddi(assessment) - assessment["observed_recognition"]
        band = recognition_gap_label(gap)
        row = rows.setdefault(band, {"band": band, "cases": 0, "with_mechanism": 0, "without_mechanism": 0})
        row["cases"] += 1
        entry = {"slug": case["slug"], "title": case.get("title", case["slug"]),
                 "url": f"/unawarded/{case['slug']}", "gap": gap}
        if case["slug"] in with_mechanism:
            row["with_mechanism"] += 1
        else:
            row["without_mechanism"] += 1
            (unexplained_deficit if is_under_recognized(gap) else aligned_without_mechanism).append(entry)
        if is_under_recognized(gap):
            n_under += 1

    # Bands are reported from the largest deficit downward, in the published order.
    ordered = [rows[band] for band in _BAND_ORDER if band in rows]

    return {
        "n_cases": len(cases),
        "n_under_recognized": n_under,
        "under_recognition_threshold": UNDER_RECOGNITION_MIN_GAP,
        "n_unexplained_under_recognition": len(unexplained_deficit),
        "unexplained_under_recognition": sorted(unexplained_deficit, key=lambda c: c["slug"]),
        "n_aligned_without_mechanism": len(aligned_without_mechanism),
        "aligned_without_mechanism": sorted(aligned_without_mechanism, key=lambda c: c["slug"]),
        "by_band": ordered,
        "eligible_concepts": audit_eligible_concepts(),
        "n_eligible_concepts": len(audit_eligible_concepts()),
        "n_evidenced_concepts": len(patterns["patterns"]),
        "note": ("A case whose recognition roughly matches assessed merit has no deficit outstanding; "
                 "finding no mechanism there is the expected result, not an explanatory failure."),
    }


def subfield_coverage(domain: str) -> dict[str, Any]:
    """For a composite domain, how the corpus is distributed across the halves of
    its own name.

    A domain can satisfy every numeric criterion while nearly all of its
    knowledge sits on one side of the join. This measures that directly. It is an
    observation and gates nothing: a domain maturity threshold does not by itself
    establish subfield coverage, and the point of computing it is that a maturity
    claim should have to say which half it rests on.
    """
    subfields = domain_subfields(domain)
    if not subfields:
        return {"composite": False, "subfields": [], "rows": [],
                "note": "This domain is not composite; subfield coverage does not apply."}

    cases = _domain_cases(domain)
    systems = _domain_systems(domain)
    awards = _domain_awards(domain)
    rows = []
    for name in subfields:
        rows.append({
            "subfield": name,
            "cases": sum(1 for c in cases if c.get("subfield") == name),
            "systems": sum(1 for s in systems if s.get("subfield") == name),
            "awards": sum(1 for a in awards if a.get("subfield") == name),
        })
    sided = [r for r in rows if r["subfield"] != "cross-cutting"]
    case_counts = [r["cases"] for r in sided]
    empty_sides = [r["subfield"] for r in sided if r["cases"] == 0]
    return {
        "composite": True,
        "subfields": list(subfields),
        "rows": rows,
        "n_cases": len(cases),
        "n_systems": len(systems),
        "cases_unassigned": sum(1 for c in cases if c.get("subfield") not in subfields),
        "sides_without_cases": empty_sides,
        "case_imbalance": (max(case_counts) - min(case_counts)) if case_counts else 0,
        "comparison_meaningful": not empty_sides,
        "note": ("Domain maturity threshold does not by itself establish subfield coverage. "
                 "These counts are reported, and gate nothing."),
    }


def award_interaction_distribution(domain: str) -> dict[str, Any]:
    rels = _domain_award_relations(domain)
    denom = len(rels)  # denominator = award relations, NOT cases
    by_type: dict[str, int] = {}
    for r in rels:
        by_type[r["interaction_type"]] = by_type.get(r["interaction_type"], 0) + 1
    distribution = [
        {"interaction_type": k, "count": v, "denominator": denom}
        for k, v in sorted(by_type.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    return {
        "denominator": denom,
        "denominator_meaning": "hardened award relations in this domain",
        "distribution": distribution,
    }


# --------------------------------------------------------------------------
# Snapshot identity (deterministic, data-derived, order-independent)
# --------------------------------------------------------------------------
def _snapshot_id(domain: str, site: dict[str, Any]) -> str:
    payload = {
        "methodology_version": site.get("methodology_version"),
        "rls_version": site.get("rls_version"),
        "cases": [
            {"slug": c["slug"], "assessment": c.get("assessment"),
             "patterns": sorted(c.get("patterns") or []),
             "pattern_evidence": c.get("pattern_evidence"),
             "mechanism_audit": c.get("mechanism_audit")}
            for c in _domain_cases(domain)
        ],
        "systems": [
            {"slug": s["slug"], "rls_assessment": s.get("rls_assessment")}
            for s in _domain_systems(domain)
        ],
        "award_relations": _domain_award_relations(domain),
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def _reference_form(domain: str, site: dict[str, Any]) -> str:
    """How a figure from this engine should be cited: corpus + methodology + date."""
    through = data_through(domain) or "undated"
    return (f"corpus {_snapshot_id(domain, site)} + methodology "
            f"{site.get('methodology_version')} + data through {through}")


def build_comparison(domain: str) -> dict[str, Any]:
    site = _load_site()
    corpus = corpus_distribution(domain)
    patterns = pattern_distribution(domain)
    systems = rls_profiles(domain)
    awards = award_interaction_distribution(domain)
    return {
        "population": {
            "domain": domain,
            "ddi_cases": corpus["n_cases"],
            "rls_systems": systems["n_systems"],
            "award_relations": awards["denominator"],
            "data_through": data_through(domain),
            "methodology_version": site.get("methodology_version"),
            "rls_version": site.get("rls_version"),
        },
        "corpus_snapshot": _snapshot_id(domain, site),
        "reference_form": _reference_form(domain, site),
        "limitations": [
            "The corpus is purposively built around recognition-gap cases; it is not a representative sample of the field.",
            "Corpus frequency is not field prevalence.",
            "Relations describe what the record connects, not why an outcome occurred.",
            "Denominators differ by layer: DDI cases, RLS systems, and award relations are distinct populations.",
        ],
        "observations": {
            "corpus_distribution": corpus,
            "structural_patterns": patterns,
            "explanatory_coverage": explanatory_coverage(domain),
            "subfield_coverage": subfield_coverage(domain),
            "recognition_system_profiles": systems,
            "award_interactions": awards,
        },
    }


def _fmt(v: Any) -> str:
    if isinstance(v, float):
        return f"{v:.1f}".rstrip("0").rstrip(".")
    return str(v)


def print_report(result: dict[str, Any]) -> None:
    pop = result["population"]
    print("ChampionsAwards - Domain comparison (observations only)")
    print("=" * 58)
    print(f"Comparison population: {pop['domain']}")
    print(f"  DDI cases: {pop['ddi_cases']} | RLS systems: {pop['rls_systems']} | award relations: {pop['award_relations']}")
    print(f"  methodology {pop['methodology_version']} / {pop['rls_version']} | snapshot {result['corpus_snapshot']} | data through {pop['data_through']}")

    c = result["observations"]["corpus_distribution"]
    print(f"\nCorpus distribution (n={c['n_cases']})")
    print(f"  median DDI {_fmt(c['median_ddi'])} | median observed {_fmt(c['median_observed_recognition'])} | median gap {_fmt(c['median_gap'])}")
    print(f"  gap min {_fmt(c['gap_min'])} Q1 {_fmt(c['gap_q1'])} Q3 {_fmt(c['gap_q3'])} max {_fmt(c['gap_max'])} (IQR {_fmt(c['gap_iqr'])})")
    print(f"  assessed DDI {_fmt(c['ddi_min'])}-{_fmt(c['ddi_max'])} (spread {_fmt(c['ddi_spread'])}) | "
          f"observed recognition {_fmt(c['observed_min'])}-{_fmt(c['observed_max'])} (spread {_fmt(c['observed_spread'])})")
    print(f"  DDI bands: {c['ddi_band_counts']}")
    print(f"  gap bands: {c['gap_band_counts']}")

    p = result["observations"]["structural_patterns"]
    print(f"\nStructural patterns (denominator {p['denominator']} {p['denominator_meaning']})")
    for pat in p["patterns"]:
        print(f"  {pat['pattern']}: {pat['support']}/{pat['denominator']} ({pat['corpus_percentage']}% of this corpus) [{pat['status']}]")
    if p["co_occurrence"]:
        print("  co-occurrence (same case, both evidenced):")
        for pair in p["co_occurrence"]:
            print(f"    {pair['pair'][0]} + {pair['pair'][1]}: {pair['count']}/{pair['denominator']}")
    print(f"  cases with a gap but no evidenced mechanism recorded: {p['n_cases_without_evidenced_pattern']}/{p['denominator']}")
    print(f"  mechanism accounting: {p['n_cases_accounted']}/{p['denominator']} "
          f"({p['accounting_coverage_percentage']}%) - evidenced or audited; "
          f"{len(p['cases_unaudited'])} not yet audited")

    e = result["observations"]["explanatory_coverage"]
    print(f"\nExplanatory coverage (gap bands as published)")
    for row in e["by_band"]:
        print(f"  {row['band']:44} {row['cases']:>2} cases | mechanism {row['with_mechanism']} | none {row['without_mechanism']}")
    print(f"  unexplained under-recognition (gap >= {_fmt(e['under_recognition_threshold'])}): "
          f"{e['n_unexplained_under_recognition']}/{e['n_under_recognized']}")
    print(f"  aligned, no mechanism needed: {e['n_aligned_without_mechanism']}")
    print(f"  audit-eligible concepts evidenced: {e['n_evidenced_concepts']}/{e['n_eligible_concepts']}")
    print("  (corpus frequency, not estimated prevalence in the field)")

    s = result["observations"]["recognition_system_profiles"]
    print(f"\nRecognition-system profiles (n={s['n_systems']}, median RLS {_fmt(s['median_composite'])}, range {_fmt(s['composite_min'])}-{_fmt(s['composite_max'])})")
    for pr in s["profiles"]:
        print(f"  {pr['title']}: RLS {pr['composite']} [{pr['band']}] hi={pr['highest_dimension']} lo={pr['lowest_dimension']}")
    print("  dimension spread (max-min across systems):")
    for k, sp in s["dimension_spread"].items():
        print(f"    {k}: {sp['min']}-{sp['max']} (spread {sp['spread']})")

    sc = result["observations"]["subfield_coverage"]
    if sc["composite"]:
        print(f"\nSubfield coverage (composite domain)")
        for row in sc["rows"]:
            print(f"  {row['subfield']:16} cases {row['cases']:>2} | systems {row['systems']:>2} | awards {row['awards']:>2}")
        if sc["sides_without_cases"]:
            print(f"  sides with no cases: {', '.join(sc['sides_without_cases'])}")
        print(f"  cross-domain comparison meaningful: {'yes' if sc['comparison_meaningful'] else 'not yet'}")
        print(f"  ({sc['note']})")

    a = result["observations"]["award_interactions"]
    print(f"\nAward interactions (denominator {a['denominator']} {a['denominator_meaning']})")
    for d in a["distribution"]:
        print(f"  {d['interaction_type']}: {d['count']}/{d['denominator']}")


REPORTS: Path = ROOT / "reports"


def write_report(result: dict[str, Any], domain: str) -> Path | None:
    """Write the build-internal JSON report.

    It lands in `reports/`, never in OUT (`public/`): this artifact is for
    inspection, diffing and tests - not an endpoint. Publishing one is a separate
    decision that has not been taken. `generated_at` is written into a sibling run-log rather than the
    report, so the report stays byte-identical across runs of the same corpus.
    """
    path = REPORTS / f"{domain}-comparison.json"
    try:
        REPORTS.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
        with (REPORTS / "last-run.txt").open("w", encoding="utf-8") as f:
            f.write(f"{domain} generated_at={generated_at()} snapshot={result['corpus_snapshot']}\n")
    except OSError:
        return None
    return path


def main() -> None:
    domain = "physics-astronomy"
    result = build_comparison(domain)
    print_report(result)
    path = write_report(result, domain)
    if path is not None:
        assert OUT not in path.parents, "comparison report must not be written under the site output directory"
        print(f"\nBuild-internal report: {path.relative_to(ROOT)}  (not published; no data endpoint is exposed)")


if __name__ == "__main__":
    main()
