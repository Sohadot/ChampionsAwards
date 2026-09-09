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
