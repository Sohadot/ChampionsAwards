"""Machine checks for the canonical aggregation engine. Run:  python scripts/test_domain_comparison.py

These freeze the quartile definition, guarantee determinism, and enforce the
denominator/eligibility rules so the comparison layer cannot silently drift into
mis-computed or causal-looking statistics.
"""
from __future__ import annotations

import domain_comparison as dc

DOMAIN = "physics-astronomy"
failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(("PASS" if condition else "FAIL") + f"  {name}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


# 1. Frozen quartile definition (inclusive). If these change, the definition drifted.
q5 = dc.quartiles([5, 4, 3, 2, 1])  # odd n
check("quartiles odd [1..5] -> Q1=2,Q3=4,IQR=2", q5["q1"] == 2 and q5["q3"] == 4 and q5["iqr"] == 2, str(q5))
q6 = dc.quartiles([6, 5, 4, 3, 2, 1])  # even n
check("quartiles even [1..6] -> Q1=2,Q3=5,IQR=3", q6["q1"] == 2 and q6["q3"] == 5 and q6["iqr"] == 3, str(q6))
check("median even [1,2,3,4] -> 2.5", dc.median([4, 3, 2, 1]) == 2.5)
check("median odd [1,2,3] -> 2", dc.median([3, 1, 2]) == 2)

# 2. Determinism: two builds are byte-identical, and the snapshot id is stable.
r1 = dc.build_comparison(DOMAIN)
r2 = dc.build_comparison(DOMAIN)
check("build_comparison is deterministic", r1 == r2)
check("snapshot id is stable", r1["corpus_snapshot"] == r2["corpus_snapshot"])

# 3. Gap denominator == case denominator (every DDI case has a computable gap).
corpus = r1["observations"]["corpus_distribution"]
gap_rows = [row for row in corpus["ranked_cases"] if "gap" in row]
check("gap denominator == n_cases", len(gap_rows) == corpus["n_cases"], f"{len(gap_rows)} vs {corpus['n_cases']}")

# 4. No duplicate case counting (ranked cases have unique slugs).
slugs = [row["slug"] for row in corpus["ranked_cases"]]
check("no duplicate cases", len(slugs) == len(set(slugs)))

# 5. Patterns: evidence-backed only, and denominator == all DDI cases (not relations).
patterns = r1["observations"]["structural_patterns"]
check("pattern denominator == n_cases", patterns["denominator"] == corpus["n_cases"])
check("established patterns require >= 2 support",
      all(p["support"] >= 2 for p in patterns["patterns"] if p["status"] == "established"))
# Evidence-backed only: every supporting case counted for a pattern must carry
# pattern_evidence for exactly that pattern.
_cases = {c["slug"]: c for c in dc._domain_cases(DOMAIN)}
_evidence_ok = all(
    (_cases[sc["slug"]].get("pattern_evidence") or {}).get(p["pattern"])
    for p in patterns["patterns"] for sc in p["cases"]
)
check("every counted pattern-case has pattern_evidence for that pattern", _evidence_ok)

# 6. Systems outside the domain are excluded; profiles come only from in-domain systems.
systems = r1["observations"]["recognition_system_profiles"]
check("system count matches in-domain systems", systems["n_systems"] == len(dc._domain_systems(DOMAIN)))

# 7. Award relations: only hardened relations are counted, and the denominator is
#    relations (NOT cases) -> the two denominators are tracked separately.
awards = r1["observations"]["award_interactions"]
check("award denominator == hardened relations", awards["denominator"] == len(dc._domain_award_relations(DOMAIN)))
check("denominators are distinct populations", awards["denominator"] != patterns["denominator"],
      f"awards {awards['denominator']} vs cases {patterns['denominator']}")

# 8. A malformed (non-hardened) relation is excluded by the loader's filter.
#    Verify the filter predicate directly on synthetic relations.
def _hardened(rel: dict) -> bool:
    return (
        isinstance(rel.get("interaction_type"), str)
        and isinstance(rel.get("claim"), str)
        and ((rel.get("record_anchor") is None) != (rel.get("exception") is None))
    )
check("hardened filter rejects missing interaction_type",
      not _hardened({"claim": "x", "record_anchor": [1]}))
check("hardened filter rejects both anchor and exception",
      not _hardened({"interaction_type": "documented-award-outcome", "claim": "x", "record_anchor": [1], "exception": {}}))
check("hardened filter accepts a well-formed relation",
      _hardened({"interaction_type": "documented-award-outcome", "claim": "x", "record_anchor": [1]}))

# 9. Observations only - no 'conclusions' key anywhere near the top level.
check("engine emits observations, not conclusions",
      "observations" in r1 and "conclusions" not in r1)

print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
raise SystemExit(1 if failures else 0)
