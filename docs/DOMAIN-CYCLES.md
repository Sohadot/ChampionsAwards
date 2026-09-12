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

## Definition of Done — DoD v1.1

> **Maturity is completeness of accountable inquiry, not conformity of findings
> to a target outcome.**

A domain is "mature v1.0" when its inquiry is complete and recorded — not when
its findings came out a particular way. The criteria below are enforced-as-measured
by `scripts/domain_status.py`, which reads the same engine and the same
provenance audit the site publishes.

Measured criteria:

- **DDI cases ≥ 10** (`DOMAIN_DOD`) — high-quality, sourced individual contributions.
- **RLS systems ≥ 3** (`DOMAIN_DOD`) — relevant recognition systems scored.
- **Mechanism accounting = 100 %** (`DOMAIN_DOD_ACCOUNTING`) — every case either
  carries one or more mechanisms backed by `pattern_evidence`, or carries an
  explicit, dated audit concluding that no evidenced mechanism was found. It does
  **not** assert that every audit tested every mechanism eligible at the time;
  that is completeness at revision, measured and reported separately.
- **Cases unaudited = 0** — nothing left unexamined.
- **Source-grade closure** — every load-bearing claim closed against a
  record-grade anchor or carried by a documented exception (the "known-status"
  model), measured by `scripts/source_audit.py`.
- **Award anatomy** — at least one award in the domain mapped in full: formal
  architecture plus corpus relations.
- **Synthesis** — at least one published report deriving from this domain, with
  hypotheses that can be confirmed or refuted.

Qualitative criteria (reviewed, not auto-counted): computed sector aggregation,
primary or institutional sources wherever possible, contested claims shown as
contested, fact/assessment/interpretation kept visibly separate, full internal
linking, no thin pages, every figure derived from the one published engine.

Reported alongside maturity and **deliberately not gates** (`DOMAIN_OBSERVED_ONLY`):
evidenced mechanisms, established mechanisms, emergent mechanisms, and cases left
unexplained after audit. These describe what a corpus turned out to contain.

### DoD v1.0 — superseded 2026-09-10

v1.0 required, in addition to the case and system thresholds:

- **Established structural-cause patterns ≥ 4.**

That requirement is withdrawn. The reason is recorded here rather than edited
away:

> The v1.0 requirement of four established mechanisms was set before any domain
> had completed a full mechanism audit. Cycle 01 ran every layer that precedes
> judgment — case deepening, provenance, source-grade auditing, award anatomy,
> comparison, synthesis, and a dedicated mechanism audit of the two unexplained
> cases — and the established count stayed at 2 while mechanism accounting
> reached 10/10. That is evidence that the count measured an empirical outcome of
> the corpus rather than the completeness of the audit, and that holding it as a
> gate created an incentive to seek additional labels or cases simply to meet a
> target. v1.1 therefore removes the established-pattern count from the domain
> maturity criteria and replaces it with complete mechanism accounting. Pattern
> recurrence continues to be measured and reported, but it no longer determines
> whether the evidence has been fully investigated.

A milder version of the same mistake was also rejected: "≥ 2 established +
100 % coverage" would have turned today's observed figure into tomorrow's
threshold. A mature field may evidence one recurring mechanism, or none that the
record can prove; requiring two would rebuild the same incentive to invent a
taxonomy or pad a corpus to clear a gate.

**What did not change:** `PATTERN_ESTABLISHED_MIN` remains 2. That is a
definition of what makes a pattern recurring rather than singular, and it stands.
Nothing in the data moved because of this decision: credit misattribution and
institutional exclusion remain established, institutional gatekeeping and
theory-experiment asymmetry remain emergent. The only thing that changed is the
answer to "when is a domain's inquiry complete?"

Pattern establishment is a property of the **result**. Mechanism accounting is a
property of the **investigation**. v1.1 gates the second and reports the first.

### Pattern lifecycle

A structural cause is not counted just because it is named once. Each pattern in
a domain is:

- **emergent** — exhibited below the threshold; recorded, but **not** counted
  toward the DoD; or
- **established** — exhibited in at least `PATTERN_ESTABLISHED_MIN` (2)
  **independent contexts** in that domain.

Contexts, not cases. Two cases sharing one institution, legal regime or apparatus
are two observations of one context, and promoting that to an established finding
would call a regime's signature a replicated mechanism. Both figures are
published — `support` counts cases, `independent_support` counts contexts — and
only the second decides status.

The distinction is reported, never required (DoD v1.1): a real structural pattern
must actually recur to be called established, but how many a domain evidences
does not decide whether the domain is mature. Patterns are surfaced by auditing
the cases, never imposed on them.

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
label. If the evidence yields two established patterns, the domain reports two; a
truthful count is preferred to a manufactured one, and under DoD v1.1 that count
gates nothing.

### Mechanism audit (coverage, not label count)

A case can carry a measured recognition gap and no evidenced mechanism. That is a
legitimate result — but only when it is the outcome of a search, never a silence.
A `mechanism_audit` on the case records that search: the date, the mechanisms
considered (each a published concept), the finding
(`mechanism-evidenced` / `no-mechanism-evidenced`), a note stating what the
record did and did not support, the best sources found, and — since MOR-006 —
the **ontology revision** the search was performed against, with the commit that
establishes it. Validation rejects an audit whose finding disagrees with the
case's own pattern tags, so the audit and the tags can never say different things.

The revision matters because the denominator moves. "Five mechanisms considered"
is complete under one revision and five-of-seven under another, and without the
revision recorded, every addition to the ontology silently made every existing
audit less complete with nothing measuring it. Two figures now follow and are
kept apart: **completeness at the audit's own revision** (a "no" is a defect,
declared in the case file) and **currency against the revision in force** (a "no"
is a dated fact that gates nothing — a closed domain does not reopen because the
vocabulary acquired a word). A defect in the first figure is repaired
by a separate, dated `mechanism_reaudit` that tests the **whole** current
ontology and returns a verdict per mechanism; the original audit is kept exactly
as performed, so the record says the audit was incomplete and was later
remediated rather than presenting a past that was never wrong. The registry, the
assignment method and the current measurements are in
[`ontology-revisions.md`](ontology-revisions.md).

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

### Temporal validity of rules

Learned from the Franklin case, where this project applied a 1974 statute to a
1962 decision:

> **Temporal validity is part of provenance.** It is not enough that a source is
> official and a rule is current. When a rule is tied to a historical event, the
> record must show which version of the rule was in force at that time.

The requirement is deliberately narrow — it applies only where a rule has
changed. A relation whose `interaction_type` is one of
`TIME_DEPENDENT_INTERACTIONS` (eligibility-constraint, sharing-constraint,
posthumous-constraint) must carry a `rule_at_time`: the `event_date`, a statement
of `rule_in_force`, and either a record-grade `record_anchor` or a documented
`exception`. Optional `effective_from` / `effective_to` date the cited rule, and
validation rejects the anachronism directly: a rule effective from 1974 may not
be applied to an event in 1962. Provenance entries may carry the same dating.

Where the rule in force cannot be established, none is applied. The outcome then
stands as an outcome without a rule-based explanation — which is what the
Franklin entry now says about 1962.

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

The Definition of Done carries its own version (currently DoD v1.1); a closed
knowledge layer carries the layer's version (`mature v1.0` at first closure).
They are different things and are never merged into one number.

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

1. **Cycle 01 — Physics & Astronomy** *(closed 2026-09-10 — mature v1.0)*
2. **Cycle 02 — Biology, Medicine & Genetics** *(closed 2026-09-11 — mature v1.0)*
3. **Cycle 03 — Mathematics & Computing** *(closed 2026-09-12 — mature v1.0)*
4. Then, and only then, outside the sciences: Literature → Peace →
   Human Rights / Law → Arts → Social Sciences → Technology / Engineering.

Physics and Astronomy begin as one cluster during construction and may be split
once each is dense enough to stand alone.

**Cycle order is not the domain registry.** A cycle is an episode of work; a
domain's lifecycle is a property of the domain. `DOMAIN_REGISTRY` in
`scripts/config.py` carries the second, with three states — `planned`, `open`,
`closed` — and aggregation derived from them rather than typed out. The first two
domains of the list above, Literature and Peace, are registered as `planned`:
they produce no sector hub, enter no maturity report, and cannot be the corpus a
synthesis derives from, but an entry may now name them. That is what a planned
domain is for. Registering a domain is not opening a cycle, and it schedules
nothing.

## Science Foundation Review v1.0 — 2026-09-12

After Cycle 03 closed, one pass over the whole repository asked whether the three
closed scientific layers still satisfy the current architecture without hidden
legacy assumptions. It added no case, system or concept, changed no score, and
opened no cycle.

**The review is not clean, and `Scientific Recognition Foundation — stable v1.0` is
not declared**, in either of its two passes. Three defects were fixed as wording corrections — two documents
typing a moving corpus snapshot, the Physics report stating the establishment
threshold in cases rather than contexts, and two case entries still denying they
carry a mechanism after the ontology review reclassified them. One material finding
is open: **20 of 22 mechanism audits predate the ontology they are now measured
against**, and nothing in the gate noticed. Nothing was back-filled, because writing
a concept into a `considered` list without running the test would fabricate dated
evidence. Full account and the three options:
[`science-foundation-review.md`](science-foundation-review.md).

**Second pass, after both findings were closed by construction.** The ontology
revision model (MOR ids, recorded per audit, enforced by the gate) and the domain
registry (`planned` / `open` / `closed`, with aggregation derived from it) were
built, and the re-run measured what they exposed. Currency is 2 of 22 as
expected — but **completeness at the audit's own revision is 10 of 22**: twelve
audits failed to test a mechanism that was already eligible on the day they ran.
Two of those gaps touch published results — `posthumous-recognition` is evidenced
in no case in the corpus and was never tested on Vera Rubin, and
`theory-experiment-asymmetry` was never tested in Biology & Medicine at all,
Rosalind Franklin included. Closing either means re-auditing an entry in a closed
layer against sources, which is an evidential act and a decision, not a refactor.

The three domains remain MATURE v1.0 individually; that status is measured per
domain and is unaffected, deliberately — a growing vocabulary must not be able to
retroactively unmake a closed layer. What is withheld is the cross-cutting claim
that the foundation as a whole needs no further work.

---

## Cycle 01 — Physics & Astronomy Recognition Architecture — CLOSED

Opened 2026-09-09. Closed 2026-09-10.

> **Physics & Astronomy Recognition Layer — mature v1.0**
> Closed at corpus snapshot `27036032e0e9` · data through 2026-09-10
> The current snapshot has moved since closure and is deliberately not copied here
> — run `python scripts/domain_status.py` for it. It moved twice on 2026-09-12:
> once when the Wolf Prize anatomy documented the inaugural 1978 physics prize to
> Chien-Shiung Wu, a relation that existed before the corpus could see it, and again
> when the Wolf Prize's track-record score was corrected. A closed layer is closed
> at a stated snapshot, not frozen against later evidence.
> Governed by DoD v1.1 (the layer closes at v1.0; the version numbers are
> different things — v1.1 is the Definition of Done, v1.0 is this knowledge layer's
> first closure)

Every criterion measured and met (`python scripts/domain_status.py`):

| Criterion | Measured |
| --- | --- |
| DDI cases ≥ 10 | 10 |
| RLS systems ≥ 3 | 3 |
| Mechanism accounting = 100 % | 10/10 |
| Cases unaudited = 0 | 0 |
| Source-grade closure | 13/13 entries closed |
| Award anatomy | Nobel Prize in Physics mapped (11 architecture elements, 8 corpus relations) |
| Synthesis | *Recognition Failure Patterns in Twentieth-Century Physics* |

Reported, and required by nothing:

| Observation | Value |
| --- | --- |
| Evidenced mechanisms | 4 |
| Established mechanisms | 2 (credit misattribution 8/10, institutional exclusion 4/10) |
| Emergent mechanisms | 2 (institutional gatekeeping, theory-experiment asymmetry) |
| Cases unexplained after audit | 1/10 (Bose — audited, no mechanism evidenced) |

Two results are worth naming, because they are what closure actually bought:

- **Bose is not a deficiency.** After a dated audit against every published
  mechanism, he is a case *known* to be unexplained by the current ontology,
  with the Nobel nomination archive showing eleven nominations and a commissioned
  expert evaluation. "Known unexplained" is information; "not yet looked at" is not.
- **Rubin refuted a published hypothesis of ours.** The audit found institutional
  exclusion evidenced with no evidenced credit misattribution — exactly the
  refutation condition the synthesis had stated. The hypothesis stays on the page,
  struck through, with what refuted it. That is worth more than a 4/4 score.

**What the closure does not license.** Public data export / API, RSS and any
commercial layer were deferred *until this cycle concluded*; that condition has
now lapsed, but nothing has been enabled by it. Publishing a machine-readable
endpoint remains a separate decision, not taken here — the engine still writes its
report to `reports/`, outside the published site.

**Post-closure change (2026-09-11).** The temporal-validity rule introduced in
Cycle 02 was applied retroactively to this corpus: the Rubin posthumous-constraint
relation now carries a `rule_at_time` showing that the Nobel prohibition on
posthumous awards was in force (from 1974) at the time of the 2016 event it is
applied to. The snapshot therefore moved from `27036032e0e9` to `6f43ff80ba61`.
No score, mechanism, count or finding changed — the relation gained the date it
should always have carried. A closed layer is not frozen: it stays closed and
stays correctable, and each correction is recorded rather than folded silently
into the original declaration.

**Not added to close it:** no eleventh physics case, no invented mechanism, no
lowered threshold. The one governance change (DoD v1.1) was made *after* the
evidence was complete, was recorded with its rationale, and moved no datum.

Next: **Cycle 02 — Biology, Medicine & Genetics**, run on the method Cycle 01
produced, from its own evidence — without reinventing the rules of maturity.

---

## Cycle 02 — Biology, Medicine & Genetics — CLOSED

Opened: 2026-09-11. Run `python scripts/domain_status.py` for live status.

The cycle opened with a **baseline requalification**, not an expansion. Cycle 01
produced a standard the inherited entries had never been held to, and an
inherited corpus is not automatically compliant with the standard that superseded
it. Round 1 re-qualified the three existing cases (Mendel, Avery, Franklin) and
the Lasker Award entry, corrected a historical error in the Franklin case, and
introduced temporal-rule validity. Full account:
[`cycle-02-requalification-ledger.md`](cycle-02-requalification-ledger.md).

The result is a smaller, narrower baseline: median gap 42 → 24, established
mechanisms 1 → 0, source-grade closure 2/6 → 6/6, sources on the three cases
4 → 15. Under DoD v1.1 the weakened findings block nothing; the completed
accounting is what counts.

Round 2, **Individuals expansion, stage 1** (2026-09-11): researched six,
published four — Schatz, Ball, Stevens, Hilleman; the two reserves were not
needed. The corpus stands at 7 cases with mechanism accounting at 7/7 and
source-grade closure at 10/10. One of the four was accepted expressly as a
control, and returned the corpus's first "recognition roughly matches assessed
merit" reading. Comparison read, including the five gaps that should govern the
next three names: [`cycle-02-stage1-read.md`](cycle-02-stage1-read.md).

Round 3, **Individuals expansion, stage 2** (2026-09-11): Just, Apgar and De —
each chosen to test a specific gap rather than to add a name. The corpus is now
at 10 cases and paused for assessment. Institutional exclusion is evidenced for
the first time in biology (1/10, emergent — not established); the instrument
produced its first negative gap (Apgar, −2); and five of ten cases are
measured-but-unexplained after a dated audit. Full recompute:
[`cycle-02-stage2-read.md`](cycle-02-stage2-read.md).

Round 4, **Ontology & explanatory-coverage hardening** (2026-09-11): concepts
now declare a `concept_type`, only `mechanism` concepts may be tested against a
case, and the engine reports explanatory coverage against the published gap bands
so that alignment between merit and recognition is no longer counted as an
explanatory failure. No case data changed. Recomputed: unexplained
under-recognition is **3 of 8** in biology and **1 of 10** in physics; two biology
cases are aligned and require no mechanism. Full account:
[`cycle-02-explanatory-coverage.md`](cycle-02-explanatory-coverage.md).

Round 5, **Nobel Prize in Physiology or Medicine — award anatomy**
(2026-09-11): four layers rather than three. Biology needed two the physics page
did not: **historical rule state** (what is in force, since when, what preceded
it, and whether the version that governed each corpus event is established at
all) and **archive visibility** (how far the award's own record is open, keeping
"no nomination found" apart from "those years are not released"). Corpus
interaction is bounded to the three cases where this award's record is
load-bearing — Schatz, Avery, Franklin. No second RLS: the Nobel Prize System
entry carries system legitimacy, this page carries award-level anatomy.

Round 6, **synthesis** (2026-09-11): *Explained, Aligned, Unresolved —
Recognition Outcomes in Biology & Medicine*, structured on three outcome classes
rather than a catalogue of failures, with cross-domain figures computed through
`{figure@domain}` tokens rather than transcribed. It also corrected two claims in
the physics synthesis that DoD v1.1 had left stale — recorded on that report's own
page, struck through, under a new `corrections` block.

Round 7, **sector reference** (2026-09-11): `/sectors/biology-medicine` published
from the same engine, carrying the explanatory-coverage panel and the domain's
first negative-gap case in its distribution.

No fourth recognition system is needed: Nobel, Lasker and Wolf already satisfy
the RLS threshold. The work is making those three reliable, not adding a fourth.

### Closure

> **Biology & Medicine Recognition Layer — mature v1.0**
> Closed at corpus snapshot `919d2f889371` · data through 2026-09-11 · governed by DoD v1.1
> The current snapshot has moved since closure and is deliberately not copied here
> — run `python scripts/domain_status.py` for it. The Wolf Prize anatomy entered this
> domain's award layer on 2026-09-12 without documenting a relation to a biology case,
> and the Wolf Prize's track-record score was corrected the same day; the first did
> not move the snapshot and the second did.

| Criterion | Measured |
| --- | --- |
| DDI cases ≥ 10 | 10 |
| RLS systems ≥ 3 | 3 |
| Mechanism accounting = 100 % | 10/10 |
| Cases unaudited = 0 | 0 |
| Source-grade closure | 13/13 entries |
| Award anatomy | Nobel Prize in Physiology or Medicine — four layers |
| Synthesis | *Explained, Aligned, Unresolved* |

Reported, required by nothing:

| Observation | Value |
| --- | --- |
| Audit-eligible mechanisms evidenced | 3 of 6 ontology concepts |
| Established mechanisms | 1 (credit misattribution, 3/10 cases) |
| Emergent mechanisms | 2 (institutional exclusion, delayed recognition) |
| Cases with a recognition deficit | 8/10 |
| Unexplained under-recognition | 3/8 |
| Aligned, no mechanism required | 2/10 |

**Biology is not a second copy of Physics.** The cycle added three capabilities
to the project, each forced by a case rather than designed in advance:

1. **Temporal-rule provenance** — from the Franklin error. A rule may be applied
   to a past event only where the record shows which version was then in force;
   validation rejects the anachronism directly.
2. **Archive-visibility semantics** — from the Nobel Medicine anatomy. "No
   nomination found", "those years are not released" and "no deliberation record
   was reached" are three different facts, and the corpus must not collapse them
   into silence.
3. **Explanatory coverage** — from the Apgar and Hilleman results. A case whose
   recognition matches assessed merit has no deficit to explain, so alignment is
   no longer counted as an explanatory failure.

**What the cycle established.** Three outcome classes, not one: some deficits
have evidenced mechanisms; some cases show no material deficit at all; and some
deficits remain unresolved after accountable inquiry. The third class is not a
weakness to hide — it is the boundary between what the record supports and what
interpretation would have to invent.

**Not added to close it:** no eleventh case, no invented mechanism, no lowered
criterion. Two cases were accepted expressly to test the instrument rather than
to accuse anyone, and one of them returned the project's first negative gap.

Next: **Cycle 03 — Mathematics & Computing**, which begins at 1 case, 3 systems,
source-grade closure 1/4, and no award anatomy or synthesis.

---

## Cycle 03 — Mathematics & Computing — CLOSED

Opened 2026-09-11. Closed 2026-09-12. Run `python scripts/domain_status.py` for live status.

Like Cycle 02, this cycle opens with a **baseline requalification** rather than an
expansion — and with one question Cycle 02 did not have to ask:

> Is Mathematics & Computing one coherent governance domain, or two recognition
> cultures collected under a single label?

Round 1 re-qualified the one inherited case (Noether) and the three recognition
systems, and audited the domain's own name. Full account:
[`cycle-03-requalification-ledger.md`](cycle-03-requalification-ledger.md).

### Composite domains

A domain whose name joins two recognition cultures can satisfy every numeric
criterion while nearly all of its knowledge sits on one side of the join. Entries
in such a domain (`DOMAIN_SUBFIELDS` in `scripts/config.py`) declare a `subfield`,
and the engine reports coverage across the halves:

> **Domain maturity threshold does not by itself establish subfield coverage.**

This is an observation and gates nothing — the Definition of Done is unchanged and
an uneven split blocks no cycle. What it refuses is the silence. Measured at the
open of Cycle 03: mathematics 1 case and 1 system, computing **0 cases** and 1
system, cross-cutting 1 system. Re-measured at the Stage 1 pause: mathematics 2
cases, computing 3, cross-cutting 0, and `comparison_meaningful` now True.

### Planned order

1. **Expansion in stages**, chosen after the baseline rather than in advance:
   4 cases → comparison and mechanism read at 5 → 3 cases → read at 8 → the last
   two chosen by what the corpus has revealed.
2. **Award anatomy**, whose subject is decided by which apparatus turns out to be
   load-bearing for the cases — not chosen now. If the corpus ends genuinely
   balanced across the join, one anatomy may satisfy the Definition of Done while
   being epistemically insufficient; in that case two are built without changing
   the threshold.
3. Synthesis, then sector reference and closure review.

### Stage 1 — the pause at 5 (2026-09-12)

The decision after requalification was to weight the first batch toward the empty
side: **3 computing + 1 mathematics**, four researched and four published, no
reserve drawn. Each was entered to test something specific, and none was entered
with a pattern assigned.

| Case | Subfield | Entered to test | DDI | Obs | Gap | Mechanism |
| --- | --- | --- | --- | --- | --- | --- |
| Barbara Liskov | computing | an award-positive control on the empty side | 85 | 90 | −5 | none |
| Karen Spärck Jones | computing | an outcome not predictable in advance | 86 | 80 | 6 | none |
| Lynn Conway | computing | exclusion held apart from recognition outcome | 85 | 75 | 10 | institutional exclusion |
| Andrew Wiles | mathematics | a documented eligibility rule, dated to its event | 86 | 94 | −8 | none |

Baseline at the pause — mathematics 2 cases, computing **3 cases** (from 0),
cross-cutting 0; gap range −8 to 17, median 6; mechanism accounting 5/5;
**unexplained under-recognition 0**; `comparison_meaningful` **False → True**;
machine-visible award relations still **0**. Full account:
[`cycle-03-stage1-read.md`](cycle-03-stage1-read.md).

Two results are worth carrying forward. Institutional exclusion is now evidenced
once on each side of the join (Noether, Conway) — the first mechanism in this
corpus to span a composite domain. And the Wiles entry demonstrates, positively
rather than defensively, what the Cycle 02 temporal machinery was built for: a
rule published by the awarding union, applied to a dated event by that Congress's
own press office, recorded in a `rule_at_time` block — and a **negative** gap
alongside it. A constraint can be real, documented and consequential for one
award without producing a present recognition deficit.

The next three cases are not chosen. The read at 5 is the input to that choice.

### Award anatomies, and the recompute at the same 5 (2026-09-12)

Two things the Stage 1 corpus exposed were corrected before any further
expansion, and no case was added, removed or rescored while doing it.

**Identity.** The section label "The Unawarded Archive" had become narrower than
its contents - Cycle 02 put two aligned cases in it, Stage 1 put a Turing laureate
in it - and the unconditional paragraph beneath it asserted a failure that was
false on four of twenty-five entries. The label is now **The Recognition Archive**,
described by the project's own three-outcome logic: *a governed archive of how
contribution and recognition align, diverge, or remain unresolved.* Display
strings only; the `/unawarded` URL and the data cluster are unchanged, so
`unawarded` survives as a corpus subset rather than as the public identity.

**Two anatomies, not one.** A composite domain with one award anatomy would leave
half its own name blind at the award layer - the failure mode `subfield_coverage`
exists to stop passing silently. The Turing Award anatomy documents 3 of 12
architecture elements and states that nine are absent because every page of the
awarding society returned HTTP 403 across three domains; the Fields Medal anatomy
documents 9 of 12 from the award's own published Statutes. Award relations in the
domain went **0 to 3**, across three interaction types, and `eligibility-constraint`
is the first of its kind in the corpus. Full account:
[`cycle-03-anatomy-read.md`](cycle-03-anatomy-read.md).

**Governance and funding are now separate by schema.** `funding_source` is a
first-class architecture field; an anatomy that says who decides without saying
who pays fails validation. Both Nobel anatomies were amended in the same pass.
The requalification had lowered the Turing independence score from 85 to 62 on
exactly this confusion; the schema is what stops the next anatomy repeating it.

The recompute answered the domain-boundary question in a form it could not take
before. Both halves now carry an award architecture under one schema, so they can
be compared element by element - and the comparison returns a large contrast:
open nomination and published committees at the Fields Medal, invitation-only
nomination and fifty-year seals at the Nobel, neither readable at the Turing
Award; a university trust, a bequest, and a single commercial sponsor. On that
evidence the Fields Medal resembles the Nobel system more than it resembles the
award in its own domain. **The two halves are comparable, and they are not
alike** - which keeps the composite name as a unit of comparison and not as a
claim of similarity. No split proposed.

One Stage 1 inference was withdrawn in the same round: the 85-86 DDI compression
is not evidence about this domain. Both mature domains show a DDI spread of 13-14
at ten cases; a spread of 1 at five deliberately top-tier cases is most
economically read as selection. That is an observation about the corpus, not
about the domain or the instrument.

### The Wolf Prize anatomy, and the second recompute at 5 (2026-09-12)

Question 5 of the anatomy read pointed at an anatomy rather than a case, and the
anatomy answered its own question in an unexpected way. The Wolf Prize has nine
fields and **no computing field**, so it cannot bridge the two halves of this
domain; the `subfield: cross-cutting` label Round 1 gave it is corrected to
`mathematics`, and the cross-cutting compartment is now empty of cases, systems
and awards alike.

What it is instead is the project's **first cross-domain apparatus**: two
documented relations, Wiles in mathematics (1995/6, shared with Langlands) and
Chien-Shiung Wu in physics (the inaugural 1978 prize, held alone). Wu is a Cycle
01 case, so a closed domain gained a relation it had always had and could not see.
Award relations: mathematics-computing 3 to 4, physics-astronomy 8 to **9**.

An award anatomy may now declare `domains` in the plural, and **a relation is
counted in the domain of the case it names, not of the award that carries it**.
Sector pages filter by the same rule. Full account:
[`cycle-03-wolf-read.md`](cycle-03-wolf-read.md).

The domain reading is otherwise unchanged - DDI still 85-86, the deficit
population still two cases with one mechanism, explanatory coverage still
complete on a population of two - so the three evidence gaps Stage 2 must address
stand exactly as the anatomy read left them.

### The SEO contract (2026-09-12)

From this round on, every governed page carries a presentation contract in its
own data: primary query, secondary entities, title, description, canonical, H1,
schema types, incoming and outgoing governed links, and indexing status. It is
enforced in two layers - shape from one file in `validate_content`, and
route-level facts in `seo_gate.py`, which reads the built output rather than the
data so it cannot agree with a stale assumption. Awards are the first cluster
under the contract.

The rule this imposes on the project is the same one the evidence layers already
follow: **presentation may not claim more than the page contains.** A title must
name the entity it is about, structured data must match what is on the page (no
FAQ schema without an FAQ), a canonical must match the route, no page may be an
orphan, and no two pages may compete on one title. Nothing in the contract may
change what an entry claims.

### The SEO architecture audit (2026-09-12)

Run once across the whole site, after the Wolf anatomy and before Stage 2, and
changing presentation only. The contract moved from `awards` to all five data
clusters and to the 16 generated routes; every one of the 63 built routes is now
governed, and an ungoverned route fails the gate. Full account:
[`seo-architecture-audit.md`](seo-architecture-audit.md).

Its two structural outputs:

**`/sectors/mathematics-computing` is published**, as an open reference rather
than a finished one. The domain under active work had no page from which anything
could reach its five cases, its three systems or its three award anatomies. The
page states its own maturity as measured - `open cycle`, `DDI cases 5/10 not yet`
- because a reference does not need to be finished to be useful; it needs to not
claim to be finished.

**The reasoning graph and the rendered graph were not the same graph.** Checking
declared links against the built HTML rather than against other declarations found
90 links the project assumed existed and the site never rendered - person to
mechanism, concept to the cases evidencing it, award anatomy to its own
recognition-system entry in both directions. They are now built from the data with
descriptive anchors.

The audit also surfaced a cannibalisation the ontology had built in: an award has
two pages here, the anatomy answering how it is built and the system entry
answering how legitimate it is, and both were targeting the award's name. Resolved
by differentiating intent, not by merging pages.

One rule is recorded as house discipline and explicitly not as anyone else's:
the title and description length bounds are ChampionsAwards presentation
discipline, **not** a claimed search-engine requirement. The project does not turn
a heuristic into a fact in its presentation layer any more than in its evidence
layer.

### Stage 2 - the pause at 8 (2026-09-12)

Three cases, chosen as types against the three evidence gaps rather than as
names: a lower-DDI mathematics test, a lower-DDI computing test, and an
under-recognition test that does not start from institutional exclusion.

| Case | Subfield | DDI | Obs | Gap | Mechanism |
| --- | --- | --- | --- | --- | --- |
| Yitang Zhang | mathematics | 77 | 80 | -3 | none |
| Jean Sammet | computing | 77 | 84 | -7 | none |
| Tommy Flowers | computing | 83 | 56 | **27** | **none - ontology boundary** |

Baseline at the pause - **DDI range 77-86 (spread 1 to 9)**; gap -8 to 27, median
1.5; 5 aligned, 2 under-recognised, 1 significantly under-recognised; mathematics
3 cases / computing 5; mechanism accounting 8/8; **unexplained under-recognition
1** (was 0); ontology coverage still **1 of 6**; award relations **4, unchanged**.
Full account: [`cycle-03-stage2-read.md`](cycle-03-stage2-read.md).

Three results worth carrying. The two lowest-assessed cases in the domain are both
in the aligned band, so **a lower assessed index does not bring lower recognition**
- the first time this corpus could show the two sides of the instrument moving
independently. Three new cases produced **no new mechanism**, leaving one evidenced
across eight cases. And Flowers stands on a boundary the ontology does not cover:
his contribution was withheld from the record by statutory secrecy, which is
neither a barrier to a position, nor a community unable to absorb the work, nor a
person exercising discretionary obstruction. **No concept was created for it** - a
mechanism invented to fit the case that motivated it is a taxonomy built backwards
from a result, which is the error removed from the Definition of Done in Cycle 01.

One rule was set for this stage and held: *a wider DDI range is an outcome to
observe, not a target to manufacture*. The range widened because two genuinely
narrower contributions scored lower on dimensions the record bounds - Zhang's
uniqueness taken from his own abstract naming the work it refines, Sammet's from
two institutional records stating her committee role rather than attributing COBOL
to a person. No relation was manufactured either: Zhang carries no Fields Medal
eligibility relation, because being over forty is not a documented interaction.

### Stage 3 - the full read at 10 (2026-09-12)

Two cases, each chosen to test a question Stage 2 produced rather than to fill a
row. Expansion is complete.

| Case | Subfield | Question | DDI | Obs | Gap | Result |
| --- | --- | --- | --- | --- | --- | --- |
| George Green | mathematics | does delayed recognition survive a case chosen for it? | 88 | 67 | 21 | **evidenced** |
| James H. Ellis | computing | is the Flowers boundary a one-off? | 78 | 44 | **34** | **it recurs** |

Green evidences **delayed recognition** - the first in this domain, the corpus's
second anywhere - and the fit is clause by clause: an 1828 essay sold by
subscription to fifty-one people, eighteen years of silence, rediscovery by a
third party five years after his death. Support 1 of 10, so **emergent, not
established**; the threshold was not bent for the mechanism the round was designed
around.

Ellis reproduces the Flowers boundary exactly, in a different decade and
technology, and **no concept was created for it**. Both cases arise inside one
national cryptographic apparatus, so a shape recurring within a single secrecy
regime may describe that regime rather than a mechanism of recognition; two
occurrences are therefore not counted as a pattern. Credit misattribution was
tested hardest here, because the field's highest award for public-key cryptography
is held by others, and is still refused - independent arrival by another route is
not displacement.

At the pause: DDI 77-88 (spread 11); gap -8 to 34, median 8; 5 aligned, 3
under-recognised, 2 significantly under-recognised; mathematics 4 / computing 6;
cross-cutting still **0/0/0** across a completed corpus; mechanism accounting
10/10; **ontology coverage 2 of 6**; unexplained under-recognition **2 of 5**,
from 0 of 2 at n=5. Award relations 4, unchanged since n=5. Full account:
[`cycle-03-stage3-read.md`](cycle-03-stage3-read.md).

Every Definition-of-Done criterion is now met except synthesis.

Read against the closed domains, this one aligns where they do not - 5 aligned
cases against 0 in physics and 2 in biology, and a median gap of 8 against 26.5
and 24.5 - and it produces fewer mechanisms per deficit than either: physics
explains 9 of its 10 deficits, biology 5 of 8, this domain 3 of 5. Its two
unexplained cases are not short of evidence; every fact in both is documented by
the state agency that imposed the secrecy. They are short of a concept.

### Ontology review over the completed corpus (2026-09-12)

The answer to Stage 3's question is **both, and they are separate questions**:
compulsory secrecy is a mechanism, and it is not yet independently replicated. The
review's first job was to make the instrument able to say both at once.

**The governance defect, fixed first.** `PATTERN_ESTABLISHED_MIN` was documented as
requiring independent cases and implemented as counting cases. That held while
every case carrying a pattern arose in a different institution, era and country.
Flowers and Ellis broke it - two cases, one national cryptographic apparatus - and
nothing in the code could have noticed. A case may now declare, per pattern, the
`pattern_context` its instance belongs to; a case declaring none **is its own
context**, so **no existing result moved**. Both figures are published, and only
**independent-context support decides lifecycle status**; an instance set that
collapses to one context is flagged regime-bounded. An unknown context fails
validation rather than silently creating false independence.

**The new mechanism.** `compulsory-secrecy`, audit-eligible, with five tests all of
which must hold, and distinguished by design from its three nearest neighbours -
exclusion needs a barrier to a position, delayed recognition needs a community
unready to absorb, gatekeeping needs a person exercising discretion. The name was
chosen over *state secrecy* and *statutory secrecy*, both too narrow, because it
names the causal structure rather than the apparatus that exposed it.

**Reclassification without rescoring.** Flowers and Ellis now carry the mechanism,
both in the `uk-government-cryptographic-secrecy` context. No score moved. Their
`mechanism-boundary` exceptions are kept and marked resolved rather than deleted:
the sequence - boundary recorded, boundary reproduced, then concept added - is the
thing that makes the addition defensible.

After the review: deficits still 5, deficits explained **3 to 5**, unexplained
under-recognition **2 of 5 to 0 of 5**, ontology **6 to 7** mechanisms, evidenced
in this domain **2 of 6 to 3 of 7**, compulsory secrecy emergent at 2 cases and 1
context. DDI range, gaps, aligned cases and award relations all unchanged. Full
account: [`cycle-03-ontology-review.md`](cycle-03-ontology-review.md).

**Three outcome classes, not four.** A fourth class for regime-bounded mechanisms
was considered and rejected: it would mix what happened to a case with how broadly
a mechanism has been replicated, and keeping those apart is what the recurrence
model exists to enforce. Regime-boundedness belongs to mechanism maturity.

Stage 3's provisional headline - that this domain produces gaps the ontology
cannot explain - is **withdrawn**. Every deficit is now explained, and the domain's
contribution is methodological:

> A completed corpus forced the ontology to distinguish recurrence from
> independent replication.

Physics forced the project to stop using mechanism counts as maturity gates.
Biology forced it to distinguish aligned cases from unexplained deficits.
Mathematics & Computing forced it to distinguish two observations from two
independent contexts.

### Synthesis (2026-09-12)

[*Two Observations, One Context: Recognition Outcomes in Mathematics & Computing*](https://championsawards.com/reports/recurrence-and-replication-mathematics-computing)
derives from the completed corpus at snapshot `fb8f6090f4e8`. Its question is the
one the ontology review answered and the corpus is the first to have posed:

> When the same mechanism appears in two cases drawn from one institution, one
> legal regime and one apparatus, has a pattern recurred - or has one regime been
> observed twice?

Nine observations, every figure resolved from the engine at build time and no
number typed by an author. Three hypotheses, each with its refutation condition -
that compulsory secrecy is a regime signature rather than a general mechanism,
that this domain's high alignment rate is a property of the selection rather than
of the field, and that the Deservingness Index discriminates less sharply on merit
than on recognition in every domain. One dated correction, withdrawing the
provisional Stage 3 headline. Six limits, including that the mechanism column is
younger than two of the cases it describes.

The sharpest figure in it is a pair: institutional exclusion and compulsory
secrecy carry the same case count and hold different lifecycle status, because
one's instances stand in separate contexts and the other's do not. Identical
support, different status, is what the distinction between recurrence and
replication looks like once it is measured rather than argued.

### Closure

> **Mathematics & Computing Recognition Layer — mature v1.0**
> Closed at corpus snapshot `fb8f6090f4e8` · data through 2026-09-12 · governed by DoD v1.1

Every criterion measured and met (`python scripts/domain_status.py`):

| Criterion | Measured |
| --- | --- |
| DDI cases ≥ 10 | 10 |
| RLS systems ≥ 3 | 3 |
| Mechanism accounting = 100 % | 10/10 |
| Cases unaudited = 0 | 0 |
| Source-grade closure | 13/13 entries closed |
| Award anatomy | Turing Award, Fields Medal and Wolf Prize mapped |
| Synthesis | *Two Observations, One Context: Recognition Outcomes in Mathematics & Computing* |

Reported, and required by nothing:

| Observation | Value |
| --- | --- |
| Evidenced mechanisms | 3 of 7 audit-eligible concepts |
| Established mechanisms | 1 — institutional exclusion (2 cases, 2 contexts) |
| Emergent mechanisms | 2 — delayed recognition (1 case); compulsory secrecy (**2 cases, 1 context — regime-bounded**) |
| Cases with a recognition deficit | 5 of 10 |
| Deficits with an evidenced mechanism | 5 of 5 |
| Unexplained under-recognition | 0 of 5 |
| Recognition aligned, no deficit to explain | 5 of 10 |
| Subfield coverage | mathematics 4c / computing 6c / **cross-cutting 0c 0s 0a** |

The cross-cutting compartment stays in the vocabulary. It is not deleted because
it is empty and it is not filled because it is available: the synthesis uses it
honestly to describe a report spanning both halves, while coverage counts only
cases, systems and awards. **The zero is a result.**

### What this cycle added to the project

Closure is not the arrival of a tenth person. Six things entered the project here
that were not in it before, each because the corpus forced them rather than
because a plan scheduled them:

1. **Composite-domain accounting.** A domain whose name joins two recognition
   cultures can no longer hide an empty half. `subfield_coverage` measures it,
   publishes it, and gates nothing.
2. **Recognition architecture became comparative.** Three anatomies in one domain
   showed that systems sharing a field can differ radically in nomination, funding,
   transparency and governance — open nomination and committees published since
   1936 at the Fields Medal, invitation-only with fifty-year seals at the Nobel,
   neither readable at the Turing Award.
3. **Cross-domain award accounting.** A relation is counted in the domain of the
   *case* it names, never of the award that carries it.
4. **Recurrence is not replication.** Two cases inside one regime do not become an
   established mechanism. Support and independent support are separate published
   figures, and only the second decides lifecycle status.
5. **Compulsory secrecy.** The ontology grew because the corpus produced two
   documented deficits no concept described — not because a maturity gate asked
   for another mechanism. The gate had already been removed in Cycle 01 for
   exactly that reason.
6. **SEO became governed architecture.** The reasoning graph and the rendered
   graph are one structure, checked against the built artefact, rather than a
   presentation layer applied afterwards.

> **Mathematics & Computing did not mature by producing more mechanisms. It
> matured by learning when two observations are still only one context.**

Production verification in Search Console - submit the sitemap, inspect one URL
per template family, confirm the Google-selected canonical and the structured-data
parsing match what the build declares - runs in parallel and blocks nothing.
