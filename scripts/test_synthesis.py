"""Machine checks for the synthesis layer. Run:  python scripts/test_synthesis.py

A synthesis is where a project is most tempted to let the model outrun the
evidence, so the rules that keep it honest are tested rather than trusted:
figures must come from the engine, observations must cite figures, hypotheses
must be refutable, and a hand-typed statistic must fail the build.
"""
from __future__ import annotations

import yaml

from config import DATA
import synthesis_figures as sf
from validate_content import load_yaml_file, validate_report

DOMAIN = "physics-astronomy"
failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(("PASS" if condition else "FAIL") + f"  {name}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


figures = sf.figure_map(DOMAIN)

# 1. The token vocabulary is the engine's, and it is deterministic.
check("figure map is deterministic", sf.figure_map(DOMAIN) == figures)
check("figure map carries no build timestamp",
      "generated_at" not in figures and all("T" not in v for v in figures.values()))

# 2. Bare numbers are rejected; years are not.
check("a typed statistic is caught", sf.bare_numbers("8 of 10 cases") == ["8", "10"])
check("a date is not a statistic", sf.bare_numbers("the 1957 award, the 1930s, audited 2026-09-10") == [])
check("a version identifier is not a statistic", sf.bare_numbers("DDI v1.0 under DoD v1.1") == [])
check("a version-like statistic is still caught", sf.bare_numbers("3 of 8 cases") == ["3", "8"])
check("a resolved token is not a typed number", sf.bare_numbers("{n_cases} cases") == [])
check("an unknown token is caught", sf.unknown_tokens("{no_such_figure}", figures) == ["no_such_figure"])
check("a known token resolves", sf.resolve("{n_cases}", figures) == figures["n_cases"])

# 3. Every published report obeys the rules (and validate_report actually bites).
report_files = sorted((DATA / "reports").glob("*.yaml")) if (DATA / "reports").exists() else []
check("at least one synthesis report exists", bool(report_files))
check("a cross-domain token resolves to the other corpus's figure",
      sf.figure_map(DOMAIN, ("biology-medicine",)).get("n_cases@biology-medicine")
      == sf.figure_map("biology-medicine")["n_cases"])
check("an undeclared cross-domain token does not resolve",
      "n_cases@biology-medicine" not in sf.figure_map(DOMAIN))
for path in report_files:
    item = load_yaml_file(path)
    check(f"report validates ({path.name})", not validate_report("reports", item, path.name),
          str(validate_report("reports", item, path.name)))
    from config import DOMAINS
    check(f"report declares a governed corpus ({path.name})", item.get("derives_from") in DOMAINS)
    check(f"report's compares_with names governed domains ({path.name})",
          all(d in DOMAINS for d in item.get("compares_with") or []))
    _figs = sf.figure_map(item["derives_from"], tuple(item.get("compares_with") or ()))
    for index, obs in enumerate(item.get("observations") or [], start=1):
        check(f"observation #{index} resolves every token ({path.name})",
              not sf.unknown_tokens(obs["statement"], _figs),
              str(sf.unknown_tokens(obs["statement"], _figs)))
    for index, obs in enumerate(item.get("observations") or [], start=1):
        cited = set(sf.cited_tokens(obs["statement"]))
        declared = set(obs.get("derived_from") or [])
        check(f"observation #{index} declares every figure it cites ({path.name})",
              cited <= declared, f"undeclared: {sorted(cited - declared)}")
    for index, hyp in enumerate(item.get("hypotheses") or [], start=1):
        check(f"hypothesis #{index} says what would refute it ({path.name})", bool(hyp.get("refuted_by")))

# 4. The gate bites: a report that types a figure, or invents one, must fail.
sample = load_yaml_file(report_files[0]) if report_files else {}
bad_typed = {**sample, "observations": [{"statement": "8 of 10 cases show it.", "derived_from": ["n_cases"]}]}
check("a hand-typed statistic fails validation", bool(validate_report("reports", bad_typed, "sample.yaml")))
bad_token = {**sample, "observations": [{"statement": "{invented_figure} cases.", "derived_from": ["n_cases"]}]}
check("an invented figure fails validation", bool(validate_report("reports", bad_token, "sample.yaml")))
bad_hyp = {**sample, "hypotheses": [{"statement": "Something is true.", "basis": "because"}]}
check("a hypothesis without a refutation fails validation", bool(validate_report("reports", bad_hyp, "sample.yaml")))
no_corpus = {k: v for k, v in sample.items() if k != "derives_from"}
check("a report without a declared corpus fails validation", bool(validate_report("reports", no_corpus, "sample.yaml")))

# 5. Mechanism audits: a case is accounted for by evidence or by a dated audit,
#    the audit's finding must agree with the case's tags, and the gate must bite.
from validate_content import validate_mechanism_audit
import domain_comparison as dc

_concepts = {p.stem for p in (DATA / "concepts").glob("*.yaml")}
_cases = dc._domain_cases(DOMAIN)
_patterns = dc.pattern_distribution(DOMAIN)
_with_audit = [c for c in _cases if isinstance(c.get("mechanism_audit"), dict)]
check("every mechanism audit validates",
      not [e for c in _with_audit for e in validate_mechanism_audit("unawarded", c, c["slug"], _concepts)])
check("audit findings agree with the case's tags",
      all((c["mechanism_audit"]["finding"] == "mechanism-evidenced") == bool(c.get("patterns"))
          for c in _with_audit))
check("accounting counts evidenced cases plus audited ones, without double counting",
      _patterns["n_cases_accounted"] <= _patterns["denominator"]
      and _patterns["n_cases_accounted"] == _patterns["denominator"] - len(_patterns["cases_unaudited"]))
check("a case with no evidenced mechanism is recorded as audited or unaudited",
      all("audited" in row for row in _patterns["cases_without_evidenced_pattern"]))

_audit_sample = dict(_with_audit[0]) if _with_audit else {}
_contradiction = {**_audit_sample,
                  "mechanism_audit": {**_audit_sample.get("mechanism_audit", {}), "finding": "no-mechanism-evidenced"},
                  "patterns": ["credit-misattribution"], "pattern_evidence": {"credit-misattribution": [1]}}
check("an audit contradicting the case's tags fails validation",
      bool(validate_mechanism_audit("unawarded", _contradiction, "sample.yaml", _concepts)))
_undated = {**_audit_sample, "mechanism_audit": {k: v for k, v in _audit_sample.get("mechanism_audit", {}).items()
                                                 if k != "search_date"}}
check("an undated audit fails validation",
      bool(validate_mechanism_audit("unawarded", _undated, "sample.yaml", _concepts)))

# 6. Observations may not smuggle in universals the engine never computed.
_universal = {**sample, "observations": [{"statement": "Every one of {n_cases} cases shows it.",
                                          "derived_from": ["n_cases"]}]}
check("a universal claim in an observation fails validation",
      bool(validate_report("reports", _universal, "sample.yaml")))

# 7. A refuted hypothesis must record what refuted it, and stays published.
for path in report_files:
    item = load_yaml_file(path)
    for index, hyp in enumerate(item.get("hypotheses") or [], start=1):
        if hyp.get("state") == "refuted":
            check(f"refuted hypothesis #{index} records its outcome ({path.name})", bool(hyp.get("outcome")))
_no_outcome = {**sample, "hypotheses": [{"statement": "x", "basis": "y", "refuted_by": "z", "state": "refuted"}]}
check("a refuted hypothesis without an outcome fails validation",
      bool(validate_report("reports", _no_outcome, "sample.yaml")))

# 8. Temporal validity: a rule may not be applied to an event that predates it.
from config import TIME_DEPENDENT_INTERACTIONS
from validate_content import validate_temporal_validity

_ok_relation = {"corpus_relations": [{
    "case": "x", "interaction_type": "posthumous-constraint", "claim": "c", "record_anchor": [1],
    "rule_at_time": {"event_date": 2016, "effective_from": 1974, "rule_in_force": "in force",
                     "record_anchor": [1]},
}], "sources": [{"type": "institutional"}]}
check("a correctly dated rule passes", not validate_temporal_validity("awards", _ok_relation, "s.yaml"))

_anachronism = {"corpus_relations": [{
    "case": "x", "interaction_type": "posthumous-constraint", "claim": "c", "record_anchor": [1],
    "rule_at_time": {"event_date": 1962, "effective_from": 1974, "rule_in_force": "later rule",
                     "record_anchor": [1]},
}], "sources": [{"type": "institutional"}]}
check("applying a 1974 rule to a 1962 event fails validation",
      bool(validate_temporal_validity("awards", _anachronism, "s.yaml")))

_undated = {"corpus_relations": [{
    "case": "x", "interaction_type": "posthumous-constraint", "claim": "c", "record_anchor": [1],
}], "sources": [{"type": "institutional"}]}
check("a time-dependent relation with no rule_at_time fails validation",
      bool(validate_temporal_validity("awards", _undated, "s.yaml")))

_not_time_dependent = {"corpus_relations": [{
    "case": "x", "interaction_type": "documented-award-outcome", "claim": "c", "record_anchor": [1],
}], "sources": [{"type": "institutional"}]}
check("an ordinary documented outcome needs no rule_at_time",
      not validate_temporal_validity("awards", _not_time_dependent, "s.yaml"))

_secondary_anchor = {"corpus_relations": [{
    "case": "x", "interaction_type": "sharing-constraint", "claim": "c", "record_anchor": [1],
    "rule_at_time": {"event_date": 1962, "rule_in_force": "r", "record_anchor": [1]},
}], "sources": [{"type": "general-secondary"}]}
check("a rule dated only by a secondary source fails validation",
      bool(validate_temporal_validity("awards", _secondary_anchor, "s.yaml")))

_ledger = DATA.parent.parent / "docs" / "cycle-02-requalification-ledger.md"
check("the requalification ledger exists", _ledger.is_file())

# 9. Explanatory coverage: alignment is not an explanatory failure.
from config import AUDIT_ELIGIBLE_CONCEPT_TYPES, UNDER_RECOGNITION_MIN_GAP, is_under_recognized
from domain_status import dod_rows
from validate_content import (
    collect_concept_slugs_by_type,
    collect_published_slugs,
    validate_mechanism_audit as _vma,
    validate_patterns,
)

_cov = dc.explanatory_coverage(DOMAIN)
_corpus = dc.corpus_distribution(DOMAIN)
check("coverage bands account for every case",
      sum(r["cases"] for r in _cov["by_band"]) == _corpus["n_cases"])
check("every band's rows split into mechanism / no mechanism",
      all(r["with_mechanism"] + r["without_mechanism"] == r["cases"] for r in _cov["by_band"]))
check("unexplained under-recognition counts only cases above the published band floor",
      all(is_under_recognized(c["gap"]) for c in _cov["unexplained_under_recognition"]))
check("aligned cases are never counted as unexplained",
      all(not is_under_recognized(c["gap"]) for c in _cov["aligned_without_mechanism"]))
check("unexplained under-recognition never exceeds the under-recognized population",
      _cov["n_unexplained_under_recognition"] <= _cov["n_under_recognized"] <= _cov["n_cases"])
check("the band floor comes from the published gap bands, not a second number",
      _cov["under_recognition_threshold"] == UNDER_RECOGNITION_MIN_GAP
      and dc.recognition_gap_label(UNDER_RECOGNITION_MIN_GAP) == "under-recognized"
      and dc.recognition_gap_label(UNDER_RECOGNITION_MIN_GAP - 1) == "recognition roughly matches assessed merit")

# 10. Only audit-eligible concepts may be tested against a case.
_mech = collect_concept_slugs_by_type(AUDIT_ELIGIBLE_CONCEPT_TYPES)
_all_concepts = collect_published_slugs("concepts")
check("audit-eligible concepts are a strict subset of published concepts",
      bool(_mech) and _mech < _all_concepts,
      f"{len(_mech)} eligible of {len(_all_concepts)} published")
check("the engine's eligible list matches the validator's",
      set(dc.audit_eligible_concepts()) == _mech)
check("the engine counts ontology coverage against eligible concepts only",
      _cov["n_eligible_concepts"] == len(_mech))
_framework = {"merit-vs-recognition"}
_bad_audit = {"sources": [{"type": "institutional"}], "patterns": ["credit-misattribution"],
              "mechanism_audit": {"search_date": "2026-09-11", "considered": ["merit-vs-recognition"],
                                  "finding": "mechanism-evidenced", "note": "x"}}
check("a framework concept cannot be a considered mechanism",
      bool(_vma("unawarded", _bad_audit, "s.yaml", _mech)))
_bad_pattern = {"patterns": ["merit-vs-recognition"], "sources": [{"type": "institutional"}]}
check("a framework concept cannot be declared as a case pattern",
      bool(validate_patterns("unawarded", _bad_pattern, "s.yaml", _framework | _mech, _mech)))

# 11. Composite domains: coverage is measured, and gates nothing.
from config import DOMAIN_SUBFIELDS, is_composite_domain
from validate_content import validate_subfield

for _domain in DOMAIN_SUBFIELDS:
    _sc = dc.subfield_coverage(_domain)
    check(f"composite domain reports coverage ({_domain})", _sc["composite"] and bool(_sc["rows"]))
    check(f"every case is assigned to a subfield ({_domain})", _sc["cases_unassigned"] == 0)
    check(f"subfield case counts sum to the corpus ({_domain})",
          sum(r["cases"] for r in _sc["rows"]) == _sc["n_cases"])
    check(f"coverage is not a maturity criterion ({_domain})",
          not any("subfield" in str(row["requirement"]) for row in dod_rows(_domain)))
check("a non-composite domain reports no subfield coverage",
      not dc.subfield_coverage("physics-astronomy")["composite"])
check("an entry in a composite domain without a subfield fails validation",
      bool(validate_subfield("unawarded", {"domain": "mathematics-computing"}, "s.yaml")))
check("an unknown subfield fails validation",
      bool(validate_subfield("unawarded", {"domain": "mathematics-computing", "subfield": "physics"}, "s.yaml")))
check("a subfield on a non-composite domain fails validation",
      bool(validate_subfield("unawarded", {"domain": "physics-astronomy", "subfield": "mathematics"}, "s.yaml")))

print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
raise SystemExit(1 if failures else 0)
