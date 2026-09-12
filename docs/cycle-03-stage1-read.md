# Cycle 03 — Individuals Expansion, Stage 1: the pause at 5

Round: **Liskov → Spärck Jones → Conway → Wiles**, 2026-09-12. Four researched,
four published, no reserve drawn. The corpus is paused at 5 cases in
Mathematics & Computing for assessment before any further expansion.

Corpus: mathematics-computing `313a306d5d8e`, data through 2026-09-12.
Mechanism accounting 5/5 (100%), cases unaudited 0, source-grade closure 8/8.

## The four, and what they returned

| Case | Subfield | Entered to test | DDI | Obs | Gap | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Barbara Liskov | computing | an award-positive control on the empty side | 85 | 90 | **−5** | **Aligned, no mechanism.** Holder of the field's highest award; the first case in the whole corpus whose subject won the top prize of their own domain. |
| Karen Spärck Jones | computing | an outcome that could not be predicted in advance | 86 | 80 | **6** | **Aligned, no mechanism.** Two fields' premier lifetime awards against thirty-seven years without an established post. The employment record is documented and deliberately not scored as a recognition mechanism. |
| Lynn Conway | computing | whether documented exclusion can be held apart from recognition outcome | 85 | 75 | **10** | **Mechanism evidenced.** The 1968 termination is stated by two bodies that later honoured her. The entry tags the barrier and declines the arithmetic. |
| Andrew Wiles | mathematics | whether a documented eligibility rule produces a deficit | 86 | 94 | **−8** | **Aligned, no mechanism, constraint real.** The rule is published, was applied, and the union created a one-off tribute because of it. The gap is still negative. |

## The seven readings

**1. Mathematics vs computing coverage.** mathematics 2 cases / 1 system,
computing 3 cases / 1 system, cross-cutting 0 cases / 1 system. Cases
unassigned 0, imbalance 1. `comparison_meaningful` has flipped from **False to
True** — the condition that made the domain's internal comparison vacuous at
Round 1 no longer holds. The subfield counts still gate nothing.

**2. Gap distribution.** Range −8 to 17, median 6, five cases. Round 1 had a
single case at 17 and a median equal to it. The domain now has a measured
spread, and it is narrower than either closed domain: Physics & Astronomy runs
11 to 42, Biology & Medicine −2 to 41.

**3. Aligned vs deficit.** Three aligned, two with a deficit. This is the first
domain in the corpus where aligned cases are the majority. It is also the only
domain where that majority was partly designed: one of the three was entered as
a deliberate control, which is a reason to read the ratio as a property of this
sample and not of the domain.

**4. Mechanisms by subfield.** One mechanism is evidenced in the domain —
institutional exclusion, support 2 of 5 (40%), **established**. Its two cases
are Noether (mathematics) and Conway (computing). This is the first mechanism in
this corpus evidenced on both sides of a composite domain. Five audit-eligible
mechanisms return nothing here; the ontology coverage is 1 of 6.

**5. Turing / Fields interaction.** Machine-visible award relations in this
domain: **0**. Neither flagship system has an award anatomy, so no case-to-award
relation exists for the engine to count, even though two cases touch those
systems directly — Liskov holds the Turing Award, and Wiles is tied to the
Fields Medal's eligibility rule through a dated `rule_at_time` block in his
provenance. The interaction is in the data and invisible to the instrument.
That is a gap in the award layer, not in the cases.

**6. Unresolved under-recognition.** **0.** Both under-recognized cases carry an
evidenced mechanism. This is the first domain in the corpus with complete
explanatory coverage of its deficit population, and it is a small population —
two cases — so the figure describes this corpus, not the field.

**7. Cross-cutting.** Still empty of cases: 0 cases, 1 system (the Wolf Prize).
The Round 1 observation stands for this third compartment unchanged.

## The new question

> Do Mathematics and Computing merely share a repository category, or are they
> beginning to produce comparable recognition observations under the same
> instruments?

**They are beginning to, and the evidence is thin enough to say so carefully.**

Three things now point the same way across the boundary. The DDI values sit in a
band of two points across all five cases (85–86) while the observed recognition
ranges over nineteen (75–94), so within this corpus the instrument is
discriminating on the recognition side rather than on the merit side, and it does
so identically in both subfields. Institutional exclusion is evidenced once on
each side. And both subfields have produced an aligned case, which means neither
is behaving as a register of a single outcome class.

Two things still pull the other way. The one mechanism the domain has is shared,
but five of six eligible mechanisms are absent everywhere in it, so the
"comparable observations" are comparable mostly in what they do not contain. And
the award layer is empty on both sides, so the strongest form of comparison —
the same recognition system read against several cases — has not been attempted
here at all.

The composite domain hypothesis is therefore **less unstable than it was at
Round 1 and not yet established**. No split is proposed, and no DoD criterion
is added; this is recorded as an observation, as the Round 1 boundary audit was.

## What this round deliberately did not do

- It did not preassign a pattern to any case. Institutional exclusion was tagged
  once, on the one case where two institutions state the barrier; it was tested
  and refused on Spärck Jones, where the subject's own recorded account says the
  opposite, and on Liskov, where a documented first is not a documented barrier.
- It did not score Wiles against the Fields Medal. His observed recognition is
  read across the whole of mathematical recognition, which is the only reading
  that can distinguish an excluded candidate from an unrecognised one.
- It did not invent an ontology entry for an eligibility constraint that
  produces no deficit. The constraint is recorded where temporal validity
  belongs — in `provenance` with a `rule_at_time` block dated to the 1998
  Congress — and the mechanism audit returns no mechanism, which is the honest
  result rather than a convenient one.

## Two disclosures

**Conway sits exactly on a threshold.** Her gap is 10, and
`UNDER_RECOGNITION_MIN_GAP` is 10 inclusive. One point of observed recognition in
either direction moves her between "under-recognized" and "recognition roughly
matches assessed merit". The score was not adjusted away from the edge, and the
case entry says so in its own rationale.

> **Resolved, 2026-09-12.** The label was corrected in the round that followed
> this read: the section is now **The Recognition Archive**, and the sentence that
> assumed failure was replaced by the project's own three-outcome logic — *a
> governed archive of how contribution and recognition align, diverge, or remain
> unresolved*. The URL and the data cluster are unchanged; `unawarded` survives as
> a corpus subset, not as the public identity. The paragraph below is left as it
> stood when the question was still open.

**The archive's name is now carrying a case it does not describe.** Liskov holds
the Turing Award and her page renders under the eyebrow "The Unawarded Archive".
The precedent for filing an aligned case there was set in Cycle 02 by Apgar (−2)
and Hilleman (+6), so this round introduces nothing new mechanically. What is new
is that the corpus now contains a laureate of her domain's highest award. Whether
the archive's public label should change is a question about the project's
identity rather than about this round's evidence, and it is left open here rather
than settled unilaterally.
