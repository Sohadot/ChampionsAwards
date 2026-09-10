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
Cycle 01 defers public data export / API, so the JSON report is a build-internal
artifact under `reports/` and the sector page calls `build_comparison()` at build
time and renders HTML. Nothing here creates a machine-readable public endpoint.
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
    DATA,
    OUT,
    ROOT,
    PATTERN_ESTABLISHED_MIN,
    RLS_CLUSTERS,
    RLS_DIMENSIONS,
    compute_ddi,
    compute_rls,
    ddi_band,
    is_published,
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


def _domain_awards(domain: str) -> list[dict[str, Any]]:
    return [item for item in _load_cluster("awards") if item.get("domain") == domain]


def _domain_award_relations(domain: str) -> list[dict[str, Any]]:
    """Hardened corpus relations only: interaction_type + claim + (anchor XOR exception)."""
    rels = []
    for item in _load_cluster("awards"):
        if item.get("domain") != domain:
            continue
        award = item["slug"]
        for rel in item.get("corpus_relations") or []:
            hardened = (
                isinstance(rel.get("interaction_type"), str)
                and isinstance(rel.get("claim"), str)
                and ((rel.get("record_anchor") is None) != (rel.get("exception") is None))
            )
            if hardened:
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
        for pat in c.get("patterns") or []:
            if evidence.get(pat):  # evidence-backed only
                support.setdefault(pat, []).append(
                    {"slug": c["slug"], "title": c.get("title", c["slug"]), "url": f"/unawarded/{c['slug']}"}
                )
    patterns = []
    for pat in sorted(support):
        cs = sorted(support[pat], key=lambda x: x["slug"])
        n = len(cs)
        patterns.append({
            "pattern": pat,
            "support": n,
            "denominator": denom,
            "corpus_percentage": round(100 * n / denom) if denom else 0,
            "status": "established" if n >= PATTERN_ESTABLISHED_MIN else "emergent",
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
        "co_occurrence": co_occurrence,
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
    print("  (corpus frequency, not estimated prevalence in the field)")

    s = result["observations"]["recognition_system_profiles"]
    print(f"\nRecognition-system profiles (n={s['n_systems']}, median RLS {_fmt(s['median_composite'])}, range {_fmt(s['composite_min'])}-{_fmt(s['composite_max'])})")
    for pr in s["profiles"]:
        print(f"  {pr['title']}: RLS {pr['composite']} [{pr['band']}] hi={pr['highest_dimension']} lo={pr['lowest_dimension']}")
    print("  dimension spread (max-min across systems):")
    for k, sp in s["dimension_spread"].items():
        print(f"    {k}: {sp['min']}-{sp['max']} (spread {sp['spread']})")

    a = result["observations"]["award_interactions"]
    print(f"\nAward interactions (denominator {a['denominator']} {a['denominator_meaning']})")
    for d in a["distribution"]:
        print(f"  {d['interaction_type']}: {d['count']}/{d['denominator']}")


REPORTS: Path = ROOT / "reports"


def write_report(result: dict[str, Any], domain: str) -> Path | None:
    """Write the build-internal JSON report.

    It lands in `reports/`, never in OUT (`public/`): Cycle 01 defers public data
    export and APIs, so this artifact is for inspection, diffing and tests - not
    an endpoint. `generated_at` is written into a sibling run-log rather than the
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
        print(f"\nBuild-internal report: {path.relative_to(ROOT)}  (not published; Cycle 01 defers data export)")


if __name__ == "__main__":
    main()
