# Cycle 02 — Ontology & Explanatory-Coverage Hardening

Round 4, 2026-09-11. **No case data changed**: no score, no pattern, no source, no
threshold, no Definition of Done criterion. What changed is the semantics of two
things the project had been measuring loosely.

## 1. Concepts now declare what kind of thing they are

The concept cluster mixed levels. `credit-misattribution` names an act that can be
looked for in a record; `recognition-bias` is an umbrella tendency covering several
possible mechanisms; `merit-vs-recognition` is a framework distinction that is never
true or false of a single case. Treating all three as candidate mechanisms made the
ontology look narrower than it is and made a framework concept capable of being a
"failed mechanism test".

Every concept now carries a `concept_type` (`CONCEPT_TYPES` in `scripts/config.py`):

| Type | Concepts | Case-testable |
| --- | --- | --- |
| `mechanism` | credit-misattribution, delayed-recognition, institutional-exclusion, institutional-gatekeeping, posthumous-recognition, theory-experiment-asymmetry | **yes** |
| `recognition-pattern` | recognition-bias | no — it covers several mechanisms rather than being one |
| `framework-concept` | merit-vs-recognition | no — a distinction the project reasons with |

No concept was rewritten to fit a class. The classes record what each concept
already was.

**Enforced:** `mechanism_audit.considered` and a case's `patterns` may name only
audit-eligible concepts (`AUDIT_ELIGIBLE_CONCEPT_TYPES` = `mechanism`). The
validator caught the error immediately in **all twelve** audited cases, every one
of which had listed `recognition-bias` among the mechanisms it tested. Those
entries are corrected. No finding moved: `recognition-bias` had never been tagged
on any case, because it never could have been.

## 2. "Unexplained" now means unexplained under-recognition

`no-mechanism-evidenced` remains the raw audit result and is unchanged on every
case. What changed is the reporting. The engine now computes
`explanatory_coverage`, using the gap bands the site already publishes rather than
a new threshold, and separates:

- **unexplained under-recognition** — no evidenced mechanism *and* a gap at or
  above the published `under-recognized` floor (10 points);
- **aligned, no mechanism required** — no evidenced mechanism and a gap inside
  the band where recognition roughly matches assessed merit.

The second group is not an explanatory failure. It is the expected result for a
case with no deficit outstanding.

### Recomputed, with no data change

| | Physics & Astronomy | Biology & Medicine |
| --- | --- | --- |
| Cases | 10 | 10 |
| With a recognition deficit (gap ≥ 10) | 10 | 8 |
| **Unexplained under-recognition** | **1/10** (Bose) | **3/8** (Avery, Stevens, De) |
| Aligned, no mechanism required | 0 | **2** (Hilleman +6, Apgar −2) |
| Audit-eligible mechanisms evidenced | 4/6 | 3/6 |

By band, Biology:

| Gap band | Cases | Mechanism evidenced | None evidenced |
| --- | --- | --- | --- |
| significantly under-recognized | 5 | 3 | 2 |
| under-recognized | 3 | 2 | 1 |
| recognition roughly matches assessed merit | 2 | 0 | 2 |

## 3. What this round deliberately did not do

- It set **no new Definition of Done gate**. Coverage is reported, not required.
- It changed **no score, pattern, source or audit finding**.
- It did **not** coin a concept for the two peripheral cases (Bose, De) whose
  gaps remain unexplained. Two cases with a shared feature and no established
  causal link are a hypothesis worth testing later, not a mechanism.

The correction is recorded in `cycle-02-stage2-read.md` rather than applied
silently: that document's closing question was framed on the uncorrected figure,
and both the old framing and the new one are visible there.
