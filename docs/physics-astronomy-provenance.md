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

A claim is **record-grade OK** when at least one record-grade source backs it.
Each entry resolves to one of three audit states:

- **source-grade closed** — every load-bearing claim is record-grade.
- **needs-primary-strengthening** — a claim currently rests on a secondary
  source and a stronger record plausibly exists to be linked.
- **primary-not-found / secondary-record-sufficient** — declared per claim via
  an entry's `audit_exceptions` only after a real search concludes no primary
  is available; the project then relies on the best secondary record and claims
  no more than that. Being able to say this openly builds more trust than
  hiding the gap.

## Rule of order

The audit inspects **evidence before scores**. A strengthened or contradicting
source triggers a re-assessment of the affected DDI/RLS dimension; a source is
never swapped to move a number. The model yields to the evidence — the evidence
is never bent to satisfy the model.

## Current snapshot (2026-09-09)

Individuals (10) and the three physics-relevant systems. No `audit_exceptions`
are declared yet: strengthening and any secondary-sufficient declarations await
a dedicated archival pass, and no score was changed in this cycle.

| Entry | Audit status |
|---|---|
| Cecilia Payne-Gaposchkin | source-grade closed |
| George Zweig | source-grade closed |
| Vera Rubin | source-grade closed |
| Chien-Shiung Wu | needs-primary-strengthening (contribution) |
| Jocelyn Bell Burnell | needs-primary-strengthening (contribution) |
| Lise Meitner | needs-primary-strengthening (contribution; institutional-exclusion) |
| Nikola Tesla | needs-primary-strengthening (attribution; recognition; credit) |
| Henrietta Swan Leavitt | needs-primary-strengthening (all claims) |
| Ralph Alpher | needs-primary-strengthening (all claims; scholarly-secondary only) |
| Satyendra Nath Bose | needs-primary-strengthening (all claims; reference-secondary only) |
| Nobel Prize System | source-grade closed |
| Breakthrough Prize in Fundamental Physics | source-grade closed |
| Wolf Prize | needs-primary-strengthening (track record) |

**Source-grade closed: 5 / 13.** This is the honest baseline. A domain is not
declared mature v1.0 until this matrix is resolved — every entry either closed
or carrying a reviewed secondary-sufficient exception — which is separate from,
and stricter than, the numeric Definition of Done.
