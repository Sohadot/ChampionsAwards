# Cycle 02 — Baseline Requalification Ledger

Round: **Baseline Requalification & Temporal-Rule Audit**, 2026-09-11.
No individuals were added. The three inherited Biology & Medicine cases and the
Lasker Award entry were re-qualified against DoD v1.1 and the claim-level
authority standard that Cycle 01 produced.

Corpus snapshots: biology-medicine `5373f06112a4`, data through 2026-09-11.

The rule this round added to the method:

> **Temporal validity is part of provenance.** An official source for today's
> rule is not evidence about a decision taken before that rule existed. Where a
> rule is tied to a historical event, the record must show which version was
> then in force.

---

## 1. Claims corrected

| Claim | Was | Now |
| --- | --- | --- |
| Franklin — why the 1962 award could not include her | "The institution could not have recognized her in 1962 even in principle" (the Nobel prohibition on posthumous awards) | The prohibition entered the Statutes in **1974**, twelve years after the decision, and two prizes had been awarded posthumously before then (1931, 1961). No rule is applied to the 1962 outcome; the version governing a candidate who died in 1958 was not reached by this audit. |
| Posthumous Recognition (concept) | Stated the Nobel rule with no date, as if timeless | States the rule **and** the date it entered the Statutes, with the anachronism warning attached |
| Nobel Prize in Physics — Rubin relation | Applied the posthumous rule to a 2016 death with no temporal anchor | Carries `rule_at_time`: event 2016, rule effective from 1974, anchored to the Statutes and the Foundation's facts page |

## 2. Claims withdrawn

| Claim | Entry | Why |
| --- | --- | --- |
| "A scientific community not yet primed to interpret his statistical approach"; "his position outside major research institutions" | Mendel | Historiographical hypotheses asserted as fact. Nothing in the record distinguishes them from the bare fact of the delay. |
| "The conservatism of prize deliberations"; "disciplinary framing"; "the prize's own conservatism can act as a filter" | Avery | Causal claims about the Nobel process. Committee evaluations are not published and the Physiology or Medicine nomination archive is open only through 1953, so no available record establishes a reason. |
| "The informal circulation of her data" as a structural cause; the rule-based explanation of 1962 | Franklin | The first is contested by a 2023 archive-based reassessment; the second is the anachronism corrected above. |
| "Selections concentrate recognition within well-resourced research centres" | Lasker Award | No record-grade source. Tabulating recipients ourselves would be our own analysis presented as a documented fact. |
| Predictive-overlap figure used to justify the track-record score | Lasker Award | The foundation publishes no overall count of laureates who later received the Nobel. Now a documented exception. |

## 3. Claims strengthened

| Claim | Entry | New anchor |
| --- | --- | --- |
| Contribution | Mendel | The 1866 paper itself — *Versuche ueber Pflanzen-Hybriden*, Verhandlungen des naturforschenden Vereines in Bruenn IV, 3–47 (primary) |
| Independent confirmation | Mendel | NHGRI record of the 1900 rediscovery by de Vries, Correns and von Tschermak |
| Contribution | Avery | The 1944 paper in the Journal of Experimental Medicine 79(2): 137–158 (primary) |
| Observed recognition | Avery | The Nobel nomination archive: **38 nominations** — 37 for Physiology or Medicine, 1932–1953, plus one for Chemistry in 1957, two years after his death (institutional, record-grade) |
| Contribution | Franklin | Franklin & Gosling, *Nature* 171: 740–741 (1953) (primary), with Watson & Crick, *Nature* 171: 737–738, cited alongside |
| The 1974 rule change | Franklin, and the concept | The Nobel Foundation's own facts page |
| Archive coverage limit | Franklin, Avery | The Nobel nomination archive's own statement that Physiology or Medicine data is published only through 1953 |
| System facts | Lasker Award | The foundation's own about-the-awards page: created 1945, annual nomination window, selection by an international jury |

## 4. Claims confirmed unchanged

- Avery's DDI dimension scores and `observed_recognition` — the new evidence documents the non-award more precisely without changing how much recognition he received.
- Franklin's `attribution` score (55) — justification narrowed to what the documents show; the score itself survives the narrowing.
- Lasker's five RLS dimension scores — see §7.
- Mendel's impact, uniqueness, durability, breadth and attribution scores.

## 5. Mechanisms evidenced

| Case | Mechanism | Basis |
| --- | --- | --- |
| Mendel | delayed-recognition (**emergent**) | The interval itself: publication 1866, independent rediscovery 1900, no rival claimant. The *causes* are withdrawn. |
| Franklin | credit-misattribution (**emergent**) | The documentary relationship between the three 1953 *Nature* papers and the 1962 award — recorded as contested, since the 2023 reassessment argues she was an equal member of the group rather than its victim. |

## 6. Mechanisms explicitly unexplained

| Case | Finding | What the record shows instead |
| --- | --- | --- |
| Avery | `no-mechanism-evidenced` | 38 nominations across two decades with no award, and no published reason for any decision. Delayed recognition was withdrawn: no prize acknowledgment ever arrived, and scientific credit was never in dispute, so the record shows sustained non-award rather than delayed recognition. |

Withdrawn from Franklin: `posthumous-recognition`. The mechanism turns on eligibility
rules determining whether a contribution can be honoured; with the 1974 anachronism
removed, that element is not evidenced for 1962.

## 7. Scores changed and unchanged

| Entry | Field | Was | Now | Rationale |
| --- | --- | --- | --- | --- |
| Mendel | verification | 85 | **90** | Contribution anchored to the primary paper, and three botanists independently rediscovered the same principles in 1900 — independent confirmation of an unusually direct kind. |
| Mendel | observed_recognition | 40 | **65** | He received nothing in his lifetime, but posthumous recognition is close to total: the laws and the field carry his name. Calibrated against comparable eponymous-but-unawarded cases in this corpus. |
| Mendel | DDI / gap | 84 / 44 | **85 / 20** | Consequence of the two changes above. |
| Franklin | observed_recognition | 40 | **58** | The earlier figure did not account for documented posthumous recognition, including a Royal Society award carrying her name — against no prize in her lifetime and no share of the 1962 award. |
| Franklin | DDI / gap | 82 / 42 | **82 / 24** | DDI unchanged; the gap narrows because observed recognition was corrected. |
| Avery | DDI / gap | 79 / 29 | **79 / 29** | Unchanged. |
| Lasker | breadth | 60 | **60** | Score unchanged, justification narrowed: the biomedical-only remit is documented; the recipient-distribution claim is withdrawn and replaced by a documented exception. |
| Lasker | track_record | 88 | **88** | Score unchanged, justification narrowed: rests on the published recipient record rather than an unanchored predictive statistic. |

## 8. Baseline effect

| Measure | Before | After |
| --- | --- | --- |
| DDI cases | 3 | 3 |
| Median gap | 42 | **24** |
| Source-grade closure | 2/6 entries | **6/6** |
| Mechanism accounting | 3/3 (no audits) | **3/3, all audited** |
| Evidenced mechanisms | 3 | **2** |
| Established mechanisms | 1 | **0** |
| Cases unexplained after audit | 0 (none audited) | **1/3 (Avery)** |
| Sources on the three cases | 4 | **15** |

The baseline is smaller, its gaps are narrower, and it now evidences no
established mechanism at all. Under DoD v1.1 none of that blocks the cycle: the
established count is reported and gates nothing, and mechanism accounting — the
criterion that does gate — is complete. This is the round working as intended.
An inherited corpus is not automatically compliant with the standard that
superseded it.
