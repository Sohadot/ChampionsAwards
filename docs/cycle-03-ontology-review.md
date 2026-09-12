# Cycle 03 — Ontology review over the completed corpus

Date: 2026-09-12. Run after expansion closed at 10 and before any synthesis. No
DDI dimension, observed-recognition figure, source, or Definition-of-Done
criterion was changed. Two cases were reclassified because the vocabulary
changed, not because their evidence did.

Corpus after the review: mathematics-computing `fb8f6090f4e8`, data through
2026-09-12.

## The question the corpus put to the ontology

Two cases — Tommy Flowers and James H. Ellis — carried fully documented
recognition deficits that none of the six audit-eligible mechanisms described.
Stage 3 left the question open in exactly these terms: *is statutory secrecy a
mechanism this project has not named, or a property of one apparatus the corpus
happened to sample twice?*

The answer is **both, and they are separate questions.** It is a mechanism. It is
not yet independently replicated. The review's first job was to make the
instrument able to say both things at once, because until now it could not.

## 1. The governance defect, fixed first

`PATTERN_ESTABLISHED_MIN` was documented as requiring "independent cases" and
implemented as counting cases. That equivalence held while every case carrying a
pattern arose in a different institution, era and country — one case was one
context. Flowers and Ellis break it: two cases, one national cryptographic
apparatus. Tagging them would have promoted a regime's signature to an
established mechanism automatically, and nothing in the code could have noticed.

**The model now distinguishes case support from independent-context support.**

- A case may declare, per pattern, the `pattern_context` its instance belongs to,
  from a vocabulary in `config.py` (`RECURRENCE_CONTEXTS`).
- A case that declares none **is its own context** — which is what every entry
  written before this rule assumed, so **no existing result moved**. Verified:
  credit misattribution stays established in physics and biology; institutional
  exclusion stays established in physics and in Mathematics & Computing;
  gatekeeping, the theory-experiment asymmetry and delayed recognition stay
  emergent where they were.
- Both figures are published. `support` counts cases; `independent_support`
  counts contexts; **only the second decides lifecycle status**. An instance set
  that collapses to one context is flagged `regime-bounded` on the sector page.
- An unknown context string fails validation rather than silently creating a
  false independence.

Fourteen machine checks cover the model, including one asserting that a mechanism
with several cases in one context stays emergent.

## 2. The new mechanism

**Compulsory Secrecy** (`/concepts/compulsory-secrecy`), audit-eligible:

> Compulsory secrecy is a mechanism in which a formal legal or classification
> regime requires a contribution to remain outside the public record, constraining
> contemporaneous recognition independently of the receiving community's readiness
> to understand the work.

The name was chosen over two alternatives that were considered and rejected.
*State secrecy* would exclude formal nondisclosure regimes imposed by non-state
bodies, which the causal structure does not distinguish from. *Statutory secrecy*
would exclude classification implemented administratively under a broader legal
instrument, which is how much of it actually operates. The chosen name describes
the causal structure — an obligation that removes the choice to publish — rather
than the apparatus that exposed it.

Five tests, all of which must hold:

1. a formal nondisclosure or classification obligation existed;
2. the contribution itself was covered by it;
3. public dissemination was actually prevented or materially delayed;
4. the absence of visibility was not editorial discretion, low uptake, or
   contested attribution;
5. the effect on recognition is evidenced **separately**, not inferred from the
   existence of secrecy.

It is distinct from its three nearest neighbours by design, and each distinction
is what the two cases actually turned on. **Institutional exclusion** requires a
barrier to a position — both men held their posts and did the work in them.
**Delayed recognition** requires a community unable or unready to absorb the
contribution — in the Ellis case the community was demonstrably able, having
produced the same concept independently within about six years, and was
*prevented from knowing* rather than unready. **Institutional gatekeeping**
requires a person exercising editorial or institutional discretion — a
classification regime binds everyone involved, including whoever would otherwise
have exercised it.

## 3. Reclassification, and what did not change

Flowers and Ellis now carry `compulsory-secrecy`, both in the
`uk-government-cryptographic-secrecy` context. **No score moved**, because no
evidence changed: the same sources, the same dimensions, the same gaps of 27 and
34. Their `mechanism-boundary` audit exceptions are **kept, not deleted**, and
marked resolved with a date — the sequence is the finding, and deleting the
record of it would erase the one thing that makes the addition defensible.

## The corpus after the review

| | Before | After |
| --- | --- | --- |
| Deficit cases | 5 | 5 |
| Deficits with an evidenced mechanism | 3 | **5** |
| Unexplained under-recognition | 2 of 5 | **0 of 5** |
| Audit-eligible mechanisms in the ontology | 6 | **7** |
| Mechanisms evidenced in this domain | 2 of 6 | **3 of 7** |
| Established | institutional exclusion | institutional exclusion |
| Emergent | delayed recognition | delayed recognition, **compulsory secrecy (2 cases, 1 context)** |
| Aligned cases | 5 of 10 | 5 of 10 |
| DDI range, gaps, award relations | unchanged | unchanged |

Every Definition-of-Done criterion for this domain is now met **except synthesis**.

## Outcome classes: three, not four

A fourth class — "mechanism evidenced but only within one regime" — was
considered and rejected. It would mix two different dimensions: *what happened to
the case* and *how broadly the mechanism has been independently replicated*. This
project has separated those kinds of question repeatedly, and the separation is
what the recurrence model exists to enforce. The three classes stand:

1. **Mechanism evidenced** — now including both secrecy cases.
2. **Recognition aligned** — no deficit requiring explanation.
3. **Under-recognition mechanism-unresolved after audit** — currently empty in
   this domain.

The regime-bounded status of compulsory secrecy belongs to **mechanism maturity**,
where it is published as two cases and one independent context, and not to the
classification of the cases themselves.

## What the review changes about Cycle 03's headline finding

Stage 3's provisional reading was that Mathematics & Computing produces
recognition gaps the ontology cannot explain. That reading is **withdrawn**. Every
deficit in the domain is now explained, and the domain's contribution turns out to
be methodological rather than substantive:

> **A completed corpus forced the ontology to distinguish recurrence from
> independent replication.**

It is the third time a domain has corrected the instrument rather than merely
populating it. Physics forced the project to stop using mechanism counts as
maturity gates. Biology forced it to distinguish aligned cases from unexplained
deficits. Mathematics & Computing forced it to distinguish two observations from
two independent contexts.

## Cross-cutting stays at 0/0/0

Unchanged and deliberately so. After three rounds no entity has ever been assigned
to it on evidence. Its emptiness is now a result about the usefulness of the
category, not a hole to be filled, and whether it remains as a reserved category
is a closure decision rather than an expansion one.
