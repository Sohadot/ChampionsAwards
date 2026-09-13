# Governance Admission Standard — GAP v1.0

> Nothing enters the public corpus merely because it exists. It enters only after
> it proves what it is, where it came from, what it claims, and that it cannot
> degrade the system.

*Written 2026-09-13. This is the standard, not the implementation. One layer of
twelve is enforced today, eight are partial and three are absent, and the
registry in `scripts/config.py` says which is which. A governance document that
described its aspirations as controls would be the same defect this project keeps
finding in its own claims.*

## Why now

The project's risk has changed shape. For three cycles the danger was thin
evidence; the corpus is now dense enough that the danger is a single ungoverned
artefact — one file, one rule, one number — inheriting the credibility that
everything around it earned. Every failure this project has actually had was of
that kind:

| what happened | what it was really |
| --- | --- |
| "Definition & Documented Cases" on a concept with no cases | a claim that outlived its evidence, on nine pages |
| track record 80 on "most selections have proven durable" | an assertion admitted as a measurement |
| checks run against a build older than its inputs | a verification of something that no longer existed |
| a parser dropping every second year of `1994/5` | an analysis that looked like evidence |
| a scope rule bypassable by declaring no scope | a control with an unguarded default |

None was a content shortage. Each was something ungoverned that entered because
nothing said it could not.

## What this standard is not

It does not try to know whether a claim is true. That is not mechanisable, and a
system that pretended to it would be worse than one that does not: it would
launder judgement as validation. The standard governs **admission**, not truth —
whether an artefact has proven enough about itself to be published.

**Fail-closed is the default.** The absence of a rule is not permission.

## Decision states

Four, not two. Malware and a missing citation are both "invalid", and giving them
the same word discards the only distinction that decides what to do next.

| state | meaning |
| --- | --- |
| **PASS** | Admitted to the public corpus. |
| **REVIEW REQUIRED** | Structurally valid; an evidential or interpretive question needs a human decision. Does not publish while open. |
| **QUARANTINE** | Exists and is retained, but not admitted. Usually missing evidence rather than wrong content — kept for remediation, not deleted. |
| **BLOCK** | A safety or integrity hazard. Never enters the build, and is never remediated in place. |

**Only hazard layers may BLOCK** — repository admission, security, spam/abuse and
build integrity. An evidence layer that could block would eventually be used to
suppress an inconvenient finding rather than a threat. Evidence layers withhold;
they do not destroy.

## The twelve layers

Each layer owns one question. A failure belongs to exactly one layer, so that
"this failed" always answers "which contract did it break".

| id | layer | the question it owns | may decide |
| --- | --- | --- | --- |
| GAP-01 | Repository Admission | Is this a kind of file this repository accepts at all? | PASS · QUARANTINE · BLOCK |
| GAP-02 | Security | Does this introduce executable or network behaviour the site does not have? | PASS · BLOCK |
| GAP-03 | Data Admission | Is every field governed, typed and known? | PASS · QUARANTINE |
| GAP-04 | Evidence | Is every checkable claim anchored, derived, or declared as analysis? | PASS · REVIEW · QUARANTINE |
| GAP-05 | Source Quality | Is the source strong enough for the *kind* of claim it carries? | PASS · REVIEW · QUARANTINE |
| GAP-06 | Temporal Validity | Was this rule in force at the time it is applied to? | PASS · QUARANTINE |
| GAP-07 | Computation Integrity | Did this number come from a deterministic analyser over a retained dataset? | PASS · QUARANTINE |
| GAP-08 | Content Quality | Does this page carry enough governed substance to exist? | PASS · QUARANTINE |
| GAP-09 | Spam and Abuse | Is this mass-generated, templated, or promotional? | PASS · QUARANTINE · BLOCK |
| GAP-10 | Build Integrity | Was this verified against what the current sources actually produce? | PASS · BLOCK |
| GAP-11 | Public Surface | Does the built site match the governed source graph, exactly? | PASS · QUARANTINE |
| GAP-12 | Regression | Did admitting this lower the quality of what was already admitted? | PASS · REVIEW · QUARANTINE |

Order of execution, and no release if any layer withholds:

```
ingest → GAP-01 → GAP-02 → GAP-03 → GAP-04 → GAP-05 → GAP-06 → GAP-07
       → GAP-08 → build → GAP-10 → GAP-11 → GAP-12 → release
```

## Standing principles

**No silent coercion.** A validator says `FAIL: provenance missing`. It never
fills the provenance in, never rewrites a claim to make it pass, never defaults a
missing field into a plausible value. A gate that repairs its input is a gate
that manufactures evidence. *(Audited 2026-09-13: no validator in this repository
mutates the data it checks.)*

**Quarantine rather than deletion.** A rejected artefact is retained with the
reason for its rejection. Most rejections are evidential, and evidence arrives
later.

**Overrides are structured and rare.** There is no `skip_validation`. An override
is an exception record — who, why, when, what was bypassed, and when it must be
revisited — and the exception is itself subject to the gate. The corpus already
works this way for `audit_exceptions`.

**AI may propose. The governed pipeline decides admission.** An assistant may
search, extract, analyse and draft candidate data. It holds no bypass, and what
it produces passes the same schemas, provenance rules and tests as any other
contributor's work. *This document was drafted by one, and is subject to it.*

**Publication requires four validities.** Syntactic validity is not one of them
on its own:

> No artefact reaches the public corpus merely because it is syntactically valid.
> Publication requires evidential validity, architectural validity, security
> validity, and quality validity.

## Where the pipeline actually stands

Generated by `python scripts/gap_status.py` from the registry, and asserted by the
check suite: **a layer may not claim enforcement without naming a component that
exists**, and a layer naming nothing must declare itself absent.

**Coverage: 1 of 12 enforced, 8 partial, 3 absent.**

The three absent layers — repository admission, security, spam/abuse — have never
been tested by events. The corpus is small, hand-built and tracks only six file
types, which is why none has bitten, and is not evidence that none can.

## The finding that outranks all twelve

**There is no continuous integration.** No `.github/workflows`, no pipeline, no
check on `main`. Every "ALL SUITES PASSED" this project has ever reported was a
local run by whoever happened to be working, and nothing prevents a push that
never ran them. The build-staleness refusal added on 2026-09-13 closed the
smaller half of GAP-10; the larger half is that the gate is optional.

A twelve-layer admission pipeline that no automated step invokes is a description
of good intentions. **Until CI builds from a clean checkout and runs the
validators against the output of that same run, every layer below GAP-10 is
advisory** — including the ones marked enforced.

That is the first thing to build, ahead of any new check.

## Migration, not a rewrite

The way to reach the standard is to convert existing checks into it, one layer at
a time, cheapest real risk first — not to add dozens of new rules. Each conversion
is a commit that moves one layer's status and can be verified by the coverage
report changing.

The order this analysis suggests, and the reason for each:

1. **CI from clean checkout** — makes every other layer real rather than optional.
2. **GAP-01 repository admission** — a six-entry file-type allowlist and a secret
   scan; cheap, and it is the layer with the widest blast radius when absent.
3. **GAP-03 unknown-key rejection** — the concrete hole measured today: an
   invented `ddi_override` on a case passes validation and is silently ignored.
4. **GAP-02 security** — for a static site with no third-party script, the rule
   is nearly a constant: any new executable or remote behaviour is BLOCK.
5. **GAP-07 analyser tests** — the `1994/5` class of parser defect, which has
   already produced one finding that had to be withdrawn.
6. **GAP-12 before/after comparison** — the only layer that catches a change
   which is individually correct and collectively a regression.

Layers 5, 6, 8 and 9 follow. Each is a separate decision with its own evidence,
and none should be written before the layer it depends on is real.
