# SEO Architecture Audit — 2026-09-12

One pass over the whole site, run after the Wolf Prize anatomy and before Stage 2.
It changed **presentation only**. No case was added, removed or rescored; no
score, mechanism, provenance block or Definition-of-Done criterion was touched.
The one evidence change made in the same session — the withdrawal of the Wolf
Prize's Nobel-precursor claim — was committed separately and deliberately *before*
this audit, so that no page was given a stronger presentation contract while
carrying a claim we already knew was unclosed.

## The standing rule this establishes

> **Presentation may not claim more than the page contains.**

It is the same discipline the evidence layers run on, applied to titles,
descriptions, structured data and links. Every governed page now declares what it
is, and the gate checks the declaration against the built artefact rather than
against another declaration.

### A note on the limits

The title and description bounds (95 characters; 70–185) are **ChampionsAwards
presentation discipline, not a claimed search-engine requirement.** Search engines
publish no fixed title length, rewrite title links when they judge a better one
exists, and compose snippets from page content — a meta description may not be
used at all. These numbers keep a title readable at a glance and a description to
one honest sentence. The project does not represent them as anyone else's rule.
The same refusal to turn a heuristic into a fact governs the evidence layers.

## 1. Route inventory

63 built routes, every one governed by a contract, classified as follows:

| Class | Routes |
| --- | --- |
| person | 25 |
| concept | 8 |
| hub | 8 |
| award | 6 |
| recognition system | 6 |
| methodology | 4 |
| sector hub | 3 |
| synthesis | 2 |
| utility | 1 |

| Route | Class | Primary query | Indexing |
| --- | --- | --- | --- |
| `/awards/acm-am-turing-award` | award | Turing Award | index |
| `/awards/fields-medal-award` | award | Fields Medal | index |
| `/awards/nobel-peace-prize` | award | Nobel Peace Prize | index |
| `/awards/nobel-prize-in-physics` | award | Nobel Prize in Physics | index |
| `/awards/nobel-prize-in-physiology-or-medicine` | award | Nobel Prize in Physiology or Medicine | index |
| `/awards/wolf-prize-award` | award | Wolf Prize | index |
| `/concepts/credit-misattribution` | concept | credit misattribution | index |
| `/concepts/delayed-recognition` | concept | delayed recognition | index |
| `/concepts/institutional-exclusion` | concept | institutional exclusion | index |
| `/concepts/institutional-gatekeeping` | concept | institutional gatekeeping | index |
| `/concepts/merit-vs-recognition` | concept | merit vs recognition | index |
| `/concepts/posthumous-recognition` | concept | posthumous recognition | index |
| `/concepts/recognition-bias` | concept | recognition bias | index |
| `/concepts/theory-experiment-asymmetry` | concept | theory-experiment asymmetry | index |
| `/` | hub | recognition systems | index |
| `/awards` | hub | award architecture | index |
| `/concepts` | hub | recognition mechanisms | index |
| `/rankings` | hub | recognition gap index | index |
| `/recognition-systems` | hub | recognition system legitimacy | index |
| `/reports` | hub | recognition research | index |
| `/sectors` | hub | scientific recognition by field | index |
| `/unawarded` | hub | recognition gap | index |
| `/about` | methodology | about ChampionsAwards | index |
| `/framework` | methodology | recognition framework | index |
| `/methodology` | methodology | Deservingness Index | index |
| `/protocol` | methodology | editorial protocol | index |
| `/unawarded/albert-schatz` | person | Albert Schatz | index |
| `/unawarded/alice-ball` | person | Alice Ball | index |
| `/unawarded/andrew-wiles` | person | Andrew Wiles | index |
| `/unawarded/barbara-liskov` | person | Barbara Liskov | index |
| `/unawarded/cecilia-payne-gaposchkin` | person | Cecilia Payne-Gaposchkin | index |
| `/unawarded/chien-shiung-wu` | person | Chien-Shiung Wu | index |
| `/unawarded/emmy-noether` | person | Emmy Noether | index |
| `/unawarded/ernest-everett-just` | person | Ernest Everett Just | index |
| `/unawarded/george-zweig` | person | George Zweig | index |
| `/unawarded/gregor-mendel` | person | Gregor Mendel | index |
| `/unawarded/henrietta-swan-leavitt` | person | Henrietta Swan Leavitt | index |
| `/unawarded/jocelyn-bell-burnell` | person | Jocelyn Bell Burnell | index |
| `/unawarded/karen-sparck-jones` | person | Karen Sparck Jones | index |
| `/unawarded/lise-meitner` | person | Lise Meitner | index |
| `/unawarded/lynn-conway` | person | Lynn Conway | index |
| `/unawarded/maurice-hilleman` | person | Maurice Hilleman | index |
| `/unawarded/nettie-stevens` | person | Nettie Stevens | index |
| `/unawarded/nikola-tesla` | person | Nikola Tesla | index |
| `/unawarded/oswald-avery` | person | Oswald Avery | index |
| `/unawarded/ralph-alpher` | person | Ralph Alpher | index |
| `/unawarded/rosalind-franklin` | person | Rosalind Franklin | index |
| `/unawarded/sambhu-nath-de` | person | Sambhu Nath De | index |
| `/unawarded/satyendra-nath-bose` | person | Satyendra Nath Bose | index |
| `/unawarded/vera-rubin` | person | Vera Rubin | index |
| `/unawarded/virginia-apgar` | person | Virginia Apgar | index |
| `/recognition-systems/breakthrough-prize-fundamental-physics` | recognition system | Breakthrough Prize in Fundamental Physics | index |
| `/recognition-systems/fields-medal` | recognition system | Fields Medal legitimacy | index |
| `/recognition-systems/lasker-award` | recognition system | Lasker Award | index |
| `/recognition-systems/nobel-prize-system` | recognition system | Nobel Prize System | index |
| `/recognition-systems/turing-award` | recognition system | Turing Award legitimacy | index |
| `/recognition-systems/wolf-prize` | recognition system | Wolf Prize legitimacy | index |
| `/sectors/biology-medicine` | sector hub | Biology & Medicine recognition | index |
| `/sectors/mathematics-computing` | sector hub | Mathematics & Computing recognition | index |
| `/sectors/physics-astronomy` | sector hub | Physics & Astronomy recognition | index |
| `/reports/explained-aligned-unresolved-biology` | synthesis | Explained, Aligned, Unresolved | index |
| `/reports/recognition-failure-patterns-physics` | synthesis | Recognition Failure Patterns in Twentieth-Century Physics | index |
| `/calculator` | utility | Deservingness Index calculator | noindex |

## 2. Contract migration

The contract moved from `awards` alone to **all five data clusters** (41 entries
migrated) plus **16 generated routes** — hubs, sector references, the methodology
pages and the calculator — whose contracts live in `config.py` because there is no
YAML entry to hold them. Same ten fields, same gate. No claim in any entry was
altered; descriptions were derived from each entry's own summary or definition.

The gate now also refuses an **ungoverned built route**: a page the project
publishes and has never said anything about.

## 3. Query map, and the cannibalisation it exposed

One primary query per indexable page, enforced — two pages claiming one query is
one page's traffic split against itself. The audit found a real collision the
project had built into its own ontology: **an award has two pages here.** The
anatomy answers "how is this award built?"; the recognition-system entry answers
"how legitimate is it?" Both are legitimate pages; both were targeting the award's
name.

Resolved by differentiating intent rather than merging pages:

| Entity | Anatomy (`/awards/…`) | System (`/recognition-systems/…`) |
| --- | --- | --- |
| Turing Award | `Turing Award` | `Turing Award legitimacy` |
| Fields Medal | `Fields Medal` | `Fields Medal legitimacy` |
| Wolf Prize | `Wolf Prize` | `Wolf Prize legitimacy` |

The two are now paired explicitly in `AWARD_SYSTEM_PAIRS` and link to each other
with anchors that say which question the other page answers — a link that was
missing in both directions before this audit, for all six awards.

## 4. Hub architecture

**`/sectors/mathematics-computing` is published.** It was the single largest gap
in the site: the domain under active work had no page from which a reader or a
crawler could reach Noether, Liskov, Spärck Jones, Conway or Wiles, the Fields,
Turing and Wolf anatomies, the three scored systems, or the subfield-coverage
finding.

It is published as an **open** reference, not a finished one. The page states
`Status: open cycle`, its Definition-of-Done table reports `DDI cases 5/10 — not
yet` and `synthesis none — not yet`, and its structured data now carries the
measured maturity rather than a hardcoded string. A page does not need to be
finished to be a good reference; it needs to not claim to be finished.

One correction went with it: the sector template emitted
`"creativeWorkStatus": "Cycle 01 — open"` on **every** sector page, including two
closed ones. It is now the domain's measured maturity label. That is structured
data that did not match the page — the exact failure this audit exists to catch.

The engine's own sentence about subfield counts is now rendered on the page
verbatim, so the boundary question is visible where the counts are.

## 5. Internal graph

The audit's strongest finding came from checking declared links against the
**built HTML** rather than against other declarations. 90 declared links did not
exist as links. The semantic graph the project reasons with was not the graph the
site actually rendered.

Now built from the data, with descriptive anchors:

- **person → mechanism**, one link per evidenced pattern, naming the mechanism;
- **person → award anatomy**, for every award whose record documents that case;
- **person → sector**, and **person → methodology**;
- **concept → every case that evidences it**;
- **recognition system ↔ award anatomy**, both directions;
- **report → the corpus it derives from**;
- **hub → hub**, with an anchor that says what is on the other end.

No "read more" anywhere: a crawler and a reader both learn from anchor text.

A related finding: `/rankings` linked to every case with **absolute** URLs while
the rest of the site used site paths. Internal links, canonicals and the sitemap
now use one spelling. A canonical is a strong hint rather than a command, so the
hint only works when every other signal agrees with it — the gate now checks that
the built page's canonical matches the declared path.

## 6. Search presentation

Titles, descriptions, H1s, robots directives and breadcrumbs are rendered from the
contract on every governed route. The H1 rule is that the heading must name the
entity the query asks for — the thesis belongs in a subheading, never in place of
the name. Breadcrumbs render as both a visible trail and exactly one
`BreadcrumbList` per page: `Home → Awards → Physics & Astronomy → Nobel Prize in
Physics`. The domain rung appears only where it resolves.

Structured data is declared per page and **checked in both directions** against
the built HTML: a contract cannot promise a type the page lacks, and a page cannot
emit a type no contract declared. `FAQPage` is absent from the allowed list
because no page here has an FAQ.

## 7. Indexability

`/calculator` is the only `noindex` route — a tool, not a reference, and it should
not compete with the methodology page it implements. It is now excluded from the
sitemap, because a sitemap entry and a noindex directive contradict each other.

## 8. Post-build QA — 63/63

| Check | Result |
| --- | --- |
| Routes built | 63 |
| Missing title / description / canonical / OG / viewport | 0 / 0 / 0 / 0 / 0 |
| Invalid JSON-LD blocks | 0 |
| Broken internal links | 0 |
| Duplicate titles | 0 |
| Duplicate canonicals | 0 |
| Orphan pages | 0 |
| Indexable routes missing from the sitemap | 0 |
| `noindex` routes present in the sitemap | 0 |
| BreadcrumbList coverage | 62 / 63 (the site root has no trail) |
| Horizontal overflow at 390px | 0 / 63 |
| External CSS / JS / font hosts | 0 |
| Content requiring JavaScript | none — every figure is server-built |

A methodological note on that last row: the 390px sweep now runs over HTTP with
the stylesheet actually loaded. Earlier checks in this cycle ran over `file://`,
where the page's absolute stylesheet path does not resolve, so they were testing
unstyled HTML. No page was ever broken; the check was.

## 9. Audit ledger

| Route(s) | Issue | Disposition | Changed? | Reason |
| --- | --- | --- | --- | --- |
| all 41 entry routes | no presentation contract | migrated into the contract | changed (presentation) | a page's identity should not depend on whoever writes the next one |
| 16 generated routes | no contract, no data home | contracts in `config.py` | changed (presentation) | hubs and sector pages are pages too |
| `/sectors/mathematics-computing` | did not exist | published as an open reference | added | the active domain had no hub; maturity is stated, not implied |
| all 3 sector routes | `creativeWorkStatus` hardcoded to "Cycle 01 — open" | driven by measured maturity | changed | structured data must match the page |
| `/awards/*` ↔ `/recognition-systems/*` | same primary query; no links between them | queries differentiated, links added both ways | changed | two pages, two questions |
| `/rankings` | absolute internal URLs | site paths | changed | all signals point at one spelling |
| `/calculator` | indexable, in the sitemap | `noindex`, out of the sitemap | changed | a tool should not compete with the reference |
| all person routes | no links to mechanisms, awards or sector | graph built from the data | changed | the reasoning graph and the rendered graph must be the same graph |
| all concept routes | no links to the cases evidencing them | reciprocal links added | changed | a mechanism page with no cases is a definition, not a reference |
| `/` | no BreadcrumbList | left as is | unchanged | the root is the root; a one-item trail is noise |
| `/unawarded` URL | now labelled The Recognition Archive | left as is | unchanged | stable URLs; `unawarded` survives as a corpus subset |
| Wolf system entry | unevidenced Nobel-precursor claim | withdrawn, score lowered 82→76 | changed (evidence) | committed separately, before this audit |
| every entry's claims | — | untouched | unchanged | this audit governs presentation only |

## What was deliberately not done

No page was created for a keyword. No thin page was published to occupy a query.
The one page added is the hub for the domain with the most active evidence, and it
carries the full corpus, subfield coverage, gap distribution, three system
profiles, three award anatomies, the case matrix and the measured maturity.

## Next: production verification

The audit ends at the built artefact. The remaining step is external and cannot be
run from here: submit the sitemap in Search Console, inspect one URL from each
template family, and confirm the Google-selected canonical and the structured-data
parsing match what the build declares. Then Stage 2.
