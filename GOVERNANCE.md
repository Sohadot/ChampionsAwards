# Editorial governance

ChampionsAwards earns trust by constraint, not by assertion. Every entry passes
an automated gate before it can be published. The gate is code, not a promise:
`python scripts/build.py` fails if any rule below is violated.

## The build pipeline

1. **`validate_content.py`** — well-formedness. Required fields, valid slug,
   minimum summary length, and the *shape* of optional blocks (`sources`,
   `assessment`, `key_facts`, `analysis`, `status`).
2. **`quality_gate.py`** — publication policy (below).
3. **`generate_core.py` / `generate_pages.py`** — render pages. Draft entries
   are skipped and never emitted.
4. **`generate_rankings.py` / `generate_sectors.py`** — computed aggregate pages,
   rendered from the canonical engine, never hand-edited.
5. **`generate_sitemap.py`** — sitemap of published URLs only.

`python scripts/run_checks.py` runs the machine checks behind these rules
(frozen statistics, determinism, denominators, the publication boundary, the
sector page's fidelity to the engine, and the synthesis rules below). A failing
check means a claim the project makes is no longer enforced by its code.

## Publication policy (enforced)

An entry is **published** unless it declares `status: draft`. Published entries
must satisfy:

- **Sourcing.** At least one reference in `sources`, each with a title, a valid
  `http(s)` URL, and a `type` from the source-authority taxonomy
  (`SOURCE_TYPES`: primary, archival, institutional, scholarly-secondary,
  reference-secondary, general-secondary). Unsourced work stays `status: draft`.
  `scripts/source_audit.py` reports, per load-bearing claim, whether it is
  anchored to a record-grade source; see `docs/DOMAIN-CYCLES.md`.
- **Review date.** A `last_reviewed` field in ISO `YYYY-MM-DD` form.
- **Justified scores.** Any `assessment` / `rls_assessment` block must include a
  `rationale` for its dimensions, and every dimension must be a number 0–100.
- **Score-level provenance.** A published assessment must include an `evidence`
  map that ties every dimension — and `observed_recognition` — to specific
  `sources` by 1-based index, so each judgment is traceable
  (source → evidence → judgment → score → gap → rank).
- **Computable gap.** A published DDI `assessment` must state a numeric
  `observed_recognition`, so its recognition gap is defined and the Recognition
  Gap Index is complete.
- **Traceable facts.** Each `key_facts` entry may cite a `source` by 1-based
  index into `sources`; out-of-range citations fail the build.

## Instrument type boundaries (enforced on all entries)

The two instruments are not interchangeable, and misplacing one is a modeling
error, not a formatting one — so the gate rejects it regardless of status:

- a DDI `assessment` (individuals) is valid only in the `unawarded` cluster;
- an `rls_assessment` (systems) is valid only in the `recognition-systems`
  cluster.

These sets live in `scripts/config.py` (`ASSESSMENT_CLUSTERS`, `RLS_CLUSTERS`)
and are also honored by the rankings generator as defense in depth, so a stray
assessment can never pollute an index even if the gate were bypassed. Widening a
set is a deliberate change made together with the `/methodology` page.

## Neutrality discipline (enforced on all entries)

Entry prose may not contain unscoped superlatives (e.g. "definitive",
"the greatest", "unrivaled", "sovereign-grade"). The banned list lives in
`scripts/config.py` (`BANNED_TERMS`) and is scanned across every prose field.
The goal is a reader who trusts the reasoning, not the tone.

## Scoring integrity

The Deservingness Index (DDI) weights live in one place — `DDI_DIMENSIONS` in
`scripts/config.py` — and are mirrored by the client-side calculator and the
`/methodology` page. Changing dimensions, weights, or bands is a **version
bump** (`methodology_version` in `src/data/site.yaml`), so past scores remain
interpretable.

## Domains and deepening cycles

Every published scored entry is placed in a recognition domain: individuals
carry a single `domain`, systems carry a `domains` list, and both must reference
a domain registered in `scripts/config.py` (`DOMAINS`). The gate rejects an
orphaned scored entry. Cases may also declare `patterns` — structural-cause
concepts (e.g. `credit-misattribution`) that must resolve to a **published**
concept, keeping the ontology connected. Every declared pattern on a published
case must also carry `pattern_evidence` (source refs proving the mechanism in
that case); the maturity report counts a case toward a pattern only when that
evidence is present, so a pattern is always a sourced claim, never a bare tag.

**Recurrence is not replication.** A pattern becomes *established* in a domain at
`PATTERN_ESTABLISHED_MIN` **independent contexts**, not at that many cases. A case
may declare, per pattern, the `pattern_context` its instance belongs to — one
institution, one legal regime, one apparatus — from the vocabulary in
`RECURRENCE_CONTEXTS`; a case that declares none is its own context. Both figures
are published: `support` counts cases, `independent_support` counts contexts, and
only the second decides lifecycle status. The rule exists because two observations
of one regime are not two replications of a mechanism, and without it the gate
would promote a regime's signature to an established finding automatically. An
unknown context string fails validation rather than silently creating a false
independence.

The project deepens one domain to maturity before opening the next. The model,
the seven layers, and the machine-checked Definition of Done live in
[`docs/DOMAIN-CYCLES.md`](docs/DOMAIN-CYCLES.md); `scripts/domain_status.py`
reports each domain's status from the same scoring engine the site uses.

Two domains are closed: Physics & Astronomy and Biology & Medicine, both at
mature v1.0. Maturity is governed by **DoD v1.1**: completeness of accountable inquiry, not
conformity of findings to a target. The v1.0 requirement of four established
mechanisms is superseded — it measured what a corpus happened to contain rather
than how thoroughly it was examined — and is replaced by complete mechanism
accounting. Pattern recurrence is still measured and published; it no longer
decides whether a domain is done. The full rationale, and v1.0 kept visible as
superseded, are in `docs/DOMAIN-CYCLES.md`.

## Synthesis reports (enforced)

A synthesis is where prose is most tempted to outrun the evidence, so reports in
`src/data/reports/` are held to rules the gate can check:

- **A report declares the corpus it derives from** (`derives_from`, a registered
  domain) instead of restating sources. Its evidence is that governed corpus, and
  every case in it already carries audited sources and provenance anchors.
- **A report may not type a statistic.** Figures appear as tokens —
  `{median_gap}`, `{pattern_support:credit-misattribution}` — resolved at build
  time from the canonical engine (`scripts/synthesis_figures.py`). A bare number
  in report prose fails validation; years are the only literal numbers allowed.
  An unknown token fails too, so a report cannot cite a figure the engine does
  not produce.
- **Observation and hypothesis stay structurally apart.** An observation must
  cite at least one figure and declare the figures it rests on. A hypothesis must
  state its basis in the corpus *and* what would refute it: a claim that cannot
  be refuted is not published as one.
- **Limits are published with the report**, on the page rather than in a footer,
  including the selection effect that makes corpus frequency ≠ field prevalence.

## Award anatomy: four layers (enforced where present)

An award page separates what the rules say, when those rules took effect, how far
the award's own archive is open, and where the corpus touches the apparatus.
`rule_history` records, per rule element, the current text, its effective date,
what is known of the state before it, and — for each corpus event — whether the
governing version is `established`. Validation rejects claiming a version is
established when the rule cited takes effect after the event. `archive_visibility`
records the secrecy rule, the release horizon with the date it was checked, and a
state per case drawn from `ARCHIVE_VISIBILITY_STATES`: nomination-documented,
no-nomination-in-open-archive, archive-year-not-released, deliberation-not-reached.
The third and fourth exist because "we found nothing" and "those years are closed"
are different facts and a corpus must not collapse them into silence. The fourth
is deliberately narrow: it records that no deliberation record was reached, not
that none is obtainable — the Statutes allow access to be granted after fifty
years, so the stronger claim would assert more than was checked.

## Temporal validity of rules (enforced)

An official source for today's rule is not evidence about a decision taken before
that rule existed. Where a corpus relation asserts that a time-dependent rule bore
on a case — `eligibility-constraint`, `sharing-constraint`, `posthumous-constraint`
— it must carry a `rule_at_time` block stating the event date, the rule in force
then, and either a record-grade anchor or a documented exception. Validation
rejects applying a rule to an event that predates it. Where the rule in force
cannot be established, none is applied, and the outcome stands without a
rule-based explanation.

## Composite domains (enforced)

Where a domain's name joins two recognition cultures (`DOMAIN_SUBFIELDS` in
`scripts/config.py`), every entry placed in it declares a `subfield`, and the gate
rejects an entry that does not. The engine then reports subfield coverage —
cases, systems and awards per side — as an observation. **A domain maturity
threshold does not by itself establish subfield coverage:** a composite domain can
meet every criterion with one half empty, and the coverage report exists so that a
maturity claim has to say which half it rests on. Coverage gates nothing, and the
Definition of Done is unchanged.

## Concept semantics (enforced)

Concepts declare a `concept_type`: `mechanism` (operative and case-level),
`recognition-pattern` (an umbrella tendency covering several mechanisms) or
`framework-concept` (a distinction the project reasons with). Only a `mechanism`
can be evidenced in a case, so only a mechanism may appear in a case's `patterns`
or in a `mechanism_audit.considered` list — an umbrella tendency or a framework
distinction cannot be a failed mechanism test, and counting it as one makes the
ontology look narrower than it is.

## Mechanism audits (enforced)

A case may declare a `mechanism_audit`: a dated record of the search for a
structural mechanism, naming the mechanisms considered, the finding
(`mechanism-evidenced` or `no-mechanism-evidenced`), what the record did and did
not support, and the best sources found. The gate rejects an audit that
contradicts the case's own `patterns`. This makes "no mechanism recorded" a
documented decision rather than a silence, and lets the engine report **mechanism
accounting** — how much of the corpus has actually been examined — separately from
how many mechanisms recur.

"No mechanism evidenced" is not the same as "unexplained". A case whose
recognition roughly matches assessed merit has no deficit outstanding, so finding
no mechanism there is the expected result. The engine therefore reports
**explanatory coverage** against the published gap bands: unexplained
under-recognition (no mechanism *and* a gap at or above the `under-recognized`
floor) is counted separately from aligned cases that require no explanation.

## Ontology revisions (enforced)

The set of audit-eligible mechanisms grows. An audit recording "five mechanisms
considered" is therefore uninterpretable on its own: the reader cannot tell
whether five was all of them. Every audit records the **ontology revision** it
was performed under (`ontology_revision`, an immutable id such as `MOR-004`) and
the evidence for that revision (`revision_basis` — the commit that put it in
force). Ids are ordered by the commit that changed the set, not by date, because
more than one revision can land on one day. A revision is never edited once
published; a change creates the next id.

Two figures follow, and the project keeps them apart:

- **Completeness at its own revision** — did the audit test everything that was
  eligible on the day it ran? A "no" is a defect in the audit. Where a legacy
  audit did not, the gap is declared in the case file (`incomplete_at_revision`)
  naming exactly the untested mechanisms. A declared gap is a known defect; a
  gap inferred later from a shifting denominator is an unnoticed one. Nothing is
  ever added to `considered` without re-running the audit, because that would
  fabricate a test that never happened. From `MOR-006` onward the declaration is
  unavailable: a new audit must simply be complete.
- **Currency against the revision in force** — does the audit cover today's
  mechanism set? A "no" is not a defect, and it gates nothing. A closed domain
  does not become immature because the vocabulary later acquired a word.

**Mechanism accounting at 100 per cent** asserts only that every case carries
either evidence for a mechanism or a dated audit that searched and found none.
It does **not** assert that every audit tested every eligible mechanism; that is
the completeness figure, reported separately. `docs/ontology-revisions.md`
carries the registry and the current measurements.

## Correction policy

Being wrong in public is normal and fixable. Substantive corrections are made
by editing the entry and advancing its `last_reviewed` date; a well-sourced
challenge is grounds for revision. The published `/protocol` page states these
commitments to readers.
