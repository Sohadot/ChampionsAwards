"""Machine checks for the synthesis layer. Run:  python scripts/test_synthesis.py

A synthesis is where a project is most tempted to let the model outrun the
evidence, so the rules that keep it honest are tested rather than trusted:
figures must come from the engine, observations must cite figures, hypotheses
must be refutable, and a hand-typed statistic must fail the build.
"""
from __future__ import annotations

import pathlib
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
    from config import AGGREGATED_DOMAINS
    check(f"report declares a governed corpus ({path.name})",
          item.get("derives_from") in AGGREGATED_DOMAINS)
    check(f"report's compares_with names governed domains ({path.name})",
          all(d in AGGREGATED_DOMAINS for d in item.get("compares_with") or []))
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

# 12. Award anatomy: who decides and who pays are separate, enforced fields.
from config import AWARD_ARCHITECTURE_KEYS, FUNDING_SEPARATION_REQUIRED
from validate_content import validate_architecture

_decides, _pays = FUNDING_SEPARATION_REQUIRED
check("funding is a first-class architecture field", _pays in AWARD_ARCHITECTURE_KEYS)
check("an anatomy that names the granting body without the funder fails validation",
      bool(validate_architecture("awards", {"architecture": {_decides: "A society."}}, "a.yaml")))
check("naming both passes",
      not validate_architecture(
          "awards", {"architecture": {_decides: "A society.", _pays: "A company."}}, "a.yaml"))
check("an anatomy may state the funder without the granting body",
      not validate_architecture("awards", {"architecture": {_pays: "A company."}}, "a.yaml"))

_award_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "data" / "awards"
_anatomies = [yaml.safe_load(f.read_text(encoding="utf-8")) for f in sorted(_award_dir.glob("*.yaml"))]
_with_arch = [a for a in _anatomies if isinstance(a.get("architecture"), dict) and a["architecture"]]
check("every published anatomy separates governance from funding",
      bool(_with_arch) and all(_pays in a["architecture"] for a in _with_arch))

# 13. The SEO contract: presentation is governed as data, not by memory.
from config import (
    CLUSTERS, SEO_BRAND_SUFFIX, SEO_CONTRACT_CLUSTERS, SEO_CONTRACT_FIELDS,
    SEO_DESCRIPTION_MAX, SEO_REQUIRED_SCHEMA_TYPES, is_canonical_path,
)
from validate_content import validate_seo

_good = {
    "primary_query": "Wolf Prize",
    "secondary_entities": ["Wolf Foundation"],
    "title": "Wolf Prize - Selection" + SEO_BRAND_SUFFIX,
    "description": "x" * 120,
    "canonical": "/awards/wolf-prize-award",
    "h1": "Wolf Prize",
    "schema_types": sorted(SEO_REQUIRED_SCHEMA_TYPES),
    "incoming_links": ["/awards"],
    "outgoing_links": ["/unawarded/andrew-wiles"],
    "indexing": "index",
}
_cluster = sorted(SEO_CONTRACT_CLUSTERS)[0]
check("a complete seo contract passes", not validate_seo(_cluster, {"seo": dict(_good)}, "a.yaml"))
check("a governed cluster entry without a contract fails",
      bool(validate_seo(_cluster, {}, "a.yaml")))
_ungoverned = sorted(set(CLUSTERS) - SEO_CONTRACT_CLUSTERS)
check("an ungoverned cluster without a contract passes",
      bool(_ungoverned) and not validate_seo(_ungoverned[0], {}, "c.yaml"))
for _field in SEO_CONTRACT_FIELDS:
    _partial = {k: v for k, v in _good.items() if k != _field}
    check(f"a contract missing '{_field}' fails", bool(validate_seo(_cluster, {"seo": _partial}, "a.yaml")))
check("a title without the brand suffix fails",
      bool(validate_seo(_cluster, {"seo": dict(_good, title="Wolf Prize")}, "a.yaml")))
check("a title that omits the primary query fails",
      bool(validate_seo(_cluster, {"seo": dict(_good, title="An Anatomy" + SEO_BRAND_SUFFIX)}, "a.yaml")))
check("an h1 that omits the primary query fails",
      bool(validate_seo(_cluster, {"seo": dict(_good, h1="An Anatomy of a Recognition Mechanism")}, "a.yaml")))
check("an over-long description fails",
      bool(validate_seo(_cluster, {"seo": dict(_good, description="x" * (SEO_DESCRIPTION_MAX + 1))}, "a.yaml")))
check("a contract without BreadcrumbList fails",
      bool(validate_seo(_cluster, {"seo": dict(_good, schema_types=["Article"])}, "a.yaml")))
check("an unsupported schema type fails",
      bool(validate_seo(_cluster, {"seo": dict(_good, schema_types=["BreadcrumbList", "FAQPage"])}, "a.yaml")))
check("a canonical with .html fails", not is_canonical_path("/awards/wolf.html"))
check("a canonical with a trailing slash fails", not is_canonical_path("/awards/wolf/"))
check("a relative canonical fails", not is_canonical_path("awards/wolf"))
check("an unknown contract field fails",
      bool(validate_seo(_cluster, {"seo": dict(_good, keywords="wolf prize")}, "a.yaml")))

# 14. A multi-field award's relations are counted in the domain of the case.
_award_items = [yaml.safe_load(f.read_text(encoding="utf-8"))
                for f in sorted((pathlib.Path(__file__).resolve().parent.parent
                                 / "src" / "data" / "awards").glob("*.yaml"))]
_multi = [a for a in _award_items if isinstance(a.get("domains"), list) and len(a["domains"]) > 1]
check("a multi-domain award anatomy exists to exercise the rule", bool(_multi))
for _domain in ("physics-astronomy", "biology-medicine", "mathematics-computing"):
    _case_slugs = {c["slug"] for c in dc._domain_cases(_domain)}
    _rels = dc._domain_award_relations(_domain)
    check(f"every counted award relation names a case in the domain ({_domain})",
          all(r["case"] in _case_slugs for r in _rels))
_all_rel_cases = {r["case"] for d in ("physics-astronomy", "biology-medicine", "mathematics-computing")
                  for r in dc._domain_award_relations(d)}
_declared = {rel["case"] for a in _award_items for rel in (a.get("corpus_relations") or [])}
check("no declared award relation is silently dropped from every domain",
      _declared <= _all_rel_cases)

# 15. Recurrence: two observations are not two replications.
from config import (
    PATTERN_ESTABLISHED_MIN as _PMIN, RECURRENCE_CONTEXTS, is_valid_recurrence_context,
    pattern_context_key,
)
from validate_content import validate_pattern_context

check("an undeclared context makes a case its own context",
      pattern_context_key("a-case", None).startswith("case:"))
check("an unknown context is not silently honoured",
      pattern_context_key("a-case", "not-a-context").startswith("case:"))
check("a declared context is used verbatim",
      pattern_context_key("a-case", sorted(RECURRENCE_CONTEXTS)[0]) == sorted(RECURRENCE_CONTEXTS)[0])
check("an unknown context fails validation",
      bool(validate_pattern_context("unawarded",
           {"patterns": ["p"], "pattern_context": {"p": "invented"}}, "s.yaml")))
check("a context for an undeclared pattern fails validation",
      bool(validate_pattern_context("unawarded",
           {"patterns": ["p"], "pattern_context": {"q": sorted(RECURRENCE_CONTEXTS)[0]}}, "s.yaml")))
check("a case declaring no context passes",
      not validate_pattern_context("unawarded", {"patterns": ["p"]}, "s.yaml"))

for _domain in ("physics-astronomy", "biology-medicine", "mathematics-computing"):
    _pats = dc.pattern_distribution(_domain)["patterns"]
    check(f"independent support never exceeds case support ({_domain})",
          all(p["independent_support"] <= p["support"] for p in _pats))
    check(f"status is decided by contexts, not cases ({_domain})",
          all((p["status"] == "established") == (p["independent_support"] >= _PMIN) for p in _pats))
    check(f"every pattern publishes both figures ({_domain})",
          all({"support", "independent_support", "contexts"} <= set(p) for p in _pats))

_mc = {p["pattern"]: p for p in dc.pattern_distribution("mathematics-computing")["patterns"]}
check("a mechanism with several cases in one context stays emergent",
      any(p["support"] >= _PMIN and p["independent_support"] < _PMIN and p["status"] == "emergent"
          for p in _mc.values()),
      str({k: (v["support"], v["independent_support"], v["status"]) for k, v in _mc.items()}))
check("a regime-bounded mechanism is flagged as such",
      any(p["regime_bounded"] for p in _mc.values()))

# 16. Foundation review: legacy drift the closed layers could hide.
_docs = pathlib.Path(__file__).resolve().parent.parent / "docs"
_doc_text = "\n".join(f.read_text(encoding="utf-8") for f in sorted(_docs.glob("*.md")))
check("no document types a moving corpus snapshot",
      "Current snapshot `" not in _doc_text,
      "a snapshot that changes must be read from the engine, not copied into prose")

_concepts_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "data" / "concepts"
_eligible = {
    yaml.safe_load(f.read_text(encoding="utf-8"))["slug"]
    for f in sorted(_concepts_dir.glob("*.yaml"))
    if yaml.safe_load(f.read_text(encoding="utf-8")).get("concept_type") in AUDIT_ELIGIBLE_CONCEPT_TYPES
}
_cases_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "data" / "unawarded"
_audits = [yaml.safe_load(f.read_text(encoding="utf-8")) for f in sorted(_cases_dir.glob("*.yaml"))]
_audits = [c for c in _audits if isinstance(c.get("mechanism_audit"), dict)]
_current = [c for c in _audits
            if _eligible <= set(c["mechanism_audit"].get("considered") or [])]
check("the ontology-currency of every audit is measurable",
      bool(_audits) and all(isinstance(c["mechanism_audit"].get("considered"), list) for c in _audits))
# Reported, never gated: an audit predating a concept is a dated fact, not a defect,
# and back-filling a `considered` list without re-running the audit would fabricate
# evidence. The figure exists so the corpus cannot hide the drift.
print(f"      [reported] audits current against the {len(_eligible)}-concept ontology: "
      f"{len(_current)}/{len(_audits)}")

# 17. Ontology revisions: an audit is only readable against the ontology it ran under.
from config import (
    COMPLETENESS_ENFORCED_FROM, CURRENT_ONTOLOGY_REVISION, LEGACY_REVISION_UNRESOLVED,
    MECHANISM_ACCOUNTING_MEANING, ONTOLOGY_REVISIONS, audit_is_complete_at_revision,
    audit_is_current, is_valid_ontology_revision, revision_is_before, revision_mechanisms,
)
from validate_content import validate_mechanism_audit as _vma

_ids = list(ONTOLOGY_REVISIONS)
check("revision ids are immutable and ordered by commit, not by date",
      _ids == sorted(_ids) and CURRENT_ONTOLOGY_REVISION == _ids[-1])
check("a revision never loses a mechanism",
      all(revision_mechanisms(a) <= revision_mechanisms(b) for a, b in zip(_ids, _ids[1:])))
check("only the revision in force may lack a commit hash",
      all(ONTOLOGY_REVISIONS[i].get("commit") for i in _ids[:-1]),
      "a published revision is anchored in history")
check("an unresolved revision is valid but constrains nothing",
      is_valid_ontology_revision(LEGACY_REVISION_UNRESOLVED)
      and revision_mechanisms(LEGACY_REVISION_UNRESOLVED) == frozenset())
check("an invented revision id is rejected", not is_valid_ontology_revision("MOR-999"))

_mechs = {"credit-misattribution", "delayed-recognition", "institutional-exclusion",
          "posthumous-recognition", "theory-experiment-asymmetry", "institutional-gatekeeping",
          "compulsory-secrecy"}


def _audit(**kw):
    base = {"search_date": "2026-09-12", "considered": sorted(revision_mechanisms("MOR-005")),
            "ontology_revision": CURRENT_ONTOLOGY_REVISION, "revision_basis": "commit deadbee",
            "finding": "no-mechanism-evidenced", "note": "n"}
    base.update(kw)
    return _vma("unawarded", {"mechanism_audit": base}, "s.yaml", _mechs)


check("a complete current audit passes", not _audit())
check("an audit with no recorded revision fails",
      any("ontology_revision" in e for e in _audit(ontology_revision=None)))
check("an audit with no revision evidence fails",
      any("revision_basis" in e for e in _audit(revision_basis="   ")))
check("an undeclared gap at the recorded revision fails",
      bool(_audit(considered=["delayed-recognition"])))
check("a declared gap must name exactly the untested mechanisms",
      bool(_audit(ontology_revision="MOR-003", revision_basis="commit c78250e",
                  considered=["delayed-recognition"],
                  incomplete_at_revision=["posthumous-recognition"])))
check("a legacy audit that declares its gap exactly passes",
      not _audit(ontology_revision="MOR-003", revision_basis="commit c78250e",
                 considered=["delayed-recognition"],
                 incomplete_at_revision=sorted(revision_mechanisms("MOR-003") - {"delayed-recognition"})))
check("a gap cannot be declared in a mechanism that did not yet exist",
      bool(_audit(ontology_revision="MOR-001", revision_basis="commit d6e52a0",
                  considered=sorted(revision_mechanisms("MOR-001")),
                  incomplete_at_revision=["compulsory-secrecy"])))
check("a mechanism cannot be both tested and untested",
      bool(_audit(ontology_revision="MOR-003", revision_basis="commit c78250e",
                  incomplete_at_revision=["delayed-recognition"])))
check(f"the declared-gap escape is closed from {COMPLETENESS_ENFORCED_FROM} onward",
      bool(_audit(considered=["delayed-recognition"],
                  incomplete_at_revision=sorted(revision_mechanisms(CURRENT_ONTOLOGY_REVISION)
                                                - {"delayed-recognition"}))))
check("an unresolved revision cannot declare a gap at that revision",
      bool(_audit(ontology_revision=LEGACY_REVISION_UNRESOLVED,
                  revision_basis="history does not establish one",
                  incomplete_at_revision=["delayed-recognition"])))
check("the completeness boundary is a real boundary",
      revision_is_before(_ids[0], COMPLETENESS_ENFORCED_FROM)
      and not revision_is_before(COMPLETENESS_ENFORCED_FROM, COMPLETENESS_ENFORCED_FROM))

check("every published audit records a revision and its evidence",
      all(is_valid_ontology_revision(c["mechanism_audit"].get("ontology_revision"))
          and str(c["mechanism_audit"].get("revision_basis", "")).strip() for c in _audits))
check("completeness and currency are different measurements",
      audit_is_complete_at_revision(sorted(revision_mechanisms("MOR-003")), "MOR-003")
      and not audit_is_current(sorted(revision_mechanisms("MOR-003"))))
check("the accounting figure does not claim per-mechanism completeness",
      "does not assert" in MECHANISM_ACCOUNTING_MEANING)

# Currency gates nothing: every closed domain stays mature while most of its
# audits predate the current mechanism set. A vocabulary that grows must not be
# able to retroactively unmake a closed layer.
import domain_status as _ds
for _domain in ("physics-astronomy", "biology-medicine", "mathematics-computing"):
    _pd = dc.pattern_distribution(_domain)
    _mature, _pending = _ds.dod_status(_domain)
    check(f"a domain with out-of-date audits stays mature ({_domain})",
          _mature and _pd["n_audits_current"] <= _pd["n_audits"])
    print(f"      [reported] {_domain}: complete at own revision "
          f"{_pd['n_audits_complete_at_revision']}/{_pd['n_audits']}, current against "
          f"{_pd['current_ontology_revision']} {_pd['n_audits_current']}/{_pd['n_audits']}")
check("no Definition of Done criterion reads an audit-revision figure",
      not any(k in str(_ds.dod_rows("biology-medicine"))
              for k in ("complete_at_revision", "n_audits_current", "ontology_revision")))

# 18. Domain registry: lifecycle is a property of the domain, not of a cycle.
from config import (
    AGGREGATED_DOMAINS, DOMAIN_LIFECYCLE_STATES, DOMAIN_REGISTRY, DOMAIN_SCOPED_CLUSTERS,
    DOMAIN_SCOPE_POSTURES, PUBLISHED_SECTORS, domain_state, is_aggregated_domain,
)
from validate_content import validate_domains as _vd

check("every registered domain declares a valid state and a date",
      all(e.get("state") in DOMAIN_LIFECYCLE_STATES and e.get("state_since") and e.get("label")
          for e in DOMAIN_REGISTRY.values()))
check("aggregation is derived from the registry, not typed",
      tuple(PUBLISHED_SECTORS) == AGGREGATED_DOMAINS
      and set(AGGREGATED_DOMAINS) == {d for d in DOMAIN_REGISTRY if domain_state(d) != "planned"})
check("the project has at least one planned domain to be wrong about",
      any(domain_state(d) == "planned" for d in DOMAIN_REGISTRY))

_planned = [d for d in DOMAIN_REGISTRY if domain_state(d) == "planned"]
_case_domains = [c.get("domain") for c in
                 (yaml.safe_load(f.read_text(encoding="utf-8"))
                  for f in sorted(_cases_dir.glob("*.yaml")))]
_systems_dir = pathlib.Path(__file__).resolve().parent.parent / "src" / "data" / "recognition-systems"
_system_domains = [d for f in sorted(_systems_dir.glob("*.yaml"))
                   for d in (yaml.safe_load(f.read_text(encoding="utf-8")).get("domains") or [])]
check("a planned domain carries no assessed case or system",
      not (set(_planned) & (set(_case_domains) | set(_system_domains))))
check("a planned domain publishes no sector hub",
      not any(d in PUBLISHED_SECTORS for d in _planned))
check("a closed domain meets its Definition of Done",
      all(_ds.dod_status(d)[0] for d in DOMAIN_REGISTRY if domain_state(d) == "closed"))

check("an unscoped published entry in a domain-scoped cluster fails",
      bool(_vd("awards", {"status": "published", "title": "t"}, "s.yaml")))
check("naming a planned domain is enough to be scoped",
      not _vd("awards", {"status": "published", "domains": _planned[:1]}, "s.yaml"))
check("a cluster with a declared posture is exempt",
      "concepts" in DOMAIN_SCOPE_POSTURES and "concepts" not in DOMAIN_SCOPED_CLUSTERS
      and not _vd("concepts", {"status": "published", "title": "t"}, "s.yaml"))
check("an unregistered domain is still rejected",
      bool(_vd("awards", {"status": "published", "domain": "chemistry"}, "s.yaml")))
check("a synthesis cannot derive from a domain with no corpus",
      not is_aggregated_domain(_planned[0]))

# 19. Re-audits: a historical defect is remediated, never erased.
from config import MECHANISM_VERDICTS
from validate_content import validate_mechanism_reaudit as _vmr

_reaudited = [c for c in _audits if isinstance(c.get("mechanism_reaudit"), dict)]
_defective = [c for c in _audits if c["mechanism_audit"].get("incomplete_at_revision")]

check("every historical audit defect carries a dated re-audit",
      all(isinstance(c.get("mechanism_reaudit"), dict) for c in _defective),
      ", ".join(c["slug"] for c in _defective if not c.get("mechanism_reaudit")))
check("no original audit was rewritten to look complete",
      all(c["mechanism_audit"].get("incomplete_at_revision") for c in _reaudited),
      "the defect must stay visible in the audit it belongs to")
check("every re-audit tests the whole current ontology",
      all(revision_mechanisms(CURRENT_ONTOLOGY_REVISION)
          <= set(c["mechanism_reaudit"]["considered"]) for c in _reaudited))
check("every re-audit returns a verdict per mechanism considered",
      all(sorted(v["mechanism"] for v in c["mechanism_reaudit"]["verdicts"])
          == sorted(c["mechanism_reaudit"]["considered"]) for c in _reaudited))
check("what a re-audit supports is what its case declares",
      all(sorted(v["mechanism"] for v in c["mechanism_reaudit"]["verdicts"]
                 if v["verdict"] == "supported") == sorted(c.get("patterns") or [])
          for c in _reaudited))
check("a re-audit states whether it moved patterns and scores",
      all(isinstance(c["mechanism_reaudit"].get(f), bool)
          for c in _reaudited for f in ("patterns_changed", "scores_changed")))


def _ra(case_extra=None, **kw):
    base = {"search_date": "2026-09-12", "ontology_revision": CURRENT_ONTOLOGY_REVISION,
            "revision_basis": "commit 442ffa6",
            "remediates": {"original_search_date": "2026-09-11", "original_revision": "MOR-003",
                           "untested_then": ["theory-experiment-asymmetry"]},
            "considered": sorted(revision_mechanisms(CURRENT_ONTOLOGY_REVISION)),
            "verdicts": [{"mechanism": m, "verdict": "not-supported", "note": "n"}
                         for m in sorted(revision_mechanisms(CURRENT_ONTOLOGY_REVISION))],
            "finding": "no-mechanism-evidenced", "note": "n",
            "patterns_changed": False, "scores_changed": False}
    base.update(kw)
    item = {"mechanism_audit": {"search_date": "2026-09-11", "ontology_revision": "MOR-003",
                                "incomplete_at_revision": ["theory-experiment-asymmetry"]},
            "mechanism_reaudit": base}
    item.update(case_extra or {})
    return _vmr("unawarded", item, "s.yaml", set(_mechs))


check("a well-formed re-audit passes", not _ra())
check("a re-audit of nothing is rejected",
      bool(_vmr("unawarded", {"mechanism_reaudit": {"search_date": "2026-09-12"}}, "s.yaml", _mechs)))
check("a re-audit cannot run under an older revision",
      bool(_ra(ontology_revision="MOR-005", revision_basis="commit 69ffcc0")))
check("a re-audit cannot leave a mechanism untested",
      bool(_ra(considered=sorted(revision_mechanisms("MOR-004")),
               verdicts=[{"mechanism": m, "verdict": "not-supported", "note": "n"}
                         for m in sorted(revision_mechanisms("MOR-004"))])))
check("a re-audit cannot predate the audit it repairs",
      bool(_ra(search_date="2026-09-10")))
check("a re-audit must restate the defect it repairs, exactly",
      bool(_ra(remediates={"original_search_date": "2026-09-11", "original_revision": "MOR-003",
                           "untested_then": []})))
check("a re-audit cannot misname the revision it repairs",
      bool(_ra(remediates={"original_search_date": "2026-09-11", "original_revision": "MOR-004",
                           "untested_then": ["theory-experiment-asymmetry"]})))
check("a verdict outside the vocabulary is rejected",
      bool(_ra(verdicts=[{"mechanism": m, "verdict": "probably", "note": "n"}
                         for m in sorted(revision_mechanisms(CURRENT_ONTOLOGY_REVISION))])))
check("a re-audit supporting what the case does not declare is rejected",
      bool(_ra(finding="mechanism-evidenced",
               verdicts=[{"mechanism": m,
                          "verdict": "supported" if m == "delayed-recognition" else "not-supported",
                          "note": "n"}
                         for m in sorted(revision_mechanisms(CURRENT_ONTOLOGY_REVISION))])))
check("a re-audit whose finding contradicts its own verdicts is rejected",
      bool(_ra(finding="mechanism-evidenced")))
check("a re-audit must say whether it moved patterns and scores",
      bool(_ra(patterns_changed=None)))

# The three figures are three different claims and must stay separable.
for _domain in ("physics-astronomy", "biology-medicine", "mathematics-computing"):
    _pd = dc.pattern_distribution(_domain)
    check(f"remediation does not rewrite history ({_domain})",
          _pd["n_audits_complete_at_revision"]
          == sum(1 for r in _pd["audit_revisions"] if not r["untested_at_revision"]))
    check(f"every declared defect is accounted for ({_domain})",
          not _pd["audit_defects_outstanding"])
    print(f"      [reported] {_domain}: complete when performed "
          f"{_pd['n_audits_complete_at_revision']}/{_pd['n_audits']}, defects remediated "
          f"{_pd['n_historical_audit_defects_remediated']}/{_pd['n_historical_audit_defects']}, "
          f"current {_pd['n_audits_current']}/{_pd['n_audits']}")
check("no Definition of Done criterion reads a remediation figure",
      not any(k in str(_ds.dod_rows("biology-medicine"))
              for k in ("remediated", "historical_audit_defects")))

print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
raise SystemExit(1 if failures else 0)
