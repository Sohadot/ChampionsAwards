# Cycle 03 — Award anatomies, and the recompute at the same 5 cases

Round: **identity correction → Turing Award anatomy → Fields Medal anatomy →
recompute**, 2026-09-12. No case was added, removed or rescored. The corpus is
still paused at 5 while the next three are chosen.

Corpus: mathematics-computing `53d5e28d5677`, data through 2026-09-12.
Award relations **0 → 3**. Subfield awards: mathematics 1, computing 1,
cross-cutting 0. Definition of Done: award anatomy now **mapped**; cases 5/10 and
synthesis remain.

## What changed, and what deliberately did not

| | Before | After |
| --- | --- | --- |
| Award relations in the domain | 0 | 3 |
| Interaction types present | — | documented-award-outcome, eligibility-constraint, historical-non-award |
| Subfield awards | 0 / 0 / 0 | mathematics 1 / computing 1 / cross-cutting 0 |
| Architecture elements documented | — | Turing **3 of 12**, Fields **9 of 12** |
| DDI, observed recognition, gaps, mechanisms | 5 cases | unchanged |

`eligibility-constraint` is the first of its kind in the corpus. Physics carries
a `posthumous-constraint`; neither mature domain has ever produced a relation
where a live eligibility rule was applied to a dated event and the application
is on institutional record.

## The six questions

**1. Have Turing relations begun to show a recurring architecture interaction,
or is there only Liskov?** Only Liskov, and the binding constraint is not corpus
size. The awarding society's pages — the award page, the nomination process, the
advice for nominators, the committee procedures, the Turing FAQ, the committee
page, the digital library — all returned HTTP 403 to this audit across three
domains, so nine of twelve architecture elements are absent. A second Turing
laureate entering the corpus could only attach to `eligibility`, because that is
the only element with an anchor. The Turing page will stay thin until either the
society becomes readable or a non-society institutional description of the
procedure is found. That is a fact about source access, and it should not be
mistaken for a fact about the award.

**2. Is the Fields age rule a one-off for Wiles, or analytically useful?**
Analytically useful, and it describes a class rather than a person. The rule bars
any mathematician whose major work matures after forty, which is a structural
property of the award, not an accident of one career. The machinery to test it
now exists and is exercised: a `rule_at_time` block dated to the 1998 event and
marked established on an institutional anchor, plus an `eligibility-constraint`
relation. What the single case establishes is one direction only — that the rule
applied. It says nothing yet about whether being excluded by it predicts anything
about a person's gap, because the one case came out **negative** at −8. A second
age-rule case is the only way to learn whether that is general or particular to a
subject this heavily decorated.

**3. Is a lower-DDI case needed to break the 85–86 compression?** The data say
yes, and say it more sharply than the Stage 1 read did:

| Domain | n | DDI range | DDI spread |
| --- | --- | --- | --- |
| Physics & Astronomy | 10 | 74–87 | 13 |
| Biology & Medicine | 10 | 74–88 | 14 |
| Mathematics & Computing | 5 | 85–86 | **1** |

Both mature domains reached a spread of 13–14. This one is at 1. The most
economical explanation is **selection**: five contributors were chosen at the very
top of their field, so the merit side had nothing to discriminate. This is an
observation about the corpus, not about the domain and not about the instrument's
quality — the DDI's merit side has demonstrably spread 13 points elsewhere, so
nothing here shows it failing. The Stage 1 read used the compression as evidence
for the composite-domain question; that use is withdrawn and the read now carries
a dated correction. Until a case is entered whose assessed merit is genuinely
lower, no statement about how this domain's merit is distributed can be made at
all.

**4. Is under-recognition needed that does not rest on institutional exclusion?**
The deficit population is two cases and both carry the same mechanism. Ontology
coverage is 1 of 6: this domain has produced no credit misattribution, no
gatekeeping, no delayed recognition, no posthumous recognition and no
theory-experiment asymmetry. For contrast, credit misattribution is established
at 8 of 10 in physics. Two readings are open and the corpus cannot yet separate
them — that mathematical and computing recognition genuinely run on different
failure modes, or that five cases chosen for other reasons happened to miss them.
Both readings recommend the same next step, which is why this is the clearest
signal in the round.

**5. Is a cross-cutting case needed, or does the Wolf Prize alone not justify
one?** The question is mis-posed, and the anatomies show why. The corpus already
touches the cross-cutting system: Wiles holds the Wolf Prize in Mathematics,
recorded in his entry on the Royal Society's own fellow record. What is missing
is not a case but an **anatomy** — with no Wolf Prize architecture, that
touchpoint is invisible to the interaction layer, exactly as Liskov's Turing
Award was invisible before this round. Creating a case to populate a subfield
would be building evidence to fit a coverage table. Reading the system that is
already touched would not.

**6. Has the composite-domain hypothesis strengthened now that each half has its
own award architecture?** It has become **answerable**, which is different from
confirmed, and the first answer complicates the name rather than defending it.

Strengthened: both halves now carry an award architecture under the same schema,
so the two recognition cultures can be compared element by element for the first
time rather than by counting cases.

Complicated: the comparison returns a large contrast. Nomination is open at the
Fields Medal — anyone may submit to the committee chair, self-nomination is
merely discouraged, and the committee may consider people nobody nominated — and
invitation-only at the Nobel. Committee membership is published for every Fields
award since 1936 while its nominations are confidential with no release horizon;
the Nobel seals both for fifty years and then opens them. The Turing Award
publishes neither, at least not readably. Funding runs from a university trust
the union calls significantly underfunded, to a foundation's own endowment, to a
single commercial sponsor.

On that evidence the Fields Medal has more in common with the Nobel system — a
published statute, a closed deliberation, a scholarly granting body funding
itself or from a trust — than it has with the Turing Award, which sits in the
same domain. **The two halves of this domain are comparable, and they are not
alike.** "Mathematics & Computing" therefore holds up as a unit of comparison and
not as a claim of similarity. No split is proposed; the hypothesis is recorded as
answerable and, on its first reading, as describing a contrast rather than a
shared culture.

## One thing the round established about the instruments

The governance/funding separation is now enforced rather than asserted.
`funding_source` is a first-class architecture field, an anatomy that names the
granting body without naming the funder fails validation, and four machine checks
cover the rule. Both Nobel anatomies were amended in the same pass to state, in
that slot, that no external sponsor appears in their governing documents. The
Cycle 03 requalification had already lowered the Turing independence score from
85 to 62 on this confusion; what changed here is that the next anatomy cannot
repeat it silently.

## Still not chosen

The next three cases. Questions 3 and 4 point at the same kind of gap from
different directions, and question 5 points at an anatomy rather than a case.
Nothing in this round settles which of those the corpus should spend its next
batch on.
