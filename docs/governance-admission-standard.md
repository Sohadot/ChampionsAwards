# Governance Admission Standard — GAP v1.0

> Nothing enters the public corpus merely because it exists. It enters only after
> it proves what it is, where it came from, what it claims, and that it cannot
> degrade the system.

*Written 2026-09-13, two-axis model and CI v1 added 2026-09-14, enforcement state
synchronised with branch protection as verified 2026-09-30, GAP-01 implemented
2026-09-30. This is the
standard, not the implementation. The registry in `scripts/config.py` says which
layers exist as controls and where those controls run; the two are different
questions and are measured separately. A governance document that described its
aspirations as controls would be the same defect this project keeps finding in
its own claims.*

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

Within a hazard layer the two outcomes are separated by rule, not by judgement,
so that low quality is never handled like malware. GAP-09 is the clearest case:

| condition | decision |
| --- | --- |
| mass-generated, near-duplicate, templated or promotional | **QUARANTINE** — withheld, retained, remediable |
| malicious injection, hidden payload, cloaked or doorway behaviour | **BLOCK** — removed, never remediated in place |

## Two axes, because one word was doing two jobs

A layer can be fully implemented and still bind nothing. GAP-11 refuses what it
names — and refused nothing on any push, because no automated step invoked it.
Calling that both "enforced" and "advisory" in one document was ambiguous rather
than wrong, so the axes are now separate:

| axis | values |
| --- | --- |
| **implementation** — does a control exist that refuses what this layer names? | `enforced` · `partial` · `absent` |
| **enforcement** — where does that control run? | `none` · `local-only` · `ci-observed` · `required` |

> A layer governs admission only when it is **implemented AND required**.
> Anything short of both is a detector.

`effective` in the coverage report counts exactly that intersection. It is the
only figure that describes what the pipeline actually decides.

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

**Implementation: 2 of 12 enforced, 8 partial, 2 absent.
Enforcement: 10 required, 2 none. Effectively enforced: 2 of 12.**

The two are GAP-01, repository admission, and GAP-11, public surface — the only
layers whose control is complete and runs inside the required job. The eight
partial layers are required too, and remain partial: a required check on half a
control blocks only the half that exists.

How the figure moved, so the history stays legible: from 2026-09-14 until branch
protection was applied the registry read *9 ci-observed, effectively enforced 0 of
12*. Protection moved the enforcement axis alone, to *9 required, 1 of 12* (GAP-11).
GAP-01 then moved from absent to enforced by building its control, which is the
first change to the implementation axis since the standard was written.

The two absent layers — security and spam/abuse — have never been tested by
events. The corpus is small and hand-built, which is why neither has bitten, and
is not evidence that neither can.

## GAP-01 — Repository Admission

*Is this file a kind of thing this repository accepts, at all?* Asked of every
tracked file before anything reads it for meaning, by
`scripts/repository_admission.py`; its decision contract is frozen by
`scripts/test_repository_admission.py`.

**Population.** The Git index — `git ls-files --stage`, which in a clean CI
checkout is exactly the commit under test — with content read from Git's object
database, not the working tree. Untracked files and ignored build output
(`public/`, `reports/`) are not repository artefacts and are not in scope. The
control is read-only: it repairs, renames and deletes nothing.

**Admitted types.** `.py` `.yaml` `.yml` `.html` `.css` `.md` `.txt`, and the
basename `.gitignore`: exactly what the tracked tree held when the control was
written (126 files, all mode `100644`). Suffixes match exactly, case included.
Admitting a new type is a one-line policy change in a reviewed pull request, never
a side effect of committing one. There is no "anything text-like" rule; that
would not be an allowlist.

**Size ceiling.** 512 KiB per file, a fixed constant. The largest file at
adoption was 85,195 bytes. The ceiling is not derived from the tree, because a
threshold that moves with the tree normalises an oversized file once it arrives.

| finding | decision |
| --- | --- |
| a type outside the allowlist, including no suffix | QUARANTINE |
| a file over the ceiling | QUARANTINE |
| an admitted type that is not valid UTF-8 | QUARANTINE |
| any symlink that stays inside the repository | QUARANTINE — not in the vocabulary |
| a Git mode that is not a file (a submodule) | QUARANTINE |
| executable Git mode `100755`, whatever the content | BLOCK |
| an executable, compiled or archive suffix (`.exe`, `.so`, `.jar`, `.zip`, `.tar`, `.gz` …) | BLOCK |
| an executable or archive **signature**, under any name (ELF, PE, Mach-O, zip, gzip, bzip2, xz, 7z, rar, zstd, tar, wasm) | BLOCK |
| a NUL byte — admitted types are text, so this is a binary payload | BLOCK |
| an unbroken base64/hex run of 1024+ characters with 16+ distinct symbols | BLOCK |
| a symlink that is absolute, or resolves lexically outside the repository | BLOCK |
| a credential file by name (`.env`, `.env.*`, `id_rsa` and kin, `.netrc`, `.pypirc`, `.npmrc`, `.htpasswd`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`) | BLOCK |
| a private-key armour block, or a high-confidence token (AWS access key id, GitHub classic and fine-grained, Slack, Google API key, Stripe live secret, Anthropic API key) | BLOCK |

Every finding is reported, and the result is the strongest: BLOCK over QUARANTINE
over PASS. Exit codes are 0, 1 and 2; a control that cannot establish its
population exits 3 and is never a pass.

**Executables.** Git mode is the property governed. Python source is not an
executable because it contains code; a file tracked `100755` is, and nothing in
this repository needs one. **Payloads** are recognised by name *and* by content,
so a zip renamed `notes.txt` is still a zip. **Symlinks** are judged from the link
itself, which Git stores as its target text; the target is never opened.

**What the secret scan claims, exactly.** It detects the signatures listed above,
which issuers design to be recognisable, and nothing else. There is no entropy
heuristic, so a password typed into a YAML value, or a token format not on the
list, passes. A match is reported by rule, line and a truncated SHA-256
fingerprint; the value is never printed. The test fixtures assemble their
secret-shaped strings at runtime from fragments, so the repository holds none.

**Where it runs.** As its own step in `Governed admission checks`, after checkout
and before dependencies are installed or anything is built — standard library and
`git` only, so an inadmissible tree gains no authority from running anything
first. Its test suite runs in `run_checks.py`, so a regression in the scanner also
fails the required job.

**What it does not claim.** GAP-01 proves the admission properties above and no
others; it does not make the repository "safe". "Obfuscated payload" is held to
its artefact-level meaning — a binary disguised as text, or an encoded run.
Obfuscated *behaviour* in admitted source — a script, an inline handler, a remote
call — is GAP-02's question, not this one's. Encodings other than a base64/hex run
(escape sequences, for example) are not detected.

## CI v1 — what it does, and when it became a gate

`.github/workflows/governance.yml`, added 2026-09-14. One job, deliberately: a
matrix, caches or parallel jobs would each add a way for the gate to be green for
a reason unrelated to the corpus.

```
clean checkout → GAP-01 repository admission → pinned install
              → assert no build output present → build.py → run_checks.py
              → gap_status.py (report)
```

Two properties are worth naming. The job **refuses a checkout that already
carries `public/` or `reports/`**, because generated output in the tree would
mean every later check was reading someone else's build. And it runs the checks
**against the build produced in that same job**, which is the defect that made a
local gate report green against output that no longer existed.

**The workflow alone was not a gate, and at first it was not one.** A workflow
makes checks automatic; it does not make them binding. **Three**
repository settings do that, and none can live in a file:

1. **Require a pull request before merging** — this is what forces every change
   onto the PR path. Reviewer approvals are optional for a solo maintainer; the
   PR requirement is not, because without it a change can reach `main` without
   ever becoming a pull request for the check to run on.
2. **Require status checks to pass before merging**, selecting the job
   `Governed admission checks` (GitHub lists it by job name, sometimes as
   `governance / Governed admission checks`).
3. **Do not allow bypassing the above settings** — without it, administrators,
   including the repository owner, are exempt by default.

An earlier version of this section listed only 2 and 3. That was wrong in a way
worth recording: a required status check governs *merges*, and "do not allow
bypassing" governs *who is exempt from the rules that exist*. Neither compels a
change to become a pull request in the first place, which is rule 1's job. The
document had described two thirds of a gate as a gate.

Until all three were set, every implemented layer's enforcement was
`ci-observed` — a detector that reports — and **effectively enforced was 0 of
12**, whatever this document or the workflow said. All three were in place on
`main` by 2026-09-30, with the protection applying to everyone. Enforcement moved
to `required` only for layers whose control the required job actually executes
on a failing path (traced in the comment above `GAP_LAYERS` in
`scripts/config.py`); the absent layers name no control and stay `none`.

### How to tell, without trusting anyone's word

`mergeable_state` on an open pull request whose check has failed:

| value | meaning |
| --- | --- |
| `unstable` | the check is red and **not required** — the merge is still permitted |
| `blocked` | the check is red and **required** — the merge is refused |

That single field is the difference between a detector and a gate, and it is
observable without asking whether the settings were applied.

**Verified 2026-09-30, by PR #1.** PR #1 was opened on 2026-09-14 as a
deliberately invalid change — a recognition system declaring a domain its own
`assessment_scope` excludes — and was never meant to merge. Its first half passed
at once: the job went red at *Build from source*, `validate_content` refused it,
and the checks correctly never ran against an unbuilt tree. Its second half
failed for as long as the settings were missing: the pull request read
`unstable`, a red check a merge could ignore. Once protection was applied it read
`blocked`, and it was closed without merging. The gate is binding because a change
that should fail was shown unable to merge — not because the workflow is green.

A green workflow is not proof of teeth. That lesson came from `assessment_scope`,
which passed every test written for it while remaining bypassable, and the same
standard applies here: the pipeline is proven binding only by a change that
*should* fail being *unable to merge*.

## Migration, not a rewrite

The way to reach the standard is to convert existing checks into it, one layer at
a time, cheapest real risk first — not to add dozens of new rules. Each conversion
is a commit that moves one layer's status and can be verified by the coverage
report changing.

The order this analysis suggests, and the reason for each:

1. ~~**CI from clean checkout**~~ — done 2026-09-14; binding once the three
   repository settings above were applied (verified by PR #1, 2026-09-30).
2. ~~**GAP-01 repository admission**~~ — done 2026-09-30: a file-type allowlist,
   a fixed size ceiling, payload, symlink and executable-mode rules, and a
   signature-only secret scan, run before anything installs.
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
