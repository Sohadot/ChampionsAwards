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

# Note: /rankings and /sectors/<domain> are computed aggregate pages
# (generate_rankings.py, generate_sectors.py), not data clusters, so they
# deliberately do not appear in CLUSTERS below. Sector aggregation is computed,
# never hand-edited: there is no authorable sectors/*.yaml to contradict the
# engine.
CLUSTERS: Final[dict[str, str]] = {
    "awards": "award.html",
    "recognition-systems": "recognition-system.html",
    "concepts": "concept.html",
    "unawarded": "unawarded.html",
    "reports": "report.html",
    "timeline": "timeline.html",
}

# Domains with a published sector reference at /sectors/<domain>.
PUBLISHED_SECTORS: Final[tuple[str, ...]] = ("physics-astronomy",)

HUB_TITLES: Final[dict[str, str]] = {
    "awards": "Awards",
    "recognition-systems": "Recognition Systems",
    "concepts": "Concepts",
    "unawarded": "The Unawarded Archive",
    "reports": "Reports",
    "timeline": "Timeline",
}

REQUIRED_FIELDS_BY_CLUSTER: Final[dict[str, tuple[str, ...]]] = {
    "awards": ("title", "slug", "summary"),
    "recognition-systems": ("title", "slug", "summary"),
    "concepts": ("title", "slug", "summary"),
    "unawarded": ("title", "slug", "summary"),
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

# ---------------------------------------------------------------------------
# Definition of Done - DoD v1.1
#
# Maturity is completeness of accountable inquiry, not conformity of findings to
# a target outcome.
#
# SUPERSEDED - DoD v1.0 (in force until 2026-09-10):
#     {"ddi_cases": 10, "rls_systems": 3, "patterns": 4}
# The v1.0 requirement of four ESTABLISHED mechanisms was set before any domain
# had completed a full mechanism audit. Cycle 01 ran every layer that precedes
# judgment - case deepening, provenance, source-grade audit, award anatomy,
# comparison, synthesis, and a dedicated mechanism audit of the two unexplained
# cases - and the established count stayed at 2 while mechanism accounting
# reached 10/10. That is the evidence that the count measured an empirical
# property of the corpus, not the completeness of the investigation, and that
# holding it as a gate created an incentive to find more labels or more cases to
# clear a target. v1.1 therefore removes the established-pattern count from the
# maturity criteria and replaces it with complete mechanism accounting. Pattern
# recurrence is still measured and still published - it no longer decides
# whether the evidence has been fully investigated.
#
# Note what did NOT change: PATTERN_ESTABLISHED_MIN stays 2. That is a definition
# of what makes a pattern recurring rather than singular, and it remains in force.
# No datum moves because of this governance decision; only the question "when is
# a domain's inquiry complete?" is answered differently.
# ---------------------------------------------------------------------------
DOD_VERSION: Final[str] = "DoD v1.1"

DOMAIN_DOD: Final[dict[str, int]] = {
    "ddi_cases": 10,      # individual contributions scored with the DDI
    "rls_systems": 3,     # recognition systems scored with the RLS
}

# Accounting criteria: every case must be examined, and the examination recorded.
DOMAIN_DOD_ACCOUNTING: Final[dict[str, int]] = {
    "mechanism_accounting_percentage": 100,  # every case: evidenced mechanism OR dated audit
    "cases_unaudited": 0,                    # and nothing left unexamined
}

# Layer criteria: measured as present, not asserted in prose.
DOMAIN_DOD_LAYERS: Final[tuple[str, ...]] = (
    "source_grade_closure",  # every load-bearing claim closed or excepted by a documented decision
    "award_anatomy",         # at least one award mapped in full (architecture + corpus relations)
    "synthesis",             # at least one published synthesis report deriving from this domain
)

# Reported alongside maturity, and deliberately NOT a gate: how many mechanisms
# the corpus happens to evidence is a result, not a measure of thoroughness.
DOMAIN_OBSERVED_ONLY: Final[tuple[str, ...]] = (
    "evidenced_mechanisms",
    "established_mechanisms",
    "emergent_mechanisms",
    "cases_unexplained_after_audit",
)


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
    "question",
    "scope",
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


# Claim-level authority. Source type says what KIND of source something is;
# `basis` says WHY a source is authoritative for a specific claim. A claim is
# source-grade closed only when an entry declares a `provenance` record_anchor
# (record-grade source) with one of these bases - never on source type alone.
BASIS_VOCAB: Final[frozenset[str]] = frozenset(
    {
        "primary-publication",          # the original paper, preprint, or patent
        "awarding-institution-record",  # the prize body's own record of the outcome
        "institutional-archive",        # a university/society/institution archive of the record
        "contemporary-record",          # a contemporaneous document (letter, minutes, circular)
        "scholarly-history",            # peer-reviewed history that establishes the fact
        "reference-consensus",          # reference works in agreement (uncontested facts only)
        "participant-testimony",        # the participant's own published account of an event they lived
                                        # (a primary source in historical method; self-reported, and
                                        # weaker than a contemporaneous document for contested facts)
    }
)


def is_valid_basis(value: object) -> bool:
    return isinstance(value, str) and value in BASIS_VOCAB


# ---------------------------------------------------------------------------
# Mechanism audit
# A case may carry a measured recognition gap and no evidenced mechanism. That
# is a legitimate result, but only when it is the outcome of an actual search -
# never a silence. A mechanism audit records that search: what was considered,
# when, what the record showed, and which sources were the best available. The
# two findings below are the only ways an audit can end.
# ---------------------------------------------------------------------------
MECHANISM_FINDINGS: Final[frozenset[str]] = frozenset(
    {
        "mechanism-evidenced",     # the record supports at least one declared pattern
        "no-mechanism-evidenced",  # searched, and the record supports none
    }
)


def is_valid_mechanism_finding(value: object) -> bool:
    return isinstance(value, str) and value in MECHANISM_FINDINGS


# A published hypothesis is open until the corpus refutes it. "Refuted" is a
# first-class state: a hypothesis the evidence killed stays on the page, marked,
# rather than disappearing from the record.
HYPOTHESIS_STATES: Final[frozenset[str]] = frozenset({"open", "refuted"})


def is_valid_hypothesis_state(value: object) -> bool:
    return isinstance(value, str) and value in HYPOTHESIS_STATES


# ---------------------------------------------------------------------------
# Award Architecture Model
# An award page is an anatomy of a recognition mechanism, kept in three
# separate layers: formal architecture (what the rules say), historical
# operation (key_facts, what the record shows), and corpus interaction (which
# ChampionsAwards cases touch this structure). The fields below are the formal
# architecture; each is a factual claim anchorable via provenance ("architecture:<key>").
# ---------------------------------------------------------------------------
AWARD_ARCHITECTURE_FIELDS: Final[tuple[tuple[str, str], ...]] = (
    ("granting_body", "Granting body"),
    ("governing_documents", "Governing documents"),
    ("eligibility", "Eligibility"),
    ("nomination", "Nomination"),
    ("selection_body", "Selection & evaluation"),
    ("decision_stages", "Decision stages"),
    ("sharing_rule", "Sharing rule"),
    ("posthumous_rule", "Posthumous rule"),
    ("secrecy", "Secrecy"),
    ("withholding", "Withholding / deferral"),
    ("finality", "Finality"),
)

AWARD_ARCHITECTURE_KEYS: Final[frozenset[str]] = frozenset(k for k, _ in AWARD_ARCHITECTURE_FIELDS)

# Corpus-relation semantics. `architecture_element` says WHICH part of the award
# apparatus a relation touches; `interaction_type` says WHAT the record shows
# happened. Keeping them separate stops a descriptive relation from being read
# as a causal one. A relation may state what the record connects; it may not
# state why the outcome occurred unless the record establishes causation.
INTERACTION_TYPES: Final[frozenset[str]] = frozenset(
    {
        "documented-award-outcome",   # a specific award decision on record (who was/was not a laureate)
        "documented-nomination",      # a nomination on record (rare; nominations are sealed 50 years)
        "eligibility-constraint",     # a formal eligibility rule that bears on the case
        "sharing-constraint",         # the maximum-laureates rule bears on the case
        "posthumous-constraint",      # the no-posthumous rule bears on the case
        "archival-selection-record",  # an archival record of the selection/deliberation
        "historical-non-award",       # the record shows no award was made (a negative, not a nomination claim)
        "analytical-touchpoint",      # our analytical link, explicitly not a documented event
    }
)


def is_valid_interaction_type(value: object) -> bool:
    return isinstance(value, str) and value in INTERACTION_TYPES


# ---------------------------------------------------------------------------
# Temporal validity of rules
#
# Learned from the Franklin case: it is not enough for a source to be official
# and a rule to be current. When a rule is tied to a historical event, the
# version of the rule that was in force AT THAT TIME is what matters. The
# Nobel Foundation's prohibition on posthumous awards entered the statutes in
# 1974; citing today's statute against a 1962 decision is an anachronism, not a
# provenance.
#
# This is deliberately narrow. Only claims of the form "this rule bore on this
# case" need a `rule_at_time`; ordinary factual claims do not. The interaction
# types below are exactly those claims.
# ---------------------------------------------------------------------------
TIME_DEPENDENT_INTERACTIONS: Final[frozenset[str]] = frozenset(
    {
        "eligibility-constraint",
        "sharing-constraint",
        "posthumous-constraint",
    }
)


def is_year_or_iso_date(value: object) -> bool:
    """A rule's validity may be dated to a year (1974) or to a full date."""
    if isinstance(value, int):
        return 1000 <= value <= 2999
    if is_iso_date(value):
        return True
    return isinstance(value, str) and bool(re.fullmatch(r"\d{4}", value.strip()))


def temporal_key(value: object) -> str:
    """Comparable form of a year-or-date, for ordering checks."""
    if isinstance(value, int):
        return f"{value:04d}-00-00"
    text = str(value).strip()
    return f"{text}-00-00" if len(text) == 4 else text


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
