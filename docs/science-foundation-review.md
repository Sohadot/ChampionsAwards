# Science Foundation Review v1.0 — 2026-09-12

One pass over the whole repository after Cycle 03 closed, asking a single question:

> If ChampionsAwards were built today from scratch using everything learned across
> Cycles 01–03, do the three closed scientific layers still satisfy the current
> architecture without hidden legacy assumptions?

No case, system or concept was added. No score was changed. No cycle was opened.
Physics & Astronomy and Biology & Medicine were **not reopened as inquiries** — the
review asks only whether what they publish is still true under the current rules.

**Outcome: not clean.** Three defects were found and fixed as wording corrections,
and **two material findings remain open for a decision.** `Scientific Recognition
Foundation — stable v1.0` is therefore **not declared.**

---

## What came back clean

| Check | Result |
| --- | --- |
| Award relations counted in the domain of the **case**, not the award | 18 declared, 18 counted, **0 misattributed** |
| Cross-domain anatomy splits correctly | Wolf Prize serves 3 domains; its 2 relations land in mathematics and physics respectively |
| Sector hubs carry the recurrence columns | 3 of 3 |
| SEO contracts | every built route governed; gate passes |
| Figure tokens in closed-layer reports | ontology denominator moved 6 → 7 and **both closed reports updated themselves**; no stale number |
| "The Unawarded Archive" in published output | 0 occurrences |
| Superseded DoD language (`patterns ≥ 4`) outside the superseded record | 0 occurrences |
| Recurrence model applied without moving old results | every pre-Cycle-03 pattern keeps its status |

The token discipline is worth singling out. When the ontology grew from six
concepts to seven, two reports written in earlier cycles re-rendered with the new
denominator without anyone touching them. That is the rule "a report may not type
a statistic" paying for itself two cycles after it was imposed.

## Defects found and fixed (wording only, no finding changed)

**1. Two documents typed a moving figure.** Both closed cycles recorded a "current
snapshot" hash in prose. Both had drifted — the Wolf Prize track-record correction
of 2026-09-12 changed the RLS inputs of all three domains, and neither line was
updated. The fix is not to correct the hashes but to **stop copying them**: the
closure snapshot stays, because it is a historical fact, and the moving figure is
now read from `domain_status.py`. A machine check refuses any document that types
one again.

**2. The Physics report stated the establishment threshold in the wrong unit.** It
read "the established threshold of `{pattern_min}` independent evidenced cases".
Since the recurrence model it is independent **contexts**. The sentence described
a rule the project no longer runs, on a published page.

**3. Two case entries still denied carrying a mechanism.** Flowers and Ellis were
reclassified in the ontology review, but their `structural_reason` fields still
read "recorded as that rather than as one of this corpus's mechanisms", and the
Ellis introduction still described "this project's six mechanisms". The analysis,
the audit and the tags had been updated; these three sentences had not. They are
now stated as the sequence actually ran — constraint recorded outside the
vocabulary, concept added later, case reclassified with no score changed.

All three are the same species of defect: **prose that was true when written and
became false when the architecture moved.** None of them was reachable by any
existing check, which is why two of the three fixes are accompanied by one.

---

## Open finding 1 — 20 of 22 audits predate the ontology they are measured against

**This is the review's material result.**

`compulsory-secrecy` was added on 2026-09-12. Every case audited before that date
was tested against a smaller ontology, and nothing in the gate notices, because
`mechanism_audit.considered` is checked for *ineligible* entries and never for
*completeness*.

| Missing from `considered` | Cases |
| --- | --- |
| `compulsory-secrecy` | 20 of 22 |
| `theory-experiment-asymmetry` | all 10 Biology & Medicine cases |
| `posthumous-recognition` | 2 Physics & Astronomy cases |

**Audits current against the 7-concept ontology: 2 of 22.** The figure is now
computed and printed by the check suite, so the corpus cannot hide it.

What this does and does not mean. It does **not** mean any finding is wrong: none
of the twenty cases involves a classification regime, and the two concepts missing
from the older audits are unlikely to change a single result. It **does** mean the
published claim "mechanism accounting 100 %" rests on audits run against different
vocabularies, and the site does not say so.

**Why nothing was back-filled.** Appending `compulsory-secrecy` to twenty
`considered` lists would take about a minute and would be **fabricating dated
evidence**. A name in that list asserts that the mechanism was tested against that
record on that date. Writing it without running the test is the one thing this
project has refused at every stage.

Three options, and the choice is a governance decision rather than a technical one:

- **(a) Re-audit.** Run the missing concepts against the twenty cases and date the
  result. Honest, and it reopens closed layers for work you said not to do
  unilaterally.
- **(b) Date the ontology instead.** Record on each audit which ontology version it
  ran against, and publish currency as an observation — reported, never gated, like
  every other observation in DoD v1.1.
- **(c) Accept and state it.** Leave the audits as dated historical facts and say so
  wherever mechanism accounting is published.

The review recommends **(b)**, because it makes the drift permanently visible
without either fabricating evidence or reopening a closed inquiry — and because a
fourth domain will create the same drift again the first time the ontology grows.

## Open finding 2 — an award entry outside the domain model

`nobel-peace-prize` declares no domain at all. It is published, it is governed by
an SEO contract, and it is invisible to every domain's award layer because it
belongs to none of the three scientific domains. That is not a defect in the
domain model; it is a published entry the model does not reach. Cycle 04 —
Literature will make the same question live for a second entry, so it is better
settled before that cycle than during it.

## Examined and deliberately not acted on

**Shared recurrence contexts in the closed layers.** The recurrence model is only
meaningful if it was applied to the old layers too, so every multi-case pattern was
re-examined for instances sharing an institution or regime. One candidate exists:
Cecilia Payne-Gaposchkin and Henrietta Swan Leavitt both carry institutional
exclusion and both worked at the same observatory. It is **not** declared a shared
context, for a reason internal to the evidence: the GCHQ cases share an imposing
institution, a legal instrument and a disclosure practice, all three named in the
record, while these two entries evidence a field-wide norm — one says "her
observatory", the other "the limited roles available to women in early
twentieth-century astronomy". Declaring them one context would assert a shared
regime that neither entry documents.

Had it been declared, physics institutional exclusion would read 4 cases / 3
contexts and physics credit misattribution 8 / 7 — **no lifecycle status would
change**. The candidate is recorded here so the judgment is visible and reversible
rather than silent.

## Why stable v1.0 is not declared

The review found real drift, fixed what could be fixed without touching evidence,
and surfaced one finding that needs a decision before the foundation can be called
stable. Declaring stability over a known open finding would be the same error as
counting two observations as two replications: a label asserting more than the
record supports.

The three domains remain **MATURE v1.0** individually — that status is measured per
domain by the Definition of Done and is unaffected. What is withheld is the
cross-cutting claim that the foundation as a whole needs no further work.

## Not blocking, unchanged

Search Console verification remains an external parallel track: submit the sitemap,
inspect one URL per template family, confirm the Google-selected canonical and the
structured-data parsing match what the build declares. Nothing in this review waits
on it, and nothing in it depends on the outcome.

---

# Second pass — 2026-09-12, after the revision model and the domain registry

Both open findings were closed by construction, and the re-run then measured what
those constructions exposed. **The review is still not clean, and
`Scientific Recognition Foundation — stable v1.0` is still not declared** — but
for a different and sharper reason than the first pass.

## Finding 1 closed by construction, and the measurement was worse than expected

Option **(b)** was implemented: every audit now records the ontology revision it
ran under (`ontology_revision`) and the evidence for it (`revision_basis`), ids
are immutable and ordered by commit, and the gate enforces that an audit tests
everything eligible at its revision or declares exactly what it did not.

All 22 revisions were recovered from history by ancestry, not guessed, so the
sentinel `legacy-revision-unresolved` was not needed. Nothing was added to any
`considered` list.

Separating the two figures produced a result the first pass had not anticipated,
and it is the reason this pass is not clean:

| | measured |
| --- | --- |
| Audits complete at their own recorded revision | **10 of 22** |
| Audits current against the revision in force | **2 of 22** |

The second figure was expected. The first was not: the assumption going in was
that audits had been complete when performed and had merely aged. They had not.
Twelve audits failed to test a mechanism that was **already audit-eligible on the
day they ran** — ten Biology & Medicine audits omit `theory-experiment-asymmetry`
(eligible since MOR-002, two revisions before those audits), and the two Physics
& Astronomy audits omit `posthumous-recognition` (eligible since MOR-001, the
first revision of all). The assignment is robust to the one judgment call it
required: MOR-003 and MOR-004 carry the same mechanism set, so reading those
audits as MOR-003 audits performed before the concept-type change or as MOR-004
audits pruned by it gives the identical gap.

This is not ageing. It is a defect that existed at the time and that no check
could see, because completeness was never measured against anything. Each of the
twelve now declares its own gap in `incomplete_at_revision`.

## The consequence that needs a decision

The twelve gaps are not equal in weight, and two of them touch results the corpus
publishes.

**`posthumous-recognition` is evidenced in zero cases across the whole corpus.**
It was tested in 20 of 22 and found in none. The two cases where it was never
tested are Satyendra Nath Bose and **Vera Rubin** — and Rubin is, on the face of
the record, the corpus's strongest posthumous-recognition candidate: a
contribution of established magnitude, an award never made, and a death that
under the Nobel statutes forecloses one permanently. The corpus therefore
publishes "this mechanism is evidenced nowhere" while never having tested it on
the case most likely to carry it.

**`theory-experiment-asymmetry` was never tested in Biology & Medicine at all.**
Ten audits, none considering it. **Rosalind Franklin** is the obvious candidate —
an experimentalist whose data underwrote a model-building result that was the one
recognised — and the biology layer's published mechanism coverage rests on a set
of audits that never asked.

Neither is a clerical matter and neither is fixable by editing a file. Testing a
mechanism against a case is an evidential act: it means returning to the sources,
applying the concept's conditions, and dating the result. That is a re-audit of
two entries in closed layers, and it is the decision this pass hands back.

What it is **not**: a finding that any published score is wrong. No DDI, no
observed recognition and no gap depends on it. What would move is a mechanism
tag, the domain's evidenced-mechanism count, and — if `posthumous-recognition`
were evidenced — a concept that currently has no support anywhere in the corpus.

## Finding 2 closed

`DOMAIN_REGISTRY` separates a domain's lifecycle (`planned` / `open` / `closed`)
from cycle state, and aggregation is derived from it. Literature and Peace are
registered as planned; the Nobel Peace Prize is scoped to `peace` and is
otherwise untouched — no DDI, no RLS, no mapped architecture. The gate now
rejects any published entry in a domain-scoped cluster that names no registered
domain, with concepts exempt by a posture declared in config rather than by a
validator's omission.

Building it surfaced a smaller defect of the same species: the maturity report
iterated every registered domain, so a planned domain produced a row of zeroes
and a Definition of Done reading "pending" — a domain nobody has started,
rendered as a domain that is failing. Planned domains are now listed and not
computed.

## Corrections made in this pass

Three, all the same species as the first pass — prose that was true when written:

1. `docs/DOMAIN-CYCLES.md` still defined emergent and established in **cases**.
   That is the canonical model document, and the first pass corrected the
   derivative statements while leaving the definition itself standing.
2. The sector pages described emergent patterns as "recorded in a single case
   each" — false of compulsory secrecy, which is recorded in two cases sharing
   one context. Each emergent pattern now reports both counts.
3. The Physics report carried the same phrase as a trailing clause. It now says
   the emergent patterns fall below the threshold, which is true at any
   threshold and claims nothing the tokens do not carry.

## Why stable v1.0 is still not declared

The first pass withheld the label over a finding that turned out to be the
smaller half of the problem. Currency was the visible drift; completeness was the
real one, and it was invisible until the two were separated. Two named cases now
sit between the corpus and a claim it makes about itself.

The three domains remain **MATURE v1.0** individually. Maturity is measured per
domain by the Definition of Done, and neither figure gates it — deliberately, so
that a growing vocabulary can never retroactively unmake a closed layer. What
stays withheld is the cross-cutting claim that the foundation as a whole needs no
further work.

---

# Third pass — 2026-09-12, after the twelve re-audits

**The review is clean, and `Scientific Recognition Foundation — stable v1.0` is
declared.**

## What was checked

The pass re-ran the same question over the whole repository: do the three closed
layers still satisfy the current architecture without hidden legacy assumptions —
now including the architecture the previous two passes added.

| | result |
| --- | --- |
| The twelve historical audit defects | remediated, 12 of 12, by dated re-audit |
| Original audits preserved, defects still visible | yes — `incomplete_at_revision` untouched on all twelve |
| Re-audits complete against the current ontology | yes — all seven mechanisms, one verdict each, gate-enforced |
| Domain registry | sound: states valid, aggregation derived, planned domains produce no hub and enter no maturity report, no published entry unscoped |
| Reports and sector pages | recompute from the engine; no figure is typed |
| Stale prose | two found and fixed (below) |
| New material defect | none |

## The two defects this pass found, and fixed

Both were introduced by the remediation itself, which is the reason a third pass
had to happen rather than being assumed.

**Three added sources were left unanchored.** Testing posthumous recognition
against Bose, Rubin and Avery required the Nobel Foundation's own record of when
the posthumous prohibition entered the Statutes, so that source was added to
those three entries — and then the re-audits' `best_sources` did not cite it, in
one case because the index was guessed before the append rather than read after
it. A claim resting on a source the entry does not point to is exactly the
species of silence this project exists to remove. Fixed, and a sweep confirms the
rule holds corpus-wide: every source in all thirty case entries is now referenced
by a fact, a score, a pattern, an audit or a provenance anchor. None is orphaned.

**Twelve entries carried a `last_reviewed` older than their own review.** A
re-audit is a dated evidential act on the entry, so leaving the field at
2026-09-10 or 2026-09-11 understated when the entry was last examined and held
the corpus date back with it. Advanced to 2026-09-12 on all twelve. The live
`data_through` for Physics & Astronomy and Biology & Medicine moves with it,
which is correct and is not a conflict with their closure declarations: a
declaration names the corpus at closure, and correctable work on a closed layer
advances the live corpus without reopening the cycle. That distinction is now
written into the closure-format section of `DOMAIN-CYCLES.md`, because it will
recur every time a closed layer is corrected.

## What the remediation did not change

No pattern was added or withdrawn in any of the twelve, and no DDI,
observed-recognition or gap value moved. Every established and emergent count,
every band, every explanatory-coverage figure and every synthesis token is
unchanged. Twelve complete tests returning the same answer as twelve partial ones
is a real result: it says the defect was in the record of the search, not in the
findings the corpus published from it.

## Recorded for a future ontology review, not acted on

`posthumous-recognition`, read literally, is satisfied by every scientist who has
died since the Nobel Statutes acquired the posthumous prohibition in 1974 — a
tag that fits every deceased case distinguishes nothing. The corpus's working
practice has always been the narrower reading, in which an eligibility rule must
be shown to have determined an actual decision, and the Franklin withdrawal, the
Ball non-tag and now the Bose and Rubin verdicts all apply it. The concept's own
text does not yet say so. That is a question for an ontology review, and this
remediation deliberately closed known defects without reopening the ontology.

Also recorded, and also not a defect: mechanism audits and re-audits are data and
enter the published figures, but no case page renders an individual audit. That
has been true since audits were introduced and is not a consequence of this work.
Whether the audit trail should be readable per entry is a question for a future
cycle.

## Why stable v1.0 is declared

Stability is not the claim that every historical audit has been re-run after
every growth of the ontology. Eight audits remain non-current — the Mathematics &
Computing audits that were complete at MOR-004 and predate compulsory secrecy —
and re-running them would be work without a defect to justify it.

Stability is the claim that every **known** defect is honestly closed, and that
the system can say precisely which of its knowledge is historical, which is
current, and which was later corrected. Three figures carry that, and the corpus
keeps them apart rather than collapsing them into a flattering one:

| | measured |
| --- | --- |
| Complete when originally performed | **10 of 22** — and it will never move |
| Historical audit defects remediated | **12 of 12** |
| Latest audit statement current against MOR-006 | **14 of 22** |

The first number is the one that matters most, and it is the one a less careful
project would have deleted. Ten of twenty-two audits were complete when they ran;
that is now a permanent part of the record, sitting beside the fact that all
twelve failures were later repaired. A corpus that could only say "22 of 22
complete" would know less about itself than this one does.

## Not blocking, unchanged

Search Console verification remains an external parallel track. Nothing in any of
the three passes waits on it.

---

# Post-stability correction — 2026-09-13

Stability is not a freeze, and this is the first correction made under it. It is
recorded here rather than as a fourth pass, because it is a presentation defect
rather than a finding or an architectural fault, and it does not reopen
`Scientific Recognition Foundation — stable v1.0`.

## What was wrong

The `posthumous-recognition` concept page carried the title *"Definition &
Documented Cases"* while the corpus evidences the mechanism in no case at all —
a claim the 2026-09-12 re-audits had just made false in the most explicit way
possible, by testing it against every governed case and finding it nowhere. The
page also linked to no case, so the title advertised what the page itself could
not show.

Checking the rest of the cluster showed the defect was wider than the one page.
*"Definition & Documented Cases"* was boilerplate on **all nine** concept pages,
and three of them could not support it:

| concept | type | evidenced cases |
| --- | --- | --- |
| `posthumous-recognition` | mechanism | 0 — tested everywhere, found nowhere |
| `merit-vs-recognition` | framework-concept | 0 — and no case can ever carry it |
| `recognition-bias` | recognition-pattern | 0 — and no case can ever carry it |

The last two are a category error rather than a count problem: only a
`mechanism` can be evidenced by a case, so those pages advertised a kind of
evidence their own concept type forbids.

## What was done

The three titles are corrected. More importantly, the claim is now **measured
rather than asserted**. Every concept page renders a corpus-support line built
from the engine at build time:

> Current corpus support: 0 evidenced cases. The mechanism is defined and
> audit-eligible, and every governed case has been tested against it, but none in
> this corpus evidences it.

against, for an evidenced one:

> Current corpus support: 11 evidenced cases across 11 independent contexts, in
> Biology & Medicine and Physics & Astronomy … this one is established.

and, for a concept no case can carry:

> Current corpus support: not applicable. This is a recognition pattern rather
> than a mechanism, so no case can be tagged with it.

And the gate now refuses the claim itself. A concept whose title or description
asserts documented cases fails validation unless the engine counts at least one.
The check reads the engine, not a maintained list, so removing the last case
evidencing a concept breaks the build on the page that still advertises cases.
The boilerplate cannot outlive the evidence a second time.

## Why this was not caught by the third pass

The third pass swept prose for claims falsified by the remediation and checked
every figure against the engine. It did not treat **SEO fields as claims about
the record** — they were governed for length, uniqueness, entity coverage and
link resolution, but never for truth. That was the blind spot, and closing it is
what makes this a correction rather than a recurrence.

## Still reserved, still not acted on

The operational boundary of `posthumous-recognition` — whether the mechanism
means that death forecloses a future award, or requires an eligibility rule shown
to have constrained a relevant recognition opportunity — is now the first
question in the Cycle 04 preflight, in `DOMAIN-CYCLES.md`. Every audit in the
corpus already applies the narrower reading; the concept's text does not yet say
so, and Literature runs under the same Statutes that make the question live.
