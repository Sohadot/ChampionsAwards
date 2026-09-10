"""Sector reference pages: /sectors/<domain>.

A sector page is a *representation*, never a second calculation. Every figure on
it comes from the canonical engine (domain_comparison.build_comparison) at build
time; nothing here recomputes a median, a denominator, or a pattern count, and
nothing is hand-transcribed. The engine's JSON report stays build-internal
(reports/), so this HTML page is the published form - not a data endpoint.

Prose discipline: the page states no finding that is not literally derived from
the engine's numbers. Every sentence below that reads like a claim is built from
engine values with its denominator attached ("8 of 10 governed cases exhibit
evidenced credit misattribution"), never generalised into a claim about the
field. Corpus frequency is not field prevalence.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import (
    DDI_DIMENSIONS,
    DOMAIN_DOD,
    DOMAINS,
    DATA,
    OUT,
    PATTERN_ESTABLISHED_MIN,
    PUBLISHED_SECTORS,
    RLS_DIMENSIONS,
    TEMPLATES,
    BANNED_TERMS,
    normalize_domain,
)
from domain_comparison import _domain_awards, build_comparison
from generate_pages import attach_award_architecture, build_case_index

# PUBLISHED_SECTORS (config.py) lists the domains with a sector page. A sector
# page exists only for a domain whose corpus is actually governed; it is
# generated, never authored.

# Interaction types split into what the record positively documents versus what
# it shows as a rule-bound limit or a non-event. The split is presentational;
# the vocabulary itself lives in config.INTERACTION_TYPES.
OUTCOME_TYPES = {"documented-award-outcome", "documented-nomination", "archival-selection-record"}

# Words that would turn a corpus count into a claim about the field or a cause.
# A generated reading may say "8 of 10 governed cases exhibit evidenced credit
# misattribution"; it may not say that the mechanism is dominant, typical, or
# proven. Checked at build time, so the discipline is enforced, not remembered.
GENERALISATION_TERMS: tuple[str, ...] = (
    "dominant", "dominates", "most common", "typical", "typically", "usually",
    "in general", "prevalent", "prevalence", "proves", "proven", "demonstrates that",
    "shows that physics", "across the field", "widespread",
)


def concept_slugs() -> set[str]:
    """Mechanism names that have a published concept page, so the sector page
    links a mechanism only where an entry actually exists."""
    folder = DATA / "concepts"
    slugs: set[str] = set()
    if not folder.exists():
        return slugs
    for path in sorted(folder.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            item = yaml.safe_load(f) or {}
        if str(item.get("status", "published")).strip().lower() == "published" and item.get("slug"):
            slugs.add(str(item["slug"]).strip().strip("/"))
    return slugs


def domain_reports(domain: str) -> list[dict[str, Any]]:
    """Published synthesis reports derived from this domain, so the sector page
    links its own layer 7 rather than leaving it undiscoverable."""
    folder = DATA / "reports"
    reports: list[dict[str, Any]] = []
    if not folder.exists():
        return reports
    for path in sorted(folder.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            item = yaml.safe_load(f) or {}
        if str(item.get("status", "published")).strip().lower() != "published":
            continue
        if item.get("derives_from") == domain and item.get("slug"):
            reports.append({"title": item.get("title", item["slug"]),
                            "url": f"/reports/{str(item['slug']).strip().strip('/')}"})
    return reports


def load_site() -> dict[str, Any]:
    with (DATA / "site.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def create_environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # One number formatter for the whole page, so a median reads 26.5 and an
    # interquartile range reads 15 rather than 15.0. Formatting only - the value
    # itself is never rounded away from what the engine computed.
    env.filters["num"] = _fmt
    return env


def _fmt(value: Any) -> str:
    """Numbers as they should read: 26.5 stays 26.5, 15.0 becomes 15."""
    if isinstance(value, float):
        return f"{value:.1f}".rstrip("0").rstrip(".")
    return str(value)


# --------------------------------------------------------------------------
# Gap distribution figure: a real distribution, drawn from the actual values.
# Deterministic geometry (no jitter, no randomness): equal values stack upward
# in slug order, so the same corpus always draws the same picture.
# --------------------------------------------------------------------------
def gap_figure(corpus: dict[str, Any]) -> dict[str, Any]:
    rows = [r for r in corpus["ranked_cases"] if "gap" in r]
    if not rows:
        return {}
    width, height = 720, 188
    left, right = 46, 24
    lo = 5 * math.floor(min(r["gap"] for r in rows) / 5) - 5
    hi = 5 * math.ceil(max(r["gap"] for r in rows) / 5) + 5
    span = hi - lo or 1

    def x(value: float) -> float:
        return round(left + (value - lo) / span * (width - left - right), 2)

    baseline = 128
    seen: dict[float, int] = {}
    points = []
    for row in sorted(rows, key=lambda r: r["slug"]):
        stack = seen.get(row["gap"], 0)
        seen[row["gap"]] = stack + 1
        points.append({
            "cx": x(row["gap"]),
            "cy": baseline - stack * 15,
            "title": row["title"],
            "gap": _fmt(row["gap"]),
            "url": row["url"],
        })
    ticks = [{"x": x(v), "label": v} for v in range(int(lo), int(hi) + 1, 5)]
    return {
        "width": width, "height": height,
        "box_x": x(corpus["gap_q1"]), "box_w": round(x(corpus["gap_q3"]) - x(corpus["gap_q1"]), 2),
        "box_y": 46, "box_h": 42,
        "median_x": x(corpus["median_gap"]),
        "whisker_lo": x(corpus["gap_min"]), "whisker_hi": x(corpus["gap_max"]),
        "whisker_y": 67,
        "axis_y": baseline + 20,
        "ticks": ticks,
        "points": points,
    }


# --------------------------------------------------------------------------
# Engine-derived readings. Each function returns a sentence whose every number
# comes from the engine, with the denominator kept inside the sentence.
# --------------------------------------------------------------------------
def gap_reading(corpus: dict[str, Any]) -> str:
    return (
        f"Across the {corpus['n_cases']} governed cases the median recognition gap is "
        f"{_fmt(corpus['median_gap'])} points (assessed DDI minus observed recognition). "
        f"The middle half of the cases falls between {_fmt(corpus['gap_q1'])} and "
        f"{_fmt(corpus['gap_q3'])} (IQR {_fmt(corpus['gap_iqr'])}); the observed range is "
        f"{_fmt(corpus['gap_min'])} to {_fmt(corpus['gap_max'])}. "
        f"Median assessed DDI is {_fmt(corpus['median_ddi'])} against a median observed "
        f"recognition of {_fmt(corpus['median_observed_recognition'])}."
    )


def pattern_readings(patterns: dict[str, Any]) -> list[str]:
    established = [p for p in patterns["patterns"] if p["status"] == "established"]
    emergent = [p for p in patterns["patterns"] if p["status"] == "emergent"]
    lines: list[str] = []
    for index, pattern in enumerate(established):
        label = pattern["pattern"].replace("-", " ")
        rank = " — the highest support count in this corpus" if index == 0 else ""
        lines.append(
            f"{pattern['support']} of {pattern['denominator']} governed cases exhibit evidenced "
            f"{label}{rank}."
        )
    if emergent:
        names = ", ".join(p["pattern"].replace("-", " ") for p in emergent)
        lines.append(
            f"Recorded in a single case each and therefore not counted as established "
            f"(threshold: {PATTERN_ESTABLISHED_MIN} independent cases): {names}."
        )
    return lines


def rls_reading(systems: dict[str, Any]) -> str:
    spread = systems["dimension_spread"]
    widest = max(spread, key=lambda k: (spread[k]["spread"], k)) if spread else None
    text = (
        f"The {systems['n_systems']} recognition systems scored for this domain range from "
        f"RLS {_fmt(systems['composite_min'])} to {_fmt(systems['composite_max'])}, median "
        f"{_fmt(systems['median_composite'])}."
    )
    if widest:
        s = spread[widest]
        text += (
            f" The dimension that separates them most is {widest.replace('_', ' ')}: "
            f"{_fmt(s['min'])} to {_fmt(s['max'])} (spread {_fmt(s['spread'])})."
        )
    return text


def award_reading(awards: dict[str, Any], n_awards: int) -> str:
    parts = [f"{d['interaction_type'].replace('-', ' ')} {d['count']}/{d['denominator']}"
             for d in awards["distribution"]]
    return (
        f"{awards['denominator']} hardened relations connect the governed cases to "
        f"{n_awards} mapped award{'s' if n_awards != 1 else ''}: " + "; ".join(parts) + "."
    )


# --------------------------------------------------------------------------
# View model
# --------------------------------------------------------------------------
def build_sector(domain: str, site: dict[str, Any]) -> dict[str, Any]:
    result = build_comparison(domain)
    corpus = result["observations"]["corpus_distribution"]
    patterns = result["observations"]["structural_patterns"]
    systems = result["observations"]["recognition_system_profiles"]
    awards = result["observations"]["award_interactions"]

    # Case matrix: join the ranked cases with their evidenced patterns, so a
    # pattern appears against a case only where the case carries evidence for it.
    case_patterns: dict[str, list[str]] = {}
    for pattern in patterns["patterns"]:
        for case in pattern["cases"]:
            case_patterns.setdefault(case["slug"], []).append(pattern["pattern"].replace("-", " "))
    matrix = [{**row, "patterns": sorted(case_patterns.get(row["slug"], []))}
              for row in corpus["ranked_cases"]]

    # Award architecture, read from the award entries themselves (the same
    # rendering the award pages use), split into documented outcomes and
    # rule-bound constraints / non-award records.
    case_index = build_case_index()
    award_entries = []
    for entry in _domain_awards(domain):
        attach_award_architecture(entry, case_index)
        relations = entry.get("corpus_relation_rows") or []
        award_entries.append({
            "title": entry.get("title", entry["slug"]),
            "url": f"/awards/{entry['slug']}",
            "summary": entry.get("summary"),
            "architecture_rows": entry.get("architecture_rows") or [],
            "outcomes": [r for r in relations if r["interaction"] in OUTCOME_TYPES],
            "constraints": [r for r in relations if r["interaction"] not in OUTCOME_TYPES],
        })

    # Maturity is reported as measured, not as desired.
    measured = {"ddi_cases": corpus["n_cases"], "rls_systems": systems["n_systems"],
                "patterns": patterns["established_count"]}
    dod_rows = [{"requirement": key.replace("_", " "), "have": measured.get(key, 0), "need": need,
                 "met": measured.get(key, 0) >= need}
                for key, need in DOMAIN_DOD.items()]

    # RLS systems are shown in a fixed alphabetical order, never ranked: the page
    # presents profiles, not a podium.
    profiles = sorted(systems["profiles"], key=lambda p: p["title"])
    rls_labels = {key: label for key, label, _weight in RLS_DIMENSIONS}

    return {
        "domain": domain,
        "pattern_min": PATTERN_ESTABLISHED_MIN,
        "concept_slugs": concept_slugs(),
        "reports": domain_reports(domain),
        "domain_label": DOMAINS.get(domain, domain),
        "url": f"/sectors/{domain}",
        "canonical_url": f"{normalize_domain(site['domain'])}/sectors/{domain}",
        "population": result["population"],
        "corpus_snapshot": result["corpus_snapshot"],
        "reference_form": result["reference_form"],
        "limitations": result["limitations"],
        "corpus": corpus,
        "figure": gap_figure(corpus),
        "gap_reading": gap_reading(corpus),
        "patterns": patterns,
        "pattern_readings": pattern_readings(patterns),
        "systems": systems,
        "profiles": profiles,
        "rls_labels": rls_labels,
        "rls_reading": rls_reading(systems),
        "awards": awards,
        "award_entries": award_entries,
        "award_reading": award_reading(awards, len(award_entries)),
        "dod_rows": dod_rows,
        "mature": all(row["met"] for row in dod_rows),
        "ddi_dimensions": [{"label": label, "weight": weight} for _k, label, weight in DDI_DIMENSIONS],
        "matrix": matrix,
    }


def generated_readings(sector: dict[str, Any]) -> list[str]:
    return [sector["gap_reading"], sector["rls_reading"], sector["award_reading"], *sector["pattern_readings"]]


def lint_generated_prose(sector: dict[str, Any]) -> list[str]:
    """The neutrality lint applies to generated prose too: a computed page is not
    exempt from the protocol that governs authored entries. Beyond the site-wide
    banned superlatives, a generated reading may not generalise a corpus count
    into a claim about the field or into a cause."""
    hits = []
    for text in generated_readings(sector):
        lowered = text.lower()
        for term in BANNED_TERMS:
            if term in lowered:
                hits.append(f'banned superlative "{term}" in: {text[:70]}...')
        for term in GENERALISATION_TERMS:
            if term in lowered:
                hits.append(f'generalisation "{term}" in: {text[:70]}...')
    return hits


def main() -> None:
    site = load_site()
    env = create_environment()
    domain_root = normalize_domain(site["domain"])
    common = {
        "site": site,
        "build_year": datetime.now(timezone.utc).year,
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    sectors = []
    for domain in PUBLISHED_SECTORS:
        sector = build_sector(domain, site)
        problems = lint_generated_prose(sector)
        if problems:
            print("Sector generation failed (neutrality lint):")
            for problem in problems:
                print(f"  - {problem}")
            raise SystemExit(1)
        html = env.get_template("sector.html").render(**common, sector=sector)
        path = OUT / "sectors" / domain / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        sectors.append(sector)
        print(
            f"Sector: /sectors/{domain} | cases {sector['corpus']['n_cases']} | "
            f"systems {sector['systems']['n_systems']} | relations {sector['awards']['denominator']} | "
            f"snapshot {sector['corpus_snapshot']}"
        )

    hub = OUT / "sectors" / "index.html"
    hub.parent.mkdir(parents=True, exist_ok=True)
    hub.write_text(
        env.get_template("sectors-hub.html").render(
            **common, sectors=sectors, hub_canonical_url=f"{domain_root}/sectors"
        ),
        encoding="utf-8",
    )
    print(f"Sector hub generated. Published sectors: {len(sectors)}.")


if __name__ == "__main__":
    main()
