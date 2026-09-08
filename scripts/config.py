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
    "/about",
]

CLUSTERS: Final[dict[str, str]] = {
    "awards": "award.html",
    "recognition-systems": "recognition-system.html",
    "concepts": "concept.html",
    "unawarded": "unawarded.html",
    "sectors": "sector.html",
    "rankings": "ranking.html",
    "reports": "report.html",
    "timeline": "timeline.html",
}

HUB_TITLES: Final[dict[str, str]] = {
    "awards": "Awards",
    "recognition-systems": "Recognition Systems",
    "concepts": "Concepts",
    "unawarded": "The Unawarded Archive",
    "sectors": "Sectors",
    "rankings": "Rankings",
    "reports": "Reports",
    "timeline": "Timeline",
}

REQUIRED_FIELDS_BY_CLUSTER: Final[dict[str, tuple[str, ...]]] = {
    "awards": ("title", "slug", "summary"),
    "recognition-systems": ("title", "slug", "summary"),
    "concepts": ("title", "slug", "summary"),
    "unawarded": ("title", "slug", "summary"),
    "sectors": ("title", "slug", "summary"),
    "rankings": ("title", "slug", "summary"),
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
# Editorial governance
# validate_content.py checks well-formedness; quality_gate.py enforces the
# publication policy below on entries that declare themselves published.
# ---------------------------------------------------------------------------
VALID_STATUSES: Final[frozenset[str]] = frozenset({"published", "draft"})
DEFAULT_STATUS: Final[str] = "published"

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
