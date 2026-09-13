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
