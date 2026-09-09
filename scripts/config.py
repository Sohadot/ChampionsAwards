from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parent.parent
SRC: Final[Path] = ROOT / "src"
DATA: Final[Path] = SRC / "data"
TEMPLATES: Final[Path] = SRC / "templates"
OUT: Final[Path] = ROOT / "public"

CORE_PAGES: Final[dict[str, str]] = {
    "index.html": "index.html",
    "protocol.html": "protocol/index.html",
    "framework.html": "framework/index.html",
    "methodology.html": "methodology/index.html",
    "calculator.html": "calculator/index.html",
    "about.html": "about/index.html",
}

CORE_URLS: Final[list[str]] = [
    "/",
    "/protocol",
    "/framework",
    "/methodology",
    "/calculator",
    "/rankings",
    "/about",
]

# Note: /rankings is a computed aggregate page (generate_rankings.py), not a
# data cluster, so it deliberately does not appear in CLUSTERS below.
CLUSTERS: Final[dict[str, str]] = {
    "awards": "award.html",
    "recognition-systems": "recognition-system.html",
    "concepts": "concept.html",
    "unawarded": "unawarded.html",
    "sectors": "sector.html",
    "reports": "report.html",
    "timeline": "timeline.html",
}

HUB_TITLES: Final[dict[str, str]] = {
    "awards": "Awards",
    "recognition-systems": "Recognition Systems",
    "concepts": "Concepts",
    "unawarded": "The Unawarded Archive",
    "sectors": "Sectors",
    "reports": "Reports",
    "timeline": "Timeline",
}

REQUIRED_FIELDS_BY_CLUSTER: Final[dict[str, tuple[str, ...]]] = {
    "awards": ("title", "slug", "summary"),
    "recognition-systems": ("title", "slug", "summary"),
    "concepts": ("title", "slug", "summary"),
    "unawarded": ("title", "slug", "summary"),
    "sectors": ("title", "slug", "summary"),
    "reports": ("title", "slug", "summary"),
    "timeline": ("title", "slug", "summary"),
}

MIN_SUMMARY_LENGTH: Final[int] = 80
MAX_SLUG_LENGTH: Final[int] = 120
SLUG_PATTERN: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def normalize_slug(raw_slug: str) -> str:
    return raw_slug.strip().strip("/")


def is_valid_slug(slug: str) -> bool:
    if not slug:
        return False
    if len(slug) > MAX_SLUG_LENGTH:
        return False
    return bool(SLUG_PATTERN.fullmatch(slug))


def normalize_domain(domain: str) -> str:
    return domain.rstrip("/")


# ---------------------------------------------------------------------------
# Deservingness Index (DDI v1.0)
# The single source of truth for scoring, mirrored by the client-side
# calculator in src/core/calculator.html and documented at /methodology.
# Weights MUST sum to 1.00.
# ---------------------------------------------------------------------------
DDI_VERSION: Final[str] = "DDI v1.0"

DDI_DIMENSIONS: Final[tuple[tuple[str, str, float], ...]] = (
    ("impact", "Structural impact", 0.28),
    ("verification", "Independent verification", 0.20),
    ("uniqueness", "Counterfactual uniqueness", 0.16),
    ("durability", "Temporal durability", 0.16),
    ("breadth", "Breadth of benefit", 0.12),
    ("attribution", "Transparency of attribution", 0.08),
)

DDI_KEYS: Final[tuple[str, ...]] = tuple(key for key, _label, _weight in DDI_DIMENSIONS)


def _clamp_score(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def compute_ddi(assessment: dict) -> float:
    """Weighted sum of the six dimension scores (0-100)."""
    total = 0.0
    for key, _label, weight in DDI_DIMENSIONS:
        total += _clamp_score(assessment.get(key, 0)) * weight
    return round(total)


def ddi_band(score: float) -> str:
    if score >= 85:
        return "Landmark"
    if score >= 70:
        return "Major"
    if score >= 55:
        return "Substantial"
    if score >= 40:
        return "Moderate"
    return "Limited"


def recognition_gap_label(gap: float) -> str:
    if gap >= 25:
        return "significantly under-recognized"
    if gap >= 10:
        return "under-recognized"
    if gap > -10:
        return "recognition roughly matches assessed merit"
    if gap > -25:
        return "recognition exceeds assessed merit"
    return "recognition far exceeds assessed merit"


# ---------------------------------------------------------------------------
# Recognition Legitimacy Score (RLS v1.0)
# The companion instrument to the DDI: it scores *systems* (prizes, honors,
# ranking bodies) rather than individuals. Mirrored by the client-side
# calculator and documented at /methodology. Weights MUST sum to 1.00.
# ---------------------------------------------------------------------------
RLS_VERSION: Final[str] = "RLS v1.0"

RLS_DIMENSIONS: Final[tuple[tuple[str, str, float], ...]] = (
    ("process", "Process integrity", 0.25),
    ("breadth", "Representational breadth", 0.20),
    ("track_record", "Historical track record", 0.20),
    ("transparency", "Transparency", 0.18),
    ("independence", "Independence", 0.17),
)

RLS_KEYS: Final[tuple[str, ...]] = tuple(key for key, _label, _weight in RLS_DIMENSIONS)


def compute_rls(assessment: dict) -> float:
    """Weighted sum of the five legitimacy dimension scores (0-100)."""
    total = 0.0
    for key, _label, weight in RLS_DIMENSIONS:
        total += _clamp_score(assessment.get(key, 0)) * weight
    return round(total)


def rls_band(score: float) -> str:
    if score >= 85:
        return "Exemplary"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Adequate"
    if score >= 40:
        return "Contested"
    return "Fragile"


# ---------------------------------------------------------------------------
# Editorial governance
# validate_content.py checks well-formedness; quality_gate.py enforces the
# publication policy below on entries that declare themselves published.
# ---------------------------------------------------------------------------
VALID_STATUSES: Final[frozenset[str]] = frozenset({"published", "draft"})
DEFAULT_STATUS: Final[str] = "published"

# Type boundaries for the two instruments (see /methodology):
#   - the DDI scores individual contributions;
#   - the RLS scores recognition systems.
# A misplaced assessment block is a modeling error, not a formatting one, so the
# quality gate rejects it regardless of publication status. The rankings
# generator also honors these sets as defense in depth.
ASSESSMENT_CLUSTERS: Final[frozenset[str]] = frozenset({"unawarded"})
RLS_CLUSTERS: Final[frozenset[str]] = frozenset({"recognition-systems"})

# A published DDI assessment must state observed_recognition, because the
# Recognition Gap Index is only meaningful when the gap is computable.
REQUIRE_OBSERVED_RECOGNITION: Final[bool] = True

# ---------------------------------------------------------------------------
# Domains (recognition domains)
# ChampionsAwards deepens one domain at a time to maturity rather than growing
# horizontally. Every scored individual carries a single `domain`; every scored
# system carries `domains` (a list), because a prize can span fields.
# ---------------------------------------------------------------------------
DOMAINS: Final[dict[str, str]] = {
    "physics-astronomy": "Physics & Astronomy",
    "biology-medicine": "Biology & Medicine",
    "mathematics-computing": "Mathematics & Computing",
}

# Published scored entries must be placed in a domain (no orphans).
REQUIRE_DOMAIN: Final[bool] = True

# A case only counts toward a structural pattern when it carries explicit
# `pattern_evidence` for that pattern (source refs proving the mechanism, not
# merely the tag). Published cases must supply evidence for every pattern.
REQUIRE_PATTERN_EVIDENCE: Final[bool] = True

# Pattern lifecycle: a structural cause is only "established" in a domain once
# at least this many independent cases in that domain exhibit it. A pattern
# supported by a single case is "emergent" and does NOT count toward the DoD.
# This prevents inventing labels just to reach a threshold.
PATTERN_ESTABLISHED_MIN: Final[int] = 2

# Definition of Done for declaring a domain "mature v1.0". A domain is closed
# only when every threshold is met; domain_status.py reports progress and the
# criteria that remain. These are practical thresholds, not scientific limits.
DOMAIN_DOD: Final[dict[str, int]] = {
    "ddi_cases": 10,      # individual contributions scored with the DDI
    "rls_systems": 3,     # recognition systems scored with the RLS
    "patterns": 4,        # ESTABLISHED structural-cause concepts (>= PATTERN_ESTABLISHED_MIN cases)
}


def is_valid_domain(domain: str) -> bool:
    return domain in DOMAINS

# ISO 8601 date, e.g. 2026-09-08
ISO_DATE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Published entries must be reviewed at least this recently to stay published.
# (Enforced as a presence + validity check; staleness is a soft warning.)
REQUIRE_SOURCES: Final[bool] = True
REQUIRE_LAST_REVIEWED: Final[bool] = True

# Neutrality discipline: unscoped superlatives the editorial protocol bans in
# entry prose. Matched case-insensitively as whole phrases.
BANNED_TERMS: Final[tuple[str, ...]] = (
    "sovereign-grade",
    "definitive",
    "the greatest",
    "world's greatest",
    "unrivaled",
    "unrivalled",
    "unquestionably",
    "indisputably",
    "flawless",
    "perfect record",
    "best in the world",
    "world's leading",
    "without equal",
    "beyond dispute",
)

# Entry string fields scanned for banned terms and depth.
PROSE_FIELDS: Final[tuple[str, ...]] = (
    "summary",
    "introduction",
    "definition",
    "explanation",
    "implications",
    "legitimacy_question",
    "structural_notes",
    "omission_case",
    "structural_reason",
    "power_structure",
    "selection_logic",
)


# ---------------------------------------------------------------------------
# Source authority taxonomy
# Function, not rank: a primary paper is not automatically "better" than an
# institutional record for every question. The type says what KIND of record a
# source is, so the provenance audit can ask whether a claim is anchored to a
# record-grade source or rests on a secondary account.
# ---------------------------------------------------------------------------
SOURCE_TYPES: Final[frozenset[str]] = frozenset(
    {
        "primary",              # the original paper, letter, contemporary record, or founding decision
        "archival",             # a university/institution/society archive preserving the historical record
        "institutional",        # an institution describing its own record or awards (Nobel, CERN, Royal Society...)
        "scholarly-secondary",  # peer-reviewed history-of-science or academic study
        "reference-secondary",  # Britannica, MacTutor, and similar reference works
        "general-secondary",    # a reputable editorial source that is not the record bearing the claim
    }
)

# Record-grade tiers can anchor a load-bearing claim to a record; the secondary
# tiers are accounts of it. Used by source_audit.py, never to auto-change a score.
RECORD_GRADE_SOURCE_TYPES: Final[frozenset[str]] = frozenset(
    {"primary", "archival", "institutional"}
)

REQUIRE_SOURCE_TYPE: Final[bool] = True


def is_valid_source_type(value: object) -> bool:
    return isinstance(value, str) and value in SOURCE_TYPES


def get_status(item: dict) -> str:
    raw = item.get("status")
    status = str(raw).strip().lower() if raw is not None else DEFAULT_STATUS
    return status if status in VALID_STATUSES else DEFAULT_STATUS


def is_published(item: dict) -> bool:
    return get_status(item) == "published"


def is_iso_date(value: object) -> bool:
    # PyYAML parses unquoted YYYY-MM-DD as a datetime.date; accept both forms.
    if isinstance(value, date):
        return True
    return isinstance(value, str) and bool(ISO_DATE_PATTERN.fullmatch(value.strip()))


def find_banned_terms(item: dict) -> list[str]:
    hits: list[str] = []
    for field in PROSE_FIELDS:
        value = item.get(field)
        if not isinstance(value, str):
            continue
        haystack = value.lower()
        for term in BANNED_TERMS:
            if term in haystack:
                hits.append(f"{field}: \"{term}\"")
    return hits
