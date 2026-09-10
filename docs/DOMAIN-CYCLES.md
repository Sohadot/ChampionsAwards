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

### Mechanism audit (coverage, not label count)

A case can carry a measured recognition gap and no evidenced mechanism. That is a
legitimate result — but only when it is the outcome of a search, never a silence.
A `mechanism_audit` on the case records that search: the date, the mechanisms
considered (each a published concept), the finding
(`mechanism-evidenced` / `no-mechanism-evidenced`), a note stating what the
record did and did not support, and the best sources found. Validation rejects an
audit whose finding disagrees with the case's own pattern tags, so the audit and
the tags can never say different things.

From this the engine computes **mechanism accounting**: how many cases are
accounted for — by evidence for a mechanism, or by a dated audit that searched and
found none — and how many remain unaudited. Coverage measures how thoroughly the
corpus has been examined, which is a different question from how many mechanisms
recur, and the two are reported separately rather than blended.

Auditing a case may end in any of four ways, and three of them do not add a tag:
the record supports an existing mechanism; it supports none; a claim is corrected;
or the case is withdrawn. An audit is never a search for a label that would help a
threshold — and where the ontology does not fit the record, the finding is
"no mechanism evidenced", not a new name invented to fill the gap.

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

### Canonical aggregation engine

All domain statistics come from one module, `scripts/domain_comparison.py`;
`domain_status.py`, the sector page, the synthesis, and any export read from it,
so a number is never computed twice. It returns **observations only** (medians,
distributions, counts, ranges, evidenced pattern support) — never `conclusions`.
Quartiles use one frozen inclusive definition (tested in
`scripts/test_domain_comparison.py`); every layer carries its own denominator
(DDI cases, RLS systems, and award relations are distinct populations); and each
result carries a deterministic, data-derived `corpus_snapshot` id so a finding is
attributable to the exact corpus it was computed from — "true for Cycle 01
corpus vN", not an eternal claim.

**The corpus is dated by its own data.** A comparison declares `data_through` —
the most recent `last_reviewed` among the inputs actually included — never the
build date. Re-running the build on a later day cannot change a published figure;
a changed date always means a changed review. Build time exists only as
operational metadata (`generated_at()`), excluded from the identity and from
every stable output. A figure is therefore cited in one form:

> corpus `<snapshot>` + methodology `<version>` + data through `<YYYY-MM-DD>`

**Publication boundary.** The engine writes no file into the site output
directory. Cycle 01 defers public data export and APIs, so its JSON report is a
build-internal artifact under `reports/` (untracked) for inspection, diffing and
tests. Representations that *are* published — the sector page, the synthesis —
call `build_comparison()` at build time and render HTML. The machine checks
enforce both rules: no wall-clock value may enter the result, and no JSON
endpoint may appear under `public/`. The machine checks freeze the quartile
definition, guarantee determinism, and enforce the eligibility and
denominator rules.

### Sector reference pages

A sector page (`/sectors/<domain>`) is layer 6, and it is a **representation of
the engine, never a second calculation**. `scripts/generate_sectors.py` calls
`build_comparison()` at build time and renders HTML; there is no authorable
`sectors/*.yaml` that could contradict the computed result, and no number on the
page is hand-entered. Its order is fixed, from landscape to boundary:

1. **Recognition landscape** — the populations and the corpus identity.
2. **Recognition gap distribution** — the actual distribution drawn from the
   values (box, median, whiskers, one dot per case), not summary cards.
3. **Structural mechanisms** — evidenced support with the denominator and the
   corpus-frequency caveat in the same context, never in a footnote.
4. **Recognition systems** — multidimensional profiles in fixed alphabetical
   order. No podium, no "#1": the page presents profiles, not a ranking.
5. **Award architecture** — the mapped award's rules, then its corpus relations
   split into documented outcomes and constraints / non-award records.
6. **Case matrix** — every case with DDI, observed recognition, gap, and its
   evidenced mechanisms.
7. **Methodological boundary** — what the page does not claim, and domain
   maturity as measured, including thresholds not met, on the page itself.
8. **Provenance & reproducibility** — instruments, corpus snapshot, data
   through, and the one citation form.

**No narrative finding unless it is literally derived from the engine.** A
generated reading states a count against its denominator — "8 of 10 governed
cases exhibit evidenced credit misattribution — the highest support count in
this corpus" — and never that a mechanism is dominant, typical, or proven.
`generate_sectors.py` lints its own generated prose for banned superlatives and
for generalisation terms, and fails the build on a hit;
`scripts/test_sector_page.py` checks that the page's figures equal the engine's,
that the distribution plots every case once, that maturity reports the
established count, that systems are unranked, and that no data endpoint is
emitted.

### Synthesis reports (layer 7)

Layer 7 is where reference authority begins, so it carries the strictest rule in
the project: **a report may not type a statistic.** Report prose states figures
as tokens resolved at build time from the canonical engine; a bare number or an
unknown token fails validation (`scripts/synthesis_figures.py`,
`validate_report` in `scripts/validate_content.py`). A report declares
`derives_from` — the governed corpus that carries its evidence — instead of its
own source list, and its page links every case behind its figures.

Observation and interpretation are kept structurally apart, not merely
separated by tone:

- an **observation** is a statement about the corpus that cites at least one
  engine figure and declares the figures it rests on;
- a **hypothesis** must state its basis in the corpus *and* what would refute
  it. A claim that cannot be refuted is not published as one.

An observation may not use a universal ("every", "never", "all"): the engine
computes counts, so an observation states a count with its denominator, and a
universal claim belongs among the hypotheses where it carries a refutation
condition. When the corpus later meets a hypothesis's refutation condition, the
hypothesis is marked `state: refuted` and keeps an `outcome` recording what
refuted it and when. **A refuted hypothesis stays published, struck through, not
deleted** — the record of a discarded interpretation is part of the evidence, and
the corpus that refuted it is the same corpus that suggested it.

This is the reading of "the model must yield to the evidence" that a build can
enforce: if the corpus changes, the report's numbers change with it, and a
hypothesis stays labelled as a hypothesis until evidence — not confidence —
promotes it.

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
