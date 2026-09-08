# Editorial governance

ChampionsAwards earns trust by constraint, not by assertion. Every entry passes
an automated gate before it can be published. The gate is code, not a promise:
`python scripts/build.py` fails if any rule below is violated.

## The build pipeline

1. **`validate_content.py`** — well-formedness. Required fields, valid slug,
   minimum summary length, and the *shape* of optional blocks (`sources`,
   `assessment`, `key_facts`, `analysis`, `status`).
2. **`quality_gate.py`** — publication policy (below).
3. **`generate_core.py` / `generate_pages.py`** — render pages. Draft entries
   are skipped and never emitted.
4. **`generate_sitemap.py`** — sitemap of published URLs only.

## Publication policy (enforced)

An entry is **published** unless it declares `status: draft`. Published entries
must satisfy:

- **Sourcing.** At least one reference in `sources`, each with a title and a
  valid `http(s)` URL. Unsourced work stays `status: draft`.
- **Review date.** A `last_reviewed` field in ISO `YYYY-MM-DD` form.
- **Justified scores.** Any `assessment` block must include a `rationale` for
  its dimensions, and every DDI dimension must be a number 0–100.
- **Traceable facts.** Each `key_facts` entry may cite a `source` by 1-based
  index into `sources`; out-of-range citations fail the build.

## Neutrality discipline (enforced on all entries)

Entry prose may not contain unscoped superlatives (e.g. "definitive",
"the greatest", "unrivaled", "sovereign-grade"). The banned list lives in
`scripts/config.py` (`BANNED_TERMS`) and is scanned across every prose field.
The goal is a reader who trusts the reasoning, not the tone.

## Scoring integrity

The Deservingness Index (DDI) weights live in one place — `DDI_DIMENSIONS` in
`scripts/config.py` — and are mirrored by the client-side calculator and the
`/methodology` page. Changing dimensions, weights, or bands is a **version
bump** (`methodology_version` in `src/data/site.yaml`), so past scores remain
interpretable.

## Correction policy

Being wrong in public is normal and fixable. Substantive corrections are made
by editing the entry and advancing its `last_reviewed` date; a well-sourced
challenge is grounds for revision. The published `/protocol` page states these
commitments to readers.
