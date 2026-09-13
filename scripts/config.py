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

# (PUBLISHED_SECTORS is derived from DOMAIN_REGISTRY, further down.)

HUB_TITLES: Final[dict[str, str]] = {
    "awards": "Awards",
    "recognition-systems": "Recognition Systems",
    "concepts": "Concepts",
    "unawarded": "The Recognition Archive",
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


# Canonical gap bands. These thresholds are the single source for both the
# reading printed against a case and the explanatory-coverage computation, so
# "under-recognized" can never mean one thing on a page and another in a
# statistic.
SIGNIFICANT_UNDER_RECOGNITION_MIN_GAP: Final[float] = 25
UNDER_RECOGNITION_MIN_GAP: Final[float] = 10
OVER_RECOGNITION_MAX_GAP: Final[float] = -10
FAR_OVER_RECOGNITION_MAX_GAP: Final[float] = -25


def recognition_gap_label(gap: float) -> str:
    if gap >= SIGNIFICANT_UNDER_RECOGNITION_MIN_GAP:
        return "significantly under-recognized"
    if gap >= UNDER_RECOGNITION_MIN_GAP:
        return "under-recognized"
    if gap > OVER_RECOGNITION_MAX_GAP:
        return "recognition roughly matches assessed merit"
    if gap > FAR_OVER_RECOGNITION_MAX_GAP:
        return "recognition exceeds assessed merit"
    return "recognition far exceeds assessed merit"


def is_under_recognized(gap: float) -> bool:
    """Inside the bands the site already publishes, a case has a recognition
    deficit to explain only from `under-recognized` upward. A case whose
    recognition roughly matches assessed merit has nothing outstanding to
    explain, and counting it as "unexplained" mistakes alignment for failure."""
    return gap >= UNDER_RECOGNITION_MIN_GAP


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
# The registry is separate from cycle state on purpose. A deepening cycle is an
# episode of work with a narrative (docs/DOMAIN-CYCLES.md); a domain's lifecycle
# is a property of the domain itself, and the two were being carried by one list.
# While DOMAINS held only the domains under work, a domain the project intends to
# reach had nowhere to exist except in prose, and an entry belonging to it had
# nowhere to point - so it pointed nowhere, and the gate could not tell an
# intentionally unscoped entry from an oversight.
#
#   planned - registered, intended, no assessed corpus. Produces no sector hub
#             and enters no aggregation. An entry may name it, which is how a
#             reference entry says where it belongs without claiming a corpus.
#   open    - under active work: assessed entries exist, the Definition of Done
#             is not yet met.
#   closed  - the Definition of Done is met. Closed is not frozen: a closed
#             domain stays closed and stays correctable.
DOMAIN_LIFECYCLE_STATES: Final[tuple[str, ...]] = ("planned", "open", "closed")

DOMAIN_REGISTRY: Final[dict[str, dict[str, str]]] = {
    "physics-astronomy": {
        "label": "Physics & Astronomy", "state": "closed", "state_since": "2026-09-10",
    },
    "biology-medicine": {
        "label": "Biology & Medicine", "state": "closed", "state_since": "2026-09-11",
    },
    "mathematics-computing": {
        "label": "Mathematics & Computing", "state": "closed", "state_since": "2026-09-12",
    },
    "literature": {
        "label": "Literature", "state": "planned", "state_since": "2026-09-12",
    },
    "peace": {
        "label": "Peace", "state": "planned", "state_since": "2026-09-12",
    },
}

# Label lookup over every registered domain, whatever its state.
DOMAINS: Final[dict[str, str]] = {k: v["label"] for k, v in DOMAIN_REGISTRY.items()}

# The domains that carry an assessed corpus, and therefore the only ones that
# aggregate: sector hubs, domain status, synthesis derivation, rankings.
AGGREGATED_DOMAINS: Final[tuple[str, ...]] = tuple(
    k for k, v in DOMAIN_REGISTRY.items() if v["state"] in ("open", "closed")
)


def domain_state(domain: object) -> str | None:
    entry = DOMAIN_REGISTRY.get(domain) if isinstance(domain, str) else None
    return entry["state"] if entry else None


def is_aggregated_domain(domain: object) -> bool:
    return domain_state(domain) in ("open", "closed")


# Domains with a published sector reference at /sectors/<domain>. Derived from
# the registry rather than typed out: a hub is a consequence of having a corpus,
# and a planned domain has none. A sector reference is a hub for what the corpus
# HAS, not a claim that the corpus is finished; the page states its own maturity
# as measured, and the Definition of Done decides closure, not publication.
PUBLISHED_SECTORS: Final[tuple[str, ...]] = AGGREGATED_DOMAINS


# Clusters whose entries carry domain semantics and must therefore name a
# registered domain. Concepts are the declared exception, and the exception is
# written here rather than left to whichever validator happened not to check:
# a structural mechanism is defined across domains by construction - scoping
# `credit-misattribution` to one domain would assert it does not operate in the
# others, which the corpus has not established.
DOMAIN_SCOPED_CLUSTERS: Final[frozenset[str]] = frozenset(
    {"awards", "recognition-systems", "unawarded", "reports"}
)
DOMAIN_SCOPE_POSTURES: Final[dict[str, str]] = {
    "concepts": "cross-domain-by-construction: a mechanism is not the property of one domain",
}

# ---------------------------------------------------------------------------
# Composite domains
#
# Some domain names join two recognition cultures under one label. A domain like
# that can satisfy every numeric criterion while nearly all of its knowledge sits
# on one side of the join - ten cases and three systems, all mathematics, in a
# domain called Mathematics & Computing.
#
# Entries in a composite domain declare which side they belong to, so coverage
# can be measured. This is reported as an observation and gates nothing: the
# Definition of Done is unchanged, and a domain is not blocked by an uneven
# split. What is refused is the silence - a maturity claim that does not say
# which half of its own name it rests on.
# ---------------------------------------------------------------------------
DOMAIN_SUBFIELDS: Final[dict[str, tuple[str, ...]]] = {
    "mathematics-computing": ("mathematics", "computing", "cross-cutting"),
}


def domain_subfields(domain: str) -> tuple[str, ...]:
    return DOMAIN_SUBFIELDS.get(domain, ())


def is_composite_domain(domain: str) -> bool:
    return bool(DOMAIN_SUBFIELDS.get(domain))


def is_valid_subfield(domain: str, value: object) -> bool:
    return isinstance(value, str) and value in DOMAIN_SUBFIELDS.get(domain, ())


# Published scored entries must be placed in a domain (no orphans).
REQUIRE_DOMAIN: Final[bool] = True

# A case only counts toward a structural pattern when it carries explicit
# `pattern_evidence` for that pattern (source refs proving the mechanism, not
# merely the tag). Published cases must supply evidence for every pattern.
REQUIRE_PATTERN_EVIDENCE: Final[bool] = True

# ---------------------------------------------------------------------------
# Mechanism-ontology revisions.
#
# A mechanism audit is dated evidence: `considered` asserts that each named
# mechanism was tested against that record on that date. When the ontology grows,
# older audits do not become wrong - they become older. The project needs to say
# both things without lying about either, so every revision of the audit-eligible
# mechanism set carries an immutable id.
#
# Ids are immutable and ordered by the commit that changed the set, not by date:
# more than one revision can land on one day. A revision is never edited once
# published; a change to the set creates the next id.
#
# Two different figures follow from this, and they must never be conflated:
#   * completeness at the recorded revision - did the audit test everything that
#     was eligible WHEN IT RAN? A defect if it did not.
#   * currency against the current revision - has the ontology grown since? Not a
#     defect, and never a maturity gate: a closed domain does not become immature
#     because the vocabulary later acquired a word.
# ---------------------------------------------------------------------------
_MOR_001: Final[frozenset[str]] = frozenset({
    "credit-misattribution", "delayed-recognition", "institutional-exclusion",
    "posthumous-recognition",
})
_MOR_002: Final[frozenset[str]] = _MOR_001 | {"theory-experiment-asymmetry"}
_MOR_003: Final[frozenset[str]] = _MOR_002 | {"institutional-gatekeeping"}
_MOR_005: Final[frozenset[str]] = _MOR_003 | {"compulsory-secrecy"}

ONTOLOGY_REVISIONS: Final[dict[str, dict[str, object]]] = {
    "MOR-001": {
        "commit": "d6e52a0", "date": "2026-09-09", "mechanisms": _MOR_001,
        "note": "Cycle 01 opens: the first four structural-cause concepts.",
    },
    "MOR-002": {
        "commit": "8a26749", "date": "2026-09-09", "mechanisms": _MOR_002,
        "note": "Pattern lifecycle hardening adds the theory-experiment asymmetry.",
    },
    "MOR-003": {
        "commit": "c78250e", "date": "2026-09-09", "mechanisms": _MOR_003,
        "note": "Physics individuals completion adds institutional gatekeeping.",
    },
    "MOR-004": {
        "commit": "005a421", "date": "2026-09-11", "mechanisms": _MOR_003,
        "note": (
            "Concept types introduced. The mechanism set is unchanged, but eligibility becomes "
            "formal: only concept_type 'mechanism' may be tested against a case, so the umbrella "
            "concepts stop being admissible in a `considered` list."
        ),
    },
    "MOR-005": {
        "commit": "69ffcc0", "date": "2026-09-12", "mechanisms": _MOR_005,
        "note": "The Cycle 03 ontology review adds compulsory secrecy.",
    },
    "MOR-006": {
        "commit": "442ffa6", "date": "2026-09-12", "mechanisms": _MOR_005,
        "note": (
            "The revision model itself. The mechanism set is unchanged, but an audit must now "
            "record the revision it was performed against, and must test everything eligible at "
            "that revision or name the gap. The hash was backfilled immediately after the commit, "
            "because a commit cannot contain its own hash."
        ),
    },
    "MOR-007": {
        "commit": "af76e55", "date": "2026-09-13", "mechanisms": _MOR_005,
        "note": (
            "Cycle 04 preflight narrows posthumous recognition. The mechanism set is unchanged, but "
            "the concept's operational definition is not: it now requires a death-triggered "
            "eligibility rule, in force at the time, shown by the record to have constrained a "
            "specific recognition opportunity. Read loosely the mechanism attached to every "
            "contributor who had died under such a rule and distinguished nothing. A revision is "
            "recorded because a test against this concept means something different before and "
            "after, even though the list of testable concepts is identical."
        ),
    },
}

CURRENT_ONTOLOGY_REVISION: Final[str] = "MOR-007"

# From this revision onward an audit must be complete at its own revision: the
# declared-gap escape below exists only for audits performed before the model
# existed. It is a one-way door, and deliberately so - without it, "incomplete
# at revision" would become a permanent way to publish an unfinished audit.
COMPLETENESS_ENFORCED_FROM: Final[str] = "MOR-006"

# An audit whose revision cannot be established from the repository's history is
# marked rather than guessed. Guessing a revision would fabricate exactly the kind
# of dated fact this model exists to protect.
LEGACY_REVISION_UNRESOLVED: Final[str] = "legacy-revision-unresolved"


def is_valid_ontology_revision(value: object) -> bool:
    return isinstance(value, str) and (
        value in ONTOLOGY_REVISIONS or value == LEGACY_REVISION_UNRESOLVED
    )


def revision_mechanisms(revision: object) -> frozenset[str]:
    """The audit-eligible mechanisms in force at a revision. An unresolved legacy
    revision constrains nothing, because nothing about it is established."""
    entry = ONTOLOGY_REVISIONS.get(revision) if isinstance(revision, str) else None
    return entry["mechanisms"] if entry else frozenset()


def revision_is_before(revision: object, boundary: str) -> bool:
    """Ids are ordered by the commit that changed the set, so comparing the keys
    in insertion order compares history. An unresolved legacy revision is treated
    as earlier than any recorded one, because that is the only thing known of it."""
    if revision == LEGACY_REVISION_UNRESOLVED:
        return True
    order = list(ONTOLOGY_REVISIONS)
    if not isinstance(revision, str) or revision not in order:
        return False
    return order.index(revision) < order.index(boundary)


def audit_is_complete_at_revision(considered: object, revision: object) -> bool:
    """Did the audit test everything that was audit-eligible when it ran?"""
    tested = set(considered) if isinstance(considered, (list, set, tuple)) else set()
    return revision_mechanisms(revision) <= tested


# Phrases that assert the corpus holds cases evidencing a concept. A page may
# only use one when the engine counts at least one - a title is a claim about the
# record, and boilerplate is the easiest way for a claim to outlive its evidence.
# The phrase list is deliberately about ASSERTED EVIDENCE, not about the word
# "case": a page may discuss what would count as a case without claiming to have
# one.
CORPUS_CLAIM_PHRASES: Final[tuple[str, ...]] = (
    "documented case",
    "evidenced case",
    "documented example",
    "case studies",
    "cases in this corpus",
)


def asserts_corpus_cases(text: object) -> tuple[str, ...]:
    """Which corpus-case claims a piece of page text makes, if any."""
    if not isinstance(text, str):
        return ()
    lowered = text.lower()
    return tuple(phrase for phrase in CORPUS_CLAIM_PHRASES if phrase in lowered)


MECHANISM_VERDICTS: Final[frozenset[str]] = frozenset({"supported", "not-supported"})


def is_valid_mechanism_verdict(value: object) -> bool:
    return isinstance(value, str) and value in MECHANISM_VERDICTS


def audit_is_current(considered: object) -> bool:
    """Does the audit cover the mechanism set in force today? A 'no' is not a
    defect and never a maturity gate - the ontology grew after the audit ran."""
    tested = set(considered) if isinstance(considered, (list, set, tuple)) else set()
    return revision_mechanisms(CURRENT_ONTOLOGY_REVISION) <= tested


# Pattern lifecycle: a structural cause is only "established" in a domain once
# at least this many INDEPENDENT CONTEXTS in that domain exhibit it. A pattern
# supported by a single context is "emergent" and does NOT count toward the DoD.
# This prevents inventing labels just to reach a threshold.
PATTERN_ESTABLISHED_MIN: Final[int] = 2

# ---------------------------------------------------------------------------
# Recurrence contexts - two observations are not two replications.
#
# Until Cycle 03 the threshold above counted CASES. That was adequate while
# every case carrying a pattern arose in a different institution, era and
# country, so one case meant one context. Cycle 03 broke the equivalence: Tommy
# Flowers and James Ellis both carry recognition deficits produced by formal
# secrecy, and both arise inside the same national cryptographic apparatus. Two
# cases; one context. Promoting that to "established" would report a regime's
# signature as a replicated mechanism.
#
# A case may therefore declare, per pattern, the context its instance belongs
# to. A case that declares none is its own context, which is what every entry
# written before this change assumed - so no existing result moves.
#
# Both figures are published: `support` counts cases, `independent_support`
# counts contexts, and only the second decides lifecycle status.
RECURRENCE_CONTEXTS: Final[dict[str, str]] = {
    "uk-government-cryptographic-secrecy": (
        "The United Kingdom's government cryptographic apparatus and the statutory secrecy regime "
        "around it - the Post Office research station working to it, and GCHQ and its predecessors. "
        "Instances arising here share an imposing institution, a legal instrument and a disclosure "
        "practice, so they are observations of one regime rather than independent replications."
    ),
}


def is_valid_recurrence_context(value: object) -> bool:
    return isinstance(value, str) and value in RECURRENCE_CONTEXTS


def pattern_context_key(case_slug: str, declared: object) -> str:
    """The context an instance counts in. A case that declares none stands alone."""
    return declared if is_valid_recurrence_context(declared) else f"case:{case_slug}"

# ---------------------------------------------------------------------------
# Definition of Done - DoD v1.1
#
# Maturity is completeness of accountable inquiry, not conformity of findings to
# a target outcome.
#
# SUPERSEDED - DoD v1.0 (in force until 2026-09-10): DOMAIN_DOD_V1_0 below.
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
# Cycle 03 changed what it counts - independent contexts rather than cases - and
# not how many it requires.
# No datum moves because of this governance decision; only the question "when is
# a domain's inquiry complete?" is answered differently.
# ---------------------------------------------------------------------------
DOD_VERSION: Final[str] = "DoD v1.1"

# The superseded criteria, kept as data rather than as prose, so a report
# correcting a claim made under v1.0 can cite the number that was actually in
# force instead of retyping it from memory.
DOMAIN_DOD_V1_0: Final[dict[str, int]] = {"ddi_cases": 10, "rls_systems": 3, "patterns": 4}

DOMAIN_DOD: Final[dict[str, int]] = {
    "ddi_cases": 10,      # individual contributions scored with the DDI
    "rls_systems": 3,     # recognition systems scored with the RLS
}

# Accounting criteria: every case must be examined, and the examination recorded.
DOMAIN_DOD_ACCOUNTING: Final[dict[str, int]] = {
    "mechanism_accounting_percentage": 100,  # every case: evidenced mechanism OR dated audit
    "cases_unaudited": 0,                    # and nothing left unexamined
}

# What the 100% above does and does not assert. Written down because the two are
# easy to conflate, and conflating them would let the corpus claim a depth of
# examination it has not measured: accounting counts whether each case was
# examined at all, not whether each examination tested every mechanism that was
# eligible at the time. That second question is measured separately, reported,
# and gates nothing.
MECHANISM_ACCOUNTING_MEANING: Final[str] = (
    "Every case carries either evidence for a mechanism or a dated audit that searched the "
    "record and found none. It does not assert that each audit tested every mechanism that "
    "was audit-eligible when it ran; that is measured separately as completeness at revision."
)

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


# ---------------------------------------------------------------------------
# Concept semantics
#
# The concept cluster mixes levels. Some entries are operative, case-level
# mechanisms with an operational definition (an act, a barrier, an interval that
# can be looked for in a record). Others are umbrella tendencies covering
# several possible mechanisms, or framework distinctions that structure the
# project's thinking without ever being true or false of a single case.
#
# Only the first kind can be tested against a case. A framework concept cannot
# be a "failed mechanism test", and counting it as one makes an ontology look
# narrower than it is. The concepts are not rewritten to fit the classes; the
# classes record what each concept already was.
# ---------------------------------------------------------------------------
CONCEPT_TYPES: Final[frozenset[str]] = frozenset(
    {
        "mechanism",            # operative and case-level: can be evidenced or not in a given case
        "recognition-pattern",  # an umbrella tendency covering several mechanisms; not case-testable
        "framework-concept",    # a distinction the project reasons with; never true or false of a case
    }
)

# What a mechanism audit may consider, and what a case may declare as a pattern.
AUDIT_ELIGIBLE_CONCEPT_TYPES: Final[frozenset[str]] = frozenset({"mechanism"})


def is_valid_concept_type(value: object) -> bool:
    return isinstance(value, str) and value in CONCEPT_TYPES


# ---------------------------------------------------------------------------
# Archive visibility
#
# An award's archive is part of its architecture. "No nomination found" and
# "the years that would contain it are not released yet" are different facts,
# and a corpus that collapses them into silence is asserting something it has
# not checked. These four states keep them apart.
#
# Note the narrowness of the last one. This audit established that no
# deliberation record was reached - not that none is obtainable. The Statutes
# permit a prize-awarding body to give third parties access to the materials
# behind a decision once fifty years have passed, so "unavailable" would assert
# more than was checked.
# ---------------------------------------------------------------------------
ARCHIVE_VISIBILITY_STATES: Final[frozenset[str]] = frozenset(
    {
        "nomination-documented",          # a nomination record exists in the open archive
        "no-nomination-in-open-archive",  # the relevant years ARE open and contain none
        "archive-year-not-released",      # the relevant years fall after the release horizon
        "deliberation-not-reached",       # no deliberation record was reached by this audit
    }
)


def is_valid_archive_state(value: object) -> bool:
    return isinstance(value, str) and value in ARCHIVE_VISIBILITY_STATES


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
# ---------------------------------------------------------------------------
# The SEO contract.
#
# A reference page is only useful if the people looking for it can find it, and
# a search engine can only place a page it can parse. That is a presentation
# problem, not a methodological one, so nothing here may change what an entry
# claims - it governs how the entry announces itself.
#
# The contract is data on the entry and is checked by the gate, so it cannot
# depend on anyone remembering it. Every governed page declares the query it is
# the best answer to, the entities it sits among, the title and description a
# result page will show, its canonical path, its visible H1, the structured-data
# types it emits, the governed pages that link to it and that it links out to,
# and whether it should be indexed at all.
# ---------------------------------------------------------------------------
SEO_CONTRACT_CLUSTERS: Final[frozenset[str]] = frozenset(
    {"awards", "unawarded", "recognition-systems", "concepts", "reports"}
)

SEO_CONTRACT_FIELDS: Final[tuple[str, ...]] = (
    "primary_query",
    "secondary_entities",
    "title",
    "description",
    "canonical",
    "h1",
    "schema_types",
    "incoming_links",
    "outgoing_links",
    "indexing",
)

# Schema.org types this project will emit. The list is short on purpose: a type
# we cannot populate honestly is structured data that misrepresents the page.
# FAQPage is absent because no page here carries an FAQ.
# The types a page may DECLARE are exactly the types it may EMIT. The gate
# compares the declaration against the built HTML, so a contract cannot promise
# structured data the page does not carry, and a page cannot carry structured
# data its contract never declared. FAQPage is absent because no page here has an
# FAQ; a type we cannot populate honestly is a misrepresentation, not an
# optimisation.
SEO_SCHEMA_TYPES: Final[frozenset[str]] = frozenset(
    {"BreadcrumbList", "Person", "Organization", "CreativeWork", "DefinedTerm", "Report", "ItemList"}
)

# Every governed page is a node in a breadcrumb trail, so every contract emits it.
SEO_REQUIRED_SCHEMA_TYPES: Final[frozenset[str]] = frozenset({"BreadcrumbList"})

SEO_INDEXING_STATES: Final[frozenset[str]] = frozenset({"index", "noindex"})

# House presentation discipline, NOT a claimed search-engine requirement.
#
# Search engines publish no fixed title length, rewrite title links when they
# judge a better one exists, and compose snippets from page content - a meta
# description may not be used at all. These numbers are therefore ours: a bound
# that keeps a title readable at a glance and a description that says what the
# page contains in one sentence. They are editorial limits the gate enforces on
# us, and the project does not represent them as rules anyone else imposes. The
# same refusal to turn a heuristic into a fact governs the evidence layers.
SEO_BRAND_SUFFIX: Final[str] = " | ChampionsAwards"
SEO_TITLE_MAX: Final[int] = 95
SEO_DESCRIPTION_MIN: Final[int] = 70
SEO_DESCRIPTION_MAX: Final[int] = 185

# Breadcrumb trails are built from the canonical path, and each segment needs a
# human label. A segment with no label here would render as a slug.
SEO_BREADCRUMB_LABELS: Final[dict[str, str]] = {
    "": "Home",
    "awards": "Awards",
    "recognition-systems": "Recognition Systems",
    "concepts": "Concepts",
    "unawarded": "The Recognition Archive",
    "reports": "Reports",
    "sectors": "Sectors",
    "rankings": "Rankings",
}


# Routes that are generated rather than authored as entries - hubs, sector
# references, the methodology pages and the calculator - carry their contract
# here, because there is no YAML entry to hold it. Same fields, same gate.
SEO_ROUTE_CONTRACTS: Final[dict[str, dict[str, object]]] = {
    "/": {
        "primary_query": "recognition systems",
        "secondary_entities": ["recognition gap", "award architecture", "scientific recognition",
                               "Deservingness Index", "Recognition Legitimacy Score"],
        "title": "ChampionsAwards - Recognition Systems, Awards & Recognition Gaps | ChampionsAwards",
        "description": "A governed reference on how recognition systems work: award architecture, "
                       "legitimacy assessment, and the measured distance between contribution and "
                       "the recognition it received.",
        "canonical": "/",
        "h1": "Recognition Systems, Measured",
        "schema_types": [],
        "incoming_links": ["/about", "/framework", "/methodology"],
        "outgoing_links": ["/awards", "/concepts", "/methodology", "/rankings",
                           "/recognition-systems", "/reports", "/sectors", "/unawarded"],
        "indexing": "index",
    },
    "/awards": {
        "primary_query": "award architecture",
        "secondary_entities": ["Nobel Prize", "Fields Medal", "Turing Award", "Wolf Prize",
                               "award selection process"],
        "title": "Award Architecture - Rules, Funding & Selection Mapped | ChampionsAwards",
        "description": "Awards mapped as mechanisms rather than brands: who grants each prize, who "
                       "funds it, who may nominate, what its rules say, and where governed cases "
                       "meet that structure.",
        "canonical": "/awards",
        "h1": "Awards: Award Architecture",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/sectors"],
        "outgoing_links": ["/awards/acm-am-turing-award", "/awards/fields-medal-award",
                           "/awards/nobel-prize-in-physics",
                           "/awards/nobel-prize-in-physiology-or-medicine",
                           "/awards/wolf-prize-award", "/recognition-systems"],
        "indexing": "index",
    },
    "/recognition-systems": {
        "primary_query": "recognition system legitimacy",
        "secondary_entities": ["Recognition Legitimacy Score", "Nobel Prize system",
                               "Fields Medal", "Turing Award", "prize governance"],
        "title": "Recognition System Legitimacy - RLS Assessments | ChampionsAwards",
        "description": "The institutions that decide which work becomes visible, each scored on "
                       "process, breadth, track record, transparency and independence by one "
                       "published instrument.",
        "canonical": "/recognition-systems",
        "h1": "Recognition System Legitimacy",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/awards"],
        "outgoing_links": ["/methodology", "/recognition-systems/fields-medal",
                           "/recognition-systems/nobel-prize-system",
                           "/recognition-systems/turing-award", "/recognition-systems/wolf-prize"],
        "indexing": "index",
    },
    "/unawarded": {
        "primary_query": "recognition gap",
        "secondary_entities": ["under-recognition", "scientific recognition", "historical attribution",
                               "Deservingness Index", "recognition archive"],
        "title": "Recognition Gap Archive - Contribution vs Recognition Recorded | ChampionsAwards",
        "description": "A governed archive of how contribution and recognition align, diverge, or "
                       "remain unresolved - every case assessed by the same published index and "
                       "sourced claim by claim.",
        "canonical": "/unawarded",
        "h1": "The Recognition Archive: the Recognition Gap, Case by Case",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/rankings"],
        "outgoing_links": ["/concepts", "/methodology", "/rankings"],
        "indexing": "index",
    },
    "/concepts": {
        "primary_query": "recognition mechanisms",
        "secondary_entities": ["credit misattribution", "institutional exclusion",
                               "delayed recognition", "Matthew effect", "Matilda effect"],
        "title": "Recognition Mechanisms - Why Recognition Fails | ChampionsAwards",
        "description": "The defined vocabulary behind every claim here: the mechanisms by which "
                       "recognition is displaced, delayed, blocked or withheld, each with the cases "
                       "that evidence it.",
        "canonical": "/concepts",
        "h1": "Concepts: Recognition Mechanisms",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/methodology"],
        "outgoing_links": ["/concepts/credit-misattribution", "/concepts/delayed-recognition",
                           "/concepts/institutional-exclusion", "/methodology"],
        "indexing": "index",
    },
    "/reports": {
        "primary_query": "recognition research",
        "secondary_entities": ["recognition failure patterns", "scientific recognition",
                               "comparative analysis"],
        "title": "Recognition Research - Syntheses Over the Governed Corpus | ChampionsAwards",
        "description": "Syntheses derived from the governed corpus, where every figure resolves from "
                       "the published engine at build time and no number in the prose was typed by "
                       "an author.",
        "canonical": "/reports",
        "h1": "Reports: Recognition Research",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/sectors"],
        "outgoing_links": ["/reports/explained-aligned-unresolved-biology",
                           "/reports/recognition-failure-patterns-physics"],
        "indexing": "index",
    },
    "/sectors": {
        "primary_query": "scientific recognition by field",
        "secondary_entities": ["Physics & Astronomy", "Biology & Medicine",
                               "Mathematics & Computing", "recognition gap"],
        "title": "Sectors - Scientific Recognition by Field | ChampionsAwards",
        "description": "One reference per governed domain, binding its cases, recognition systems, "
                       "award anatomies, mechanisms and reports into a single analytical surface.",
        "canonical": "/sectors",
        "h1": "Sectors: Scientific Recognition by Field",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/rankings"],
        "outgoing_links": ["/awards", "/reports", "/sectors/biology-medicine",
                           "/sectors/mathematics-computing", "/sectors/physics-astronomy"],
        "indexing": "index",
    },
    "/rankings": {
        "primary_query": "recognition gap index",
        "secondary_entities": ["Deservingness Index", "under-recognized scientists",
                               "recognition gap", "comparative ranking"],
        "title": "Recognition Gap Index - Every Governed Case Ranked | ChampionsAwards",
        "description": "Every governed case ranked by the distance between assessed contribution and "
                       "observed recognition, computed at build time from the published formula.",
        "canonical": "/rankings",
        "h1": "Rankings: the Recognition Gap Index",
        "schema_types": ["BreadcrumbList", "ItemList"],
        "incoming_links": ["/", "/methodology"],
        "outgoing_links": ["/methodology", "/unawarded"],
        "indexing": "index",
    },
    "/methodology": {
        "primary_query": "Deservingness Index",
        "secondary_entities": ["Recognition Legitimacy Score", "recognition gap",
                               "scoring methodology", "evidence provenance"],
        "title": "Deservingness Index & RLS - The Published Methodology | ChampionsAwards",
        "description": "The two instruments and their weights, the gap they produce, and the "
                       "source-to-score chain every published figure has to pass through.",
        "canonical": "/methodology",
        "h1": "Methodology: the Deservingness Index and the RLS",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/rankings"],
        "outgoing_links": ["/concepts", "/protocol", "/rankings"],
        "indexing": "index",
    },
    "/framework": {
        "primary_query": "recognition framework",
        "secondary_entities": ["merit vs recognition", "award legitimacy", "documented omission"],
        "title": "The Recognition Framework - How Recognition Is Analysed | ChampionsAwards",
        "description": "The premises the whole project rests on: what recognition is, why omission "
                       "is evidence, and why a measured gap is treated as a finding rather than a "
                       "verdict.",
        "canonical": "/framework",
        "h1": "The Recognition Framework",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/about"],
        "outgoing_links": ["/concepts", "/methodology", "/unawarded"],
        "indexing": "index",
    },
    "/protocol": {
        "primary_query": "editorial protocol",
        "secondary_entities": ["sourcing standards", "corrections policy", "evidence grading"],
        "title": "Editorial Protocol - Sourcing, Neutrality & Corrections | ChampionsAwards",
        "description": "The rules every entry passes before publication: what counts as a "
                       "record-grade source, how a claim without one is handled, and how "
                       "corrections are recorded.",
        "canonical": "/protocol",
        "h1": "Editorial Protocol",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/about", "/methodology"],
        "outgoing_links": ["/methodology"],
        "indexing": "index",
    },
    "/about": {
        "primary_query": "about ChampionsAwards",
        "secondary_entities": ["recognition reference", "award analysis", "editorial standards"],
        "title": "About ChampionsAwards - What This Reference Is | ChampionsAwards",
        "description": "What this project is, what it deliberately does not claim, and the limits it "
                       "states about a young corpus whose scores are structured estimates rather "
                       "than measurements.",
        "canonical": "/about",
        "h1": "About ChampionsAwards",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/", "/framework"],
        "outgoing_links": ["/methodology", "/protocol", "/unawarded"],
        "indexing": "index",
    },
    "/calculator": {
        "primary_query": "Deservingness Index calculator",
        "secondary_entities": ["DDI weights", "recognition gap"],
        "title": "Deservingness Index Calculator - Interactive Tool | ChampionsAwards",
        "description": "An interactive tool for applying the published weights to your own inputs. "
                       "It is a utility rather than a reference page, and is deliberately kept out "
                       "of the search index.",
        "canonical": "/calculator",
        "h1": "Deservingness Index Calculator",
        "schema_types": ["BreadcrumbList"],
        "incoming_links": ["/methodology"],
        "outgoing_links": ["/methodology"],
        "indexing": "noindex",
    },
}


# An award anatomy and the recognition-system entry for the same award are two
# pages answering two questions - how the award is built, and how legitimate the
# instrument judges it. They must link to each other, and their titles are not
# always identical, so the pairing is declared rather than guessed.
# Descriptive anchor text for links between generated surfaces. A crawler and a
# reader both learn from anchor text; "read more" teaches neither anything. Held
# centrally so a declared link and the link the page renders cannot drift apart.
SEO_ROUTE_ANCHORS: Final[dict[str, str]] = {
    "/": "ChampionsAwards - recognition systems, measured",
    "/awards": "Award architecture - how each prize is actually built",
    "/recognition-systems": "Recognition systems - legitimacy assessed on five dimensions",
    "/unawarded": "The Recognition Archive - every governed case and its gap",
    "/concepts": "Recognition mechanisms - the vocabulary behind every claim here",
    "/reports": "Reports - syntheses derived from the governed corpus",
    "/sectors": "Sectors - scientific recognition by field",
    "/rankings": "The Recognition Gap Index - every case ranked by its gap",
    "/methodology": "Methodology - the Deservingness Index and the RLS, with weights",
    "/framework": "The framework - why omission is treated as evidence",
    "/protocol": "Editorial protocol - sourcing, neutrality and corrections",
    "/about": "About - what this reference is, and what it does not claim",
    "/calculator": "The calculators - apply the published weights yourself",
}


AWARD_SYSTEM_PAIRS: Final[dict[str, str]] = {
    "acm-am-turing-award": "turing-award",
    "fields-medal-award": "fields-medal",
    "wolf-prize-award": "wolf-prize",
    "nobel-prize-in-physics": "nobel-prize-system",
    "nobel-prize-in-physiology-or-medicine": "nobel-prize-system",
    "nobel-peace-prize": "nobel-prize-system",
}


def sector_route_contract(domain: str) -> dict[str, object]:
    """A sector reference's contract, derived from the domain rather than typed
    out, so a new domain cannot be published without one."""
    label = DOMAINS.get(domain, domain.replace("-", " ").title())
    return {
        "primary_query": f"{label} recognition",
        "secondary_entities": [label, "recognition gap", "recognition systems",
                               "award architecture", "scientific recognition"],
        "title": f"{label} Recognition - Awards, Cases & Systems | ChampionsAwards",
        "description": (
            f"The governed {label} reference: every assessed case and its recognition gap, the "
            f"systems scored, the award architectures mapped, and what this corpus cannot yet say."
        ),
        "canonical": f"/sectors/{domain}",
        "h1": f"{label} Recognition",
        "schema_types": ["BreadcrumbList", "CreativeWork"],
        "incoming_links": ["/sectors"],
        "outgoing_links": ["/methodology", "/rankings", "/unawarded"],
        "indexing": "index",
    }


def route_contract(path: str) -> dict[str, object] | None:
    """Every generated route's contract, by path."""
    if path in SEO_ROUTE_CONTRACTS:
        return SEO_ROUTE_CONTRACTS[path]
    if path.startswith("/sectors/"):
        domain = path[len("/sectors/"):]
        if domain in PUBLISHED_SECTORS:
            return sector_route_contract(domain)
    return None


def seo_render_vars(contract: dict[str, object] | None, path: str, page_title: str) -> dict[str, object]:
    """Turn a contract into what a template renders, plus the breadcrumb trail.
    Shared by entry pages and generated routes so both emit the same shapes."""
    contract = contract or {}
    trail = [{"name": SEO_BREADCRUMB_LABELS.get("", "Home"), "url": "/"}]
    segments = [part for part in path.split("/") if part]
    for index, part in enumerate(segments):
        walked = "/" + "/".join(segments[: index + 1])
        last = index == len(segments) - 1
        # A crumb is a place name, not a headline: prefer the short cluster label
        # wherever one exists, and fall back to the page's own heading.
        name = SEO_BREADCRUMB_LABELS.get(part) or (
            (contract.get("h1") or page_title) if last else part.replace("-", " ").title())
        trail.append({"name": name, "url": walked})
    return {
        "seo_title": contract.get("title"),
        "seo_description": contract.get("description"),
        "seo_h1": contract.get("h1"),
        "seo_robots": ("noindex,follow" if contract.get("indexing") == "noindex"
                       else "index,follow,max-image-preview:large"),
        "breadcrumbs": trail,
    }


def is_valid_schema_type(value: object) -> bool:
    return isinstance(value, str) and value in SEO_SCHEMA_TYPES


def is_canonical_path(value: object) -> bool:
    """A canonical is a clean, absolute, extension-free site path with no
    trailing slash - the one spelling of the page that every link should use."""
    if value == "/":
        return True  # the site root is a path, and it is the one that ends in a slash
    return (
        isinstance(value, str)
        and value.startswith("/")
        and not value.endswith("/")
        and ".html" not in value
        and "?" not in value
        and "#" not in value
        and " " not in value
    )


AWARD_ARCHITECTURE_FIELDS: Final[tuple[tuple[str, str], ...]] = (
    ("granting_body", "Granting body"),
    # Who decides and who pays are different facts, and an award entry that states
    # only the first invites the reader to infer the second. The Cycle 03
    # requalification of the Turing Award lowered its independence score from 85 to
    # 62 on exactly that confusion: professional-society governance had been read as
    # freedom from commercial funding, while the award's own page names a single
    # corporate funder. The separation is therefore structural here, not a remark in
    # a rationale - see FUNDING_SEPARATION_REQUIRED below.
    ("funding_source", "Funding source"),
    ("governing_documents", "Governing documents"),
    ("eligibility", "Eligibility"),
    ("nomination_eligibility", "Who may nominate"),
    ("nomination", "Nomination process"),
    ("selection_body", "Selection & evaluation"),
    ("decision_stages", "Decision stages"),
    ("sharing_rule", "Sharing rule"),
    ("posthumous_rule", "Posthumous rule"),
    ("secrecy", "Secrecy"),
    ("withholding", "Withholding / deferral"),
    ("finality", "Finality"),
)

AWARD_ARCHITECTURE_KEYS: Final[frozenset[str]] = frozenset(k for k, _ in AWARD_ARCHITECTURE_FIELDS)

# An anatomy may not say who decides without saying who pays. Where the funder is
# not documented, the entry says that in `funding_source` and carries an audit
# exception; what it may not do is leave the question unasked.
FUNDING_SEPARATION_REQUIRED: Final[tuple[str, str]] = ("granting_body", "funding_source")

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
