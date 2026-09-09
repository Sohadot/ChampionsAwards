# Physics & Astronomy — Provenance Matrix (Cycle 01)

This is a **snapshot** produced by `scripts/source_audit.py`. Regenerate it any
time with `python scripts/source_audit.py`; the tool reads the same evidence
maps the site is built from, so this record cannot drift from the data.

## What the audit checks

It does not count "how many primary sources" — a metric that is easy to game.
It inspects each **load-bearing claim** on a case (its contribution,
attribution, observed recognition, and every structural pattern) and each RLS
dimension on a system, and asks which **source type** backs that specific claim.

Source types form a functional taxonomy (see `SOURCE_TYPES` in
`scripts/config.py`), not an A/B/C ranking:

- **record-grade** — `primary`, `archival`, `institutional`
- **secondary** — `scholarly-secondary`, `reference-secondary`, `general-secondary`

Closure is **claim-level authority**, not source type: a claim closes only when
the entry declares a `provenance` record_anchor — a record-grade source — with a
`basis` saying why that source is authoritative for that specific claim. A
source being `institutional` does not close a claim on its own. Each claim
resolves to one of four legitimate ends:

- **closed** — a record anchor was found (`provenance`).
- **secondary-record-sufficient** — after a documented search no primary record
  exists; the entry carries an `audit_exceptions` decision (claim, search date,
  note, best source, reason) and claims no more than the best secondary record.
- **corrected** — the evidence was weaker than or contradicted the wording, so
  the claim (and, if warranted, its rationale or score) was revised.
- **withdrawn** — the claim or pattern could not be defended and was removed.

Saying "no primary was found, here is the best secondary" openly builds more
trust than hiding the gap. The goal is never 13/13 green — it is 13/13
**known-status**.

## Rule of order

The audit inspects **evidence before scores**. A strengthened or contradicting
source triggers a re-assessment of the affected DDI/RLS dimension; a source is
never swapped to move a number. The model yields to the evidence — the evidence
is never bent to satisfy the model.

## Snapshot after the archival strengthening pass (2026-09-09)

Introducing claim-level authority first **reopened all 13** (the earlier "5/13"
was closure inferred from source type — false closure). A targeted, web-verified
archival pass then anchored each factual claim to a record where one exists, and
recorded a documented exception where none was found. No score was changed: the
live sources confirmed every claim, so no corrections or withdrawals were
needed. Primary anchors added this pass include the original papers of Wu (1957),
Bell Burnell/Hewish (1968), Meitner/Frisch (1939), Leavitt (1912), Bose (1924),
and Alpher/Herman (1948).

| Entry | Audit status |
|---|---|
| Chien-Shiung Wu | source-grade closed |
| Jocelyn Bell Burnell | source-grade closed |
| George Zweig | source-grade closed |
| Vera Rubin | source-grade closed |
| Nobel Prize System | source-grade closed |
| Wolf Prize | source-grade closed |
| Breakthrough Prize in Fundamental Physics | source-grade closed |
| Lise Meitner | closed; exception: institutional-exclusion |
| Henrietta Swan Leavitt | closed; exceptions: attribution, credit-misattribution |
| Ralph Alpher | closed; exceptions: attribution, credit-misattribution |
| Satyendra Nath Bose | closed; exception: observed-recognition |
| Nikola Tesla | closed; exceptions: attribution, recognition, credit |
| Cecilia Payne-Gaposchkin | secondary-sufficient (all claims; primary thesis not yet linked) |

**Known-status: 13 / 13** — 7 fully source-grade closed, 6 closed with
documented secondary-sufficient exceptions, 0 unresolved. The Source-grade
criterion for Physics & Astronomy is therefore **closed** (every claim has a
defended status), even though not every claim is anchored to a primary. Open
follow-ups are honest, bounded strengthening tasks — e.g. linking Payne's 1925
thesis or an archival record of Meitner's exclusion — not blockers.
