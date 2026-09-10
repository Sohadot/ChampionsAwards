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
check("a year is not a statistic", sf.bare_numbers("the 1957 award and the 1930s") == [])
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

print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
raise SystemExit(1 if failures else 0)
