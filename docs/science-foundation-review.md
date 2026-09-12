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
