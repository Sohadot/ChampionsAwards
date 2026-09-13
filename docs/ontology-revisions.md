# Ontology revisions and audit currency

*Written 2026-09-12, after the Science Foundation Review found that mechanism
accounting could read 100 per cent in a domain whose audits had never tested
several of the mechanisms available to them.*

## The problem this closes

A mechanism audit records what it considered. Until now it did not record how
much there was to consider. The ontology has grown five times, so a list of five
considered mechanisms means "all of them" under one revision and "five of seven"
under another, and nothing in the record said which. Worse, the denominator moved
underneath the audits: every time a concept was added, every existing audit
silently became less complete, and no measurement anywhere would show it.

Two questions were being answered by one silence, and they are not the same
question:

1. Did this audit test everything that was eligible **when it ran**?
2. Does this audit cover the mechanism set **in force now**?

A "no" to the first is a defect in the audit. A "no" to the second is a dated
fact about a growing vocabulary, and treating it as a defect would mean a closed
domain reopens every time a word is added — which would make closure meaningless.

## The registry

`ONTOLOGY_REVISIONS` in `scripts/config.py` is the authority. Each revision
carries an immutable id, the commit that put it in force, its date, its mechanism
set, and a note on what changed. Ids are ordered **by commit, not by date**:
more than one revision landed on 2026-09-09, and a date cannot order them. A
published revision is never edited; a change to the set creates the next id.

| id | commit | date | mechanisms | what changed |
|----|--------|------|-----------|--------------|
| MOR-001 | `d6e52a0` | 2026-09-09 | 4 | Cycle 01 opens with the first four structural-cause concepts. |
| MOR-002 | `8a26749` | 2026-09-09 | 5 | Pattern lifecycle hardening adds theory–experiment asymmetry. |
| MOR-003 | `c78250e` | 2026-09-09 | 6 | Physics individuals completion adds institutional gatekeeping. |
| MOR-004 | `005a421` | 2026-09-11 | 6 | Concept types. The set is unchanged, but eligibility becomes formal: only `concept_type: mechanism` may be tested, so umbrella concepts stop being admissible in a `considered` list. |
| MOR-005 | `69ffcc0` | 2026-09-12 | 7 | The Cycle 03 ontology review adds compulsory secrecy. |
| MOR-006 | `442ffa6` | 2026-09-12 | 7 | The revision model itself. The set is unchanged, but an audit must now record its revision and either test everything eligible at it or declare the gap. |
| MOR-007 | `af76e55` | 2026-09-13 | 7 | Cycle 04 preflight narrows posthumous recognition to a rule shown to have constrained a specific recognition opportunity. The set is unchanged; what a test against that concept means is not. |

MOR-004 and MOR-006 show that a revision is not only a change of mechanisms: a
change in what an audit must do is a change the audits have to be read against.
MOR-006's hash was backfilled in the commit immediately after it, because a
commit cannot contain its own hash.

## How each audit was assigned

No revision was guessed. For each of the 22 audits, the commit that introduced
the `mechanism_audit` block was recovered from `git log -S`, and the revision in
force at that commit was established by ancestry, not by date arithmetic. Each
audit carries that revision in `ontology_revision` and the evidence in
`revision_basis`.

Ten biology-medicine audits and two physics audits had their `considered` lists
edited later, at `005a421`, when concept types made the umbrella concepts
ineligible. That edit **removed** candidates and tested nothing new, so those
audits remain audits of the revision they were performed under. The assignment is
robust to the alternative reading: MOR-003 and MOR-004 carry the same mechanism
set, so the measured gap is identical either way.

Two audits — Tommy Flowers and James Ellis — were extended at `69ffcc0`, when
compulsory secrecy entered the ontology and both cases were tested against its
five conditions. That was an audit act, so they are recorded at MOR-005.

Where history could not establish a revision, the sentinel
`legacy-revision-unresolved` is available. It was not needed: all 22 resolve.

## What the measurement found, before remediation

*The reading taken at commit `442ffa6`, when the model was introduced. It is kept
as the dated record of what the corpus looked like before the defects were
repaired; the current figures are in **Remediation** below.*

Both figures are computed by the engine from the case files and printed by
`scripts/domain_status.py` and on each sector page. Neither gates maturity.

**Completeness at the audit's own revision: 10 of 22.** Twelve audits did not
test a mechanism that was already eligible on the day they ran:

- All ten biology-medicine audits (MOR-003) omit **theory–experiment asymmetry**,
  eligible since MOR-002.
- `satyendra-nath-bose` and `vera-rubin` (MOR-003) omit **posthumous
  recognition**, eligible since MOR-001.
- All ten mathematics-computing audits are complete at their revisions.

Each of the twelve now declares its own gap in `incomplete_at_revision`. Nothing
was added to any `considered` list: an audit that did not test a mechanism cannot
be made to have tested it by editing a file.

**Currency against the revision in force: 2 of 22.** At that commit only Flowers
and Ellis covered the present seven-mechanism set. This is reported and gates
nothing.

## Remediation — 2026-09-12

The twelve defects were remediated by re-audit. The governing decision was that
partial repair is not repair: re-opening an audit to test only the mechanism it
missed would produce a second partial record and call it a fix. So each of the
twelve carries a `mechanism_reaudit` — a new dated search under MOR-006, tested
against **all seven** mechanisms, returning a verdict and a note for each one.

The original audits are untouched, `incomplete_at_revision` included. The record
therefore reads *the original audit was incomplete; a later re-audit remediated
it*, which is a stronger statement than a past edited to look complete.

Three figures, three different claims:

| | measured |
| --- | --- |
| Complete when originally performed | **10 of 22** — and this never moves |
| Historical audit defects remediated | **12 of 12** |
| Latest audit statement current against MOR-006 | **14 of 22** |

The eight that remain non-current are the Mathematics & Computing audits that
were complete at MOR-004 and predate compulsory secrecy. They are not defects and
were not re-run: an audit that was complete when performed has nothing to repair,
and re-running every audit after every addition to the ontology is not what
stability means.

**No re-audit changed anything.** No pattern was added or withdrawn, and no DDI,
observed-recognition or gap value moved. Each re-audit states both facts
explicitly rather than leaving them to be inferred from a diff.

## What the complete tests found

`theory-experiment-asymmetry` is **not supported in any of the ten Biology &
Medicine cases**. The concept is narrower than the shape it is often read as
having: it requires a prediction, an experiment that converts it into established
science, and reward flowing to the predicting theorists. Rosalind Franklin — the
case that made the defect look material — fails it on exactly that narrowness.
Her diffraction work and the Watson–Crick model appeared in the same April 1953
volume of Nature, with the model built from the data rather than predicted ahead
of it. The displacement the record documents is already carried by credit
misattribution, whose own definition names reward flowing to a theorist over an
experimentalist; tagging both would count one displacement twice. Oswald Avery,
the other strong-looking candidate, fails for the same structural reason.

`posthumous-recognition` is **not supported for either Physics & Astronomy case**,
and the reason generalises beyond them. Read literally — timing and eligibility
rules determining whether a contribution *can* be honoured — the mechanism is
satisfied by every scientist who has died since the Nobel Statutes acquired the
posthumous prohibition in 1974, Vera Rubin included, and a tag that fits every
deceased case distinguishes nothing. Read as the corpus actually uses it, as an
explanation of a measured recognition deficit, it requires an eligibility rule
shown to have determined an actual decision. Rubin's deficit was already in place
across four decades in which she was fully eligible; Bose's non-award is
documented as an evaluative judgment, with eleven nominations between 1956 and
1972 and a commissioned expert evaluation in 1956. The prospective foreclosure is
real and is recorded in both re-audits; it is not what produced either gap.

That tension between the two readings is an **observation for a future ontology
review**, recorded here and deliberately not acted on: this remediation closed
known defects and did not reopen the ontology.

## The open consequence — closed

The twelve gaps are not uniform in weight. Eleven concern a mechanism whose
relevance to the case is not obvious from the record. One is different:
**Rosalind Franklin** is, on the face of the record, the strongest
theory–experiment asymmetry candidate in the corpus — an experimentalist whose
data underwrote a model-building result that was recognised — and her audit never
tested that concept.

This was a possible material finding about a closed layer, not a clerical one,
and it was recorded rather than acted on because acting on it meant re-running a
mechanism audit against sources — an evidential act, not a refactor. It has since
been acted on, across all twelve rather than only the two obvious candidates: see
**Remediation** above. A closed layer is not frozen; it stays closed and stays
correctable.

## The rule going forward

From MOR-006, `incomplete_at_revision` is unavailable. A new audit records its
revision and tests every mechanism eligible at it, or it fails the gate. The
escape exists only for audits that predate the model, and it is one-way by
design — otherwise "incomplete at revision" becomes a permanent way to publish an
unfinished audit.
