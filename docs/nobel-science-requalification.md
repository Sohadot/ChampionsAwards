# Nobel science RLS — requalification

*2026-09-13. A post-stability correction, not a reopening of Cycles 01 or 02. No
case, no concept and no DDI score is touched; the Physics and Physiology or
Medicine award anatomies are unchanged.*

## Why

The Literature system was the first RLS in this project built evidence-matrix
first, score second. Placing it in the same table as the legacy `nobel-prize-system`
entry would have compared two figures produced to different standards. That entry
scored all five dimensions from the Foundation's Statutes and Nobel's will alone,
and asserted two analytical conclusions with no dataset behind either:
*"historically concentrated in Western Europe and North America"* and *"most
scientific selections have proven durable"*. It also covered two categories
decided by different bodies under one rationale.

The rule for the round was: **do not preserve the old score, preserve only the
claims the evidence survives.**

## Stage 1 — scope viability

Physics and Physiology or Medicine were researched separately, from each deciding
body's own record, before any question of a shared score was asked.

| | Physics | Physiology or Medicine |
| --- | --- | --- |
| deciding body | Royal Swedish Academy of Sciences — founded 1739, ~480 Swedish + 175 foreign members in ten disciplinary classes | Nobel Assembly at Karolinska Institutet — 50 professors of one university, membership conditional on remaining on its faculty |
| filtering body | Nobel Committee (5 voting + voting adjunct members) → **Physics Class**, which may substitute a different proposal → final Academy meeting | Nobel Committee (5 + Secretary), **elected by the Assembly from among itself** |
| decision rule | **none published** | **majority vote, first Monday in October, final and without appeal** |
| nominator population | all Academy members; Nordic chairholders in the physical sciences; chairholders at universities selected annually for country distribution | Assembly members; the Medicine and Biology classes of the RSAS; **all** Swedish and Nordic medical full professors; **no fewer than six** other faculties worldwide |
| archive horizon | 1901–**1974** (3,843 nominations) | 1901–**1953** |
| breadth record | 229 laureates: 88% Europe/N. America, 2% women | 232 laureates: 88% Europe/N. America, 6% women |
| track record | no durability analysis exists | no durability analysis exists |

**Verdict: split.** Two dimensions differ materially — *process* (three filtering
stages with an overriding disciplinary class and no published decision rule,
versus a two-stage chain with a published majority rule) and *transparency* (a
21-year difference in what the historical archive actually delivers). Two are
materially shared: *breadth*, where the outcome records are within two points on
geography, and *independence*, where both sit under the same endowment with no
appeal. *Track record* is shared only in the sense that neither has an analysis.

Under the standing rule that a material difference on more than one dimension
splits a system, one difference would not have been enough. Two are.

## Stage 2 — the requalified scores

| dimension | old shared | Physics | Medicine |
| --- | --- | --- | --- |
| process | 72 | **74** | **72** |
| breadth | 58 | **48** | **50** |
| track record | 80 | **62** | **62** |
| transparency | 55 | **56** | **52** |
| independence | 78 | **78** | **70** |
| **composite** | **69** | **64** | **62** |

What moved and why:

- **Breadth fell ten points in physics and eight in medicine**, and is now
  measured rather than asserted. The old sentence was true in direction and
  understated in degree: 88 per cent of laureates in both categories were born in
  Europe or North America, and physics has awarded 5 women in 229 laureates.
- **Track record fell eighteen points in both.** The sentence that justified 80
  is withdrawn, not rephrased. No durability analysis exists for either, and both
  now carry the same conservative figure — which reflects an identical *evidence
  situation*, not a finding that the two records are equally durable.
- **Independence diverged.** Physics keeps 78, now justified by a 1739
  multidisciplinary academy of roughly 655 members rather than by an endowment
  insulating "most categories". Medicine falls to 70 because its deciding body is
  constituted entirely from one university's professoriate.
- **Process rose slightly in physics** — the published filter chain is stronger
  than the old entry recorded — and is held below what that chain would earn
  because no decision rule is published anywhere.
- **Transparency diverged** on archive delivery, which is the half of the
  dimension the old entry never separated from published procedure.

## The architecture rule this forced

Preflight 3 recorded that *"an RLS scores a deciding body, not a foundation"*.
That was right about the Foundation and too tight about the rest — it did not sit
with a single entry covering two deciding bodies. The rule is now:

> An RLS scores a **governed decision architecture**. Several deciding bodies may
> share one RLS only where the evidence shows that all five scored dimensions are
> materially shared.

Enforced: a system whose scope covers more than one domain must declare
`shared_architecture` with a justification for every RLS dimension, or fail the
gate. One deciding body assessed across several domains is unaffected.

## Consequential corrections

- The Nobel Peace Prize entry was paired to the science system and linked to it.
  That was the same conflation, and the pairing is removed — an RLS scored over
  physics and medicine was never evidence about the Norwegian Nobel Committee.
- Recognition-system slugs now carry a `-system` suffix wherever an award anatomy
  of the same name exists or will, so the Literature system moved to
  `nobel-prize-in-literature-system` before its anatomy claims the plain name.
  The old URL was one commit old and linked from nowhere outside the corpus.

## What did not change

No DDI score, no case, no pattern, no concept. The Physics and Physiology or
Medicine award anatomies are untouched — no factual error was found in either.
Both domains remain **MATURE v1.0**: the Definition of Done counts systems and
closure, not scores, so a requalification that lowers a composite by five points
does not disturb maturity. Closure snapshots in the cycle records stay as they
were; the live corpus snapshot moves, as it does after any correction.

---

# Gate correction and the Wolf portability check — 2026-09-13

The rule this document derived was bypassable for a day, and the entry that
bypassed it was the oldest one capable of doing so.

## The loophole

`validate_assessment_scope()` returned early when no `assessment_scope` was
declared. So the escape from a requirement about multi-domain scores was to
declare nothing at all — and the Wolf Prize, covering physics, biology-medicine
and mathematics-computing with per-field juries, carried neither a scope nor a
`shared_architecture`. Four other systems were equally unscoped.

Every test written for the rule had tested a system that *had* declared a scope.
The absent test was the negative one, and it is now the first of its group:

> a scored multi-domain system with no scope at all must fail validation

**A published system carrying an `rls_assessment` must now declare an
`assessment_scope`.** All five previously unscoped systems were migrated.

## The Wolf portability check

Run before any score was touched, against the Foundation's own record.

| dimension | portable across physics, medicine, mathematics? |
| --- | --- |
| process | **Shared** — one field-agnostic published sentence is the Foundation's entire account of selection for every field |
| breadth | **Half shared, half unassessable** — see below |
| track record | **Shared** — full laureate record published for every field, no durability analysis for any |
| transparency | **Shared, and verified** — all 390 laureate pages examined: every one publishes field and year, 389 a citation, 332 an affiliation, and **not one page in any field** discloses jury membership or nomination records |
| independence | **Shared** — one 1975 family endowment, one Board, all roles voluntary |

The entry keeps its three domains, and now argues for them dimension by
dimension rather than inheriting them from a common name.

## What the check changed

**Breadth: 64 → 56.** A project analysis over all 390 laureate pages measured the
field-coverage half properly for the first time — nine fields, the five sciences
evenly distributed (Physics 72, Mathematics 68, Medicine 67, Chemistry 62,
Agriculture 61) and 60 in the arts. That is genuinely broad and supports a score.
The representation half cannot be assessed at all: the Foundation publishes no
eligibility rules and no nomination data, and affiliation is free text in which
58 of 390 laureates carry no country component, many name only an institution,
and the field label itself contains a spelling variant. The old 64 rested on
field coverage alone while the dimension's definition also covers geographies and
groups — it was silently averaging a half nobody had measured.

The attempt is recorded as a dated audit exception. It failed on the archive, not
on effort, and that distinction is the finding.

Composite: **71 → 69**, which moves the Wolf Prize from *Strong* to *Adequate*.

## Open finding, deliberately not acted on

The Wolf process score of 78 predates this round and rests on one published
sentence. The portability check confirmed that sentence is the Foundation's
*entire* published account of selection — no jury membership, no nomination
eligibility, no selection stages, no decision rule, for any of the nine fields,
verified across 390 pages. A score of 78 sits above systems whose full stage
calendar and decision rule are published, and nothing in this round established
that it should. Recorded as an exception and flagged for requalification rather
than adjusted inside a round scoped to the gate and the portability question.

## The general lesson

Writing a governance rule and testing a new case against it is not enough. The
oldest case capable of violating the rule has to be forced through it as well —
and the test that proves the rule bites is the negative one, the case that must
fail. Both of this round's findings came from asking what the rule does when
something is *missing*, rather than what it does when something is wrong.

---

# Wolf Prize RLS requalification — 2026-09-13

*Evidence first, scores last. All five dimensions re-examined against the current
standard, with no assumption that any existing figure should be preserved and no
target composite.*

## What the Foundation actually publishes

Researched from the Foundation's own pages and from its complete laureate record.

| question this dimension asks | what is published |
| --- | --- |
| who may nominate | **no classes of qualified nominator anywhere.** Nomination is by invitation only; the published route to being invited is to email the office with a name, title, affiliation and field |
| what constrains a nomination | individuals not institutions; no self-nomination; valid three years; a dated deadline |
| who filters | **nothing published** |
| who decides | "international judging committees, reappointed annually, comprising experts in their fields" — no membership, no size, no appointment rule, for any of the nine fields |
| by what rule | **nothing published** |
| any appeal or review | **nothing published** |
| who manages the money | investment committee of five, internal auditor and accountant, **all named** |

The last row is the finding that shaped two dimensions: the Foundation names who
manages the money and does not name who picks the winners.

## The scores

| dimension | was | now | why |
| --- | --- | --- | --- |
| process | 78 | **56** | One general sentence was the entire published account of selection. Publishing part of one of the five things this dimension is made of, and none of the other four, is a fact about visibility rather than evidence of robustness. Real published constraints — no self-nomination, individuals only, three-year validity, a deadline, annually reappointed juries — are counted, and they are what keeps it above the floor. |
| breadth | 56 | **56** | Re-examined and confirmed, not inherited. Field coverage is measured; representation across geographies and groups remains unassessable because affiliation is free text and no nomination data exists. |
| track record | 76 | **62** | The old score rested on a complete laureate list, four published fields per laureate, and continuous operation. Those measure record-keeping, not durability. No durability analysis exists for any field. Same conservative figure as the Nobel science systems, for the same reason. |
| transparency | 58 | **58** | Re-examined and confirmed. Verified across all 390 laureate pages: a fully published outcome layer, nothing upstream in any field. |
| independence | 76 | **66** | Funding independence is now documented rather than asserted — one 1975 family endowment, no commercial or state sponsor, named investment committee and auditor, voluntary service throughout. Decision independence cannot be verified at all: the Foundation appoints the juries that decide its prizes and publishes neither their membership nor its trustees, so no separation between funder and decider is checkable from outside. |

**Composite 69 → 59.** Still *Adequate*. Two dimensions were re-examined and kept,
three were lowered on evidence, and none was moved to protect a band.

`last_reviewed` advanced to 2026-09-13, which this round should have done when it
changed breadth on the same day and did not.

## A finding I had to withdraw before publishing it

The first pass over the laureate record appeared to show four calendar years —
1997, 2003, 2007, 2009 — with no Wolf laureate at all, which would have
contradicted the entry's claim of continuous operation. It was an artefact of my
own parser. Fifty-seven laureates carry two-year award labels (1994/5, 1996/7,
2002/3, 2006/7, 2008/9), and a regular expression taking the first four digits
had silently dropped every second year.

Corrected before anything was written to the corpus. The true picture is the
opposite of the phantom: **award activity in every calendar year from 1978 to
2025**, with each science field awarded in 38 to 41 of those 48 years — the prize
runs continuously while any single field rotates out roughly one year in six.
That rotation is itself an architectural fact the entry had never recorded.

The episode is worth the paragraph because the failure mode is the one this
project keeps finding: a measurement that looks like evidence, produced by a
method nobody checked. The parse was mine, not the Foundation's, and the only
reason it did not become a published claim is that it contradicted something the
entry already said — which is a weak safety net, not a strong one.

## Not revisited

No case, concept or DDI score. The three science domains remain **MATURE v1.0**;
medians move to 64, 62 and 69. The Definition of Done counts systems and closure,
not scores.
