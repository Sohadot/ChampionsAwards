# Domain Deepening Cycles

ChampionsAwards is not built by breadth. It is built one **recognition domain**
at a time, each taken to full maturity before the next is opened. The goal is not
a catalogue of overlooked people; it is a **mapped architecture of how human
recognition works, fails, concentrates, delays, and legitimizes merit**. People
are the data points, not the product.

A guiding rule governs every layer we add:

> Every new layer must make ChampionsAwards harder to ignore, harder to
> contradict, and harder to replicate.

## The seven layers of a domain

A domain is mature only when all seven layers exist and cohere:

1. **Individuals** — a small but strong set of DDI-scored cases, with real
   variety in the *type* of recognition gap, not the same story repeated.
2. **Recognition systems** — the prizes, academies, professional bodies, and
   other institutional mechanisms that governed recognition in the domain (RLS).
3. **Specific awards** — pages for pivotal awards whose history, rules, or
   constraints deserve independent analysis.
4. **Concepts (structural causes)** — the reusable ontology of *why* gaps occur:
   delayed recognition, credit misattribution, institutional exclusion,
   posthumous recognition, and others surfaced by the cases themselves.
5. **Comparison** — computed distribution across the domain: median DDI, median
   gap, the spread of gaps, RLS distribution, most frequent structural causes.
6. **Sector page** — `/sectors/<domain>` as a full analytical reference that
   binds individuals, systems, metrics, and concepts — never a thin index.
7. **Synthesis** — at least one study (e.g. *Recognition Failure Patterns in
   Twentieth-Century Physics*). This layer is where reference authority begins.

## Two movements, one discipline

- **Vertical depth:** Person → Award → System → Structural cause → Metric →
  Comparative finding.
- **Horizontal expansion:** Physics → Biology → Mathematics → Literature → …

We move horizontally **only** after the current domain reaches maturity.

## Definition of Done (a domain is "mature v1.0" when)

The thresholds below are enforced-as-measured by `scripts/domain_status.py`,
which reads the same scoring engine the site uses. A domain is closed only when
every threshold is met and the qualitative criteria hold.

Measured thresholds (`DOMAIN_DOD` in `scripts/config.py`):

- **DDI cases ≥ 10** — high-quality, sourced individual contributions.
- **RLS systems ≥ 3** — relevant recognition systems scored.
- **Established structural-cause patterns ≥ 4** — see the pattern lifecycle below.

### Pattern lifecycle

A structural cause is not counted just because it is named once. Each pattern in
a domain is:

- **emergent** — exhibited by a single documented case; recorded, but **not**
  counted toward the DoD; or
- **established** — exhibited by at least `PATTERN_ESTABLISHED_MIN` (2)
  independent cases in that domain.

Only established patterns count. This prevents inventing four labels to reach
4/4; a real structural pattern must actually recur. Patterns are surfaced by
auditing the cases, never imposed on them.

### Score-level provenance

Reproducibility of the formula is not enough. Every dimension score — and
`observed_recognition` — carries an `evidence` list pointing to specific
`sources`, so a reader can follow the full chain:

> source → factual evidence → dimension judgment → weighted score → gap → rank.

The quality gate requires this evidence on every published assessment; fact,
assessment, and interpretation stay visibly separate.

### Pattern-level provenance

A pattern is a sourced claim, not a tag. Every case that declares a `pattern`
must supply `pattern_evidence` — source refs that document the *mechanism* in
that case — and the quality gate rejects a pattern without it. Crucially,
`domain_status.py` counts a case toward a pattern's support **only** when that
case carries explicit pattern evidence for it. The full ontological chain is:

> source → fact → structural mechanism → recurring pattern → domain finding.

Patterns are surfaced by a cross-case audit of the evidence — asking which
mechanisms actually recur — never by hunting for a second instance to promote a
label. If the evidence yields three established patterns rather than four, the
domain reports 3/4; a truthful "not yet" is preferred to a manufactured pass.

### Source-grade audit (closure criterion)

Before a domain is declared mature v1.0, each case is reviewed for whether a
central claim — a discovery priority, an exclusion, a prize outcome — can be
anchored to a record-grade source rather than a reputable secondary source
alone. This does not reject secondary sources; it requires that load-bearing
claims reach record-grade provenance wherever one exists.

Sources carry a `type` from a functional taxonomy (`SOURCE_TYPES` in
`scripts/config.py`): record-grade (`primary`, `archival`, `institutional`) or
secondary (`scholarly-secondary`, `reference-secondary`, `general-secondary`).
The gate rejects an unknown type. `scripts/source_audit.py` inspects each
load-bearing claim — not a source count — and reports one of three states per
entry: **source-grade closed**, **needs-primary-strengthening**, or
**primary-not-found / secondary-record-sufficient** (declared per claim via an
entry's `audit_exceptions`, only after a real search finds no primary). The
audit inspects evidence before scores: a source is strengthened because the
record is better, never to move a number. The living matrix for the current
cycle is `docs/physics-astronomy-provenance.md`.

Qualitative criteria (reviewed, not auto-counted):

- Specific-award pages where an award's rules or history warrant it.
- Sector aggregation is **computed, never hand-edited**.
- Primary or institutional sources wherever possible; contested claims shown as
  contested, not buried.
- Fact, assessment, and interpretation kept visibly separate.
- Full internal linking; no thin pages.
- Every figure derived from the one published scoring engine.
- At least one synthesis report.

When all of the above hold, the domain is declared, in this document:

> `<Domain> Recognition Layer: closed / mature v1.0`

This gives the project **versioned knowledge maturity** — not "a site with N
pages" but "Physics recognition system — mapped; Biology — mapped; …".

## Corpus-relation semantics & denominator discipline

An award page's third layer links cases to the award's structure. Two rules keep
this from drifting into causal-looking statistics:

- **Descriptive, not causal.** A relation states *what the record connects*, never
  *why* an outcome occurred, unless the record establishes causation. Each
  relation separates `architecture_element` (which part of the apparatus) from
  `interaction_type` (what the record shows — a controlled vocabulary), carries a
  `claim`, and is either anchored to a record-grade source or backed by a
  documented exception. "Not among the 1957 laureates" is allowed; "excluded
  because the committee favoured theory" is a synthesis hypothesis, not a corpus
  fact.
- **Corpus frequency ≠ field prevalence.** The corpus is purposively built around
  recognition-gap cases, so counts within it describe the dataset, not the field.
  Every computed finding must show its denominator and carry this caveat: *"N of
  the M cases in the governed corpus exhibit X"*, never *"X dominates physics."*

These hold for the coming comparison layer too: it reports distributions with
denominators, and never infers prevalence or causation from descriptive relations.

## Cycle order

1. **Cycle 01 — Physics & Astronomy** *(open)*
2. Cycle 02 — Biology, Medicine & Genetics
3. Cycle 03 — Mathematics & Computing
4. Then, and only then, outside the sciences: Literature → Peace →
   Human Rights / Law → Arts → Social Sciences → Technology / Engineering.

Physics and Astronomy begin as one cluster during construction and may be split
once each is dense enough to stand alone.

---

## Cycle 01 — Physics & Astronomy Recognition Architecture — OPEN

Opened: 2026-09-09. Run `python scripts/domain_status.py` for live status.

We do not exit this cycle until `physics-astronomy` meets the Definition of Done
above. Deferred until then: sector pages for other domains, public data
export / API, RSS, and any commercial layer. Uniqueness of the data and the
methodology must come first; programmatic consumption does not create authority.
