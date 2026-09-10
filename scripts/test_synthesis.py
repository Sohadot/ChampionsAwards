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
check("a resolved token is not a typed number", sf.bare_numbers("{n_cases} cases") == [])
check("an unknown token is caught", sf.unknown_tokens("{no_such_figure}", figures) == ["no_such_figure"])
check("a known token resolves", sf.resolve("{n_cases}", figures) == figures["n_cases"])

# 3. Every published report obeys the rules (and validate_report actually bites).
report_files = sorted((DATA / "reports").glob("*.yaml")) if (DATA / "reports").exists() else []
check("at least one synthesis report exists", bool(report_files))
for path in report_files:
    item = load_yaml_file(path)
    check(f"report validates ({path.name})", not validate_report("reports", item, path.name),
          str(validate_report("reports", item, path.name)))
    check(f"report declares its corpus ({path.name})", item.get("derives_from") == DOMAIN)
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

print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
raise SystemExit(1 if failures else 0)
