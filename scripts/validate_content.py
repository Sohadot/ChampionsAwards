from __future__ import annotations

from typing import Any

import yaml

from config import (
    AWARD_ARCHITECTURE_KEYS,
    MECHANISM_FINDINGS,
    TIME_DEPENDENT_INTERACTIONS,
    CLUSTERS,
    INTERACTION_TYPES,
    DATA,
    DDI_KEYS,
    MIN_SUMMARY_LENGTH,
    REQUIRED_FIELDS_BY_CLUSTER,
    RECORD_GRADE_SOURCE_TYPES,
    RLS_KEYS,
    SOURCE_TYPES,
    VALID_STATUSES,
    is_iso_date,
    is_valid_basis,
    is_valid_domain,
    is_valid_hypothesis_state,
    is_valid_interaction_type,
    is_valid_mechanism_finding,
    is_year_or_iso_date,
    temporal_key,
    is_valid_slug,
    is_valid_source_type,
    normalize_slug,
)


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def validate_item(
    cluster_name: str,
    item: dict[str, Any],
    source_file: str,
    concept_slugs: set[str] | None = None,
    case_slugs: set[str] | None = None,
) -> list[str]:
    errors: list[str] = []

    required_fields = REQUIRED_FIELDS_BY_CLUSTER.get(cluster_name, ())
    for field in required_fields:
        value = item.get(field)
        if value is None:
            errors.append(f"{cluster_name}/{source_file}: missing required field '{field}'")
            continue

        if isinstance(value, str) and not value.strip():
            errors.append(f"{cluster_name}/{source_file}: empty required field '{field}'")

    slug = item.get("slug")
    if slug:
        normalized_slug = normalize_slug(str(slug))
        if not is_valid_slug(normalized_slug):
            errors.append(f"{cluster_name}/{source_file}: invalid slug '{normalized_slug}'")

    summary = item.get("summary")
    if isinstance(summary, str):
        if len(summary.strip()) < MIN_SUMMARY_LENGTH:
            errors.append(
                f"{cluster_name}/{source_file}: summary too short "
                f"({len(summary.strip())} chars, minimum {MIN_SUMMARY_LENGTH})"
            )

    status = item.get("status")
    if status is not None and str(status).strip().lower() not in VALID_STATUSES:
        errors.append(
            f"{cluster_name}/{source_file}: invalid status '{status}' "
            f"(expected one of: {', '.join(sorted(VALID_STATUSES))})"
        )

    errors.extend(validate_sources(cluster_name, item, source_file))
    errors.extend(validate_assessment(cluster_name, item, source_file))
    errors.extend(validate_rls_assessment(cluster_name, item, source_file))
    errors.extend(validate_key_facts(cluster_name, item, source_file))
    errors.extend(validate_analysis(cluster_name, item, source_file))
    errors.extend(validate_domains(cluster_name, item, source_file))
    errors.extend(validate_patterns(cluster_name, item, source_file, concept_slugs or set()))
    errors.extend(validate_provenance(cluster_name, item, source_file))
    errors.extend(validate_audit_exceptions(cluster_name, item, source_file))
    errors.extend(validate_architecture(cluster_name, item, source_file))
    errors.extend(validate_corpus_relations(cluster_name, item, source_file, case_slugs or set()))
    errors.extend(validate_report(cluster_name, item, source_file))
    errors.extend(validate_mechanism_audit(cluster_name, item, source_file, concept_slugs or set()))
    errors.extend(validate_temporal_validity(cluster_name, item, source_file))

    return errors


def _record_grade_refs(item: dict[str, Any], refs: Any) -> list[str]:
    """Which of these source refs are not record-grade (or do not exist)."""
    tmap = _source_types_by_index(item)
    bad: list[str] = []
    for ref in refs if isinstance(refs, list) else []:
        if not isinstance(ref, int) or ref not in tmap:
            bad.append(f"#{ref} (no such source)")
        elif tmap[ref] not in RECORD_GRADE_SOURCE_TYPES:
            bad.append(f"#{ref} ({tmap[ref]})")
    return bad


def validate_rule_at_time(
    item: dict[str, Any], where: str, block: Any, ref: str
) -> list[str]:
    """A rule tied to a historical event must state the rule AS IT STOOD THEN.

    Temporal validity is part of provenance: an official source for today's rule
    is not evidence about a decision taken before that rule existed.
    """
    errors: list[str] = []
    if not isinstance(block, dict):
        return [f"{ref}: {where} 'rule_at_time' must be a mapping"]

    if not is_year_or_iso_date(block.get("event_date")):
        errors.append(f"{ref}: {where} rule_at_time needs an 'event_date' (a year or an ISO date)")

    statement = block.get("rule_in_force")
    if not (isinstance(statement, str) and statement.strip()):
        errors.append(
            f"{ref}: {where} rule_at_time needs 'rule_in_force' stating what the rule was at that date"
        )

    has_anchor = bool(block.get("record_anchor"))
    has_exception = bool(block.get("exception"))
    if has_anchor == has_exception:
        errors.append(
            f"{ref}: {where} rule_at_time needs exactly one of 'record_anchor' (record-grade) or "
            f"'exception' (a documented search that found no record of the rule at that date)"
        )
    if has_anchor:
        bad = _record_grade_refs(item, block.get("record_anchor"))
        if bad:
            errors.append(
                f"{ref}: {where} rule_at_time record_anchor must be record-grade: {', '.join(bad)}"
            )
    if has_exception and not isinstance(block.get("exception"), dict):
        errors.append(f"{ref}: {where} rule_at_time exception must be a mapping documenting the search")

    for field in ("effective_from", "effective_to"):
        if field in block and not is_year_or_iso_date(block[field]):
            errors.append(f"{ref}: {where} rule_at_time '{field}' must be a year or an ISO date")
    start, end = block.get("effective_from"), block.get("effective_to")
    if is_year_or_iso_date(start) and is_year_or_iso_date(end) and temporal_key(start) > temporal_key(end):
        errors.append(f"{ref}: {where} rule_at_time effective_from is after effective_to")

    # The point of the field: the rule must actually have been in force at the event.
    event = block.get("event_date")
    if is_year_or_iso_date(event) and is_year_or_iso_date(start) and temporal_key(event) < temporal_key(start):
        errors.append(
            f"{ref}: {where} rule_at_time applies a rule effective from {start} to an event in {event} "
            f"- a rule cannot govern a decision taken before it existed"
        )
    if is_year_or_iso_date(event) and is_year_or_iso_date(end) and temporal_key(event) > temporal_key(end):
        errors.append(
            f"{ref}: {where} rule_at_time applies a rule that ceased at {end} to an event in {event}"
        )
    return errors


def validate_temporal_validity(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """Corpus relations that assert a rule bore on a case must date that rule.

    Only the time-dependent interaction types require it; ordinary documented
    outcomes do not. Provenance entries may also carry effective_from/effective_to
    where the rule they cite has a known start or end.
    """
    ref = f"{cluster_name}/{source_file}"
    errors: list[str] = []

    for index, rel in enumerate(item.get("corpus_relations") or [], start=1):
        if not isinstance(rel, dict):
            continue
        where = f"corpus_relation #{index}"
        if "rule_at_time" in rel:
            errors.extend(validate_rule_at_time(item, where, rel["rule_at_time"], ref))
        elif rel.get("interaction_type") in TIME_DEPENDENT_INTERACTIONS:
            errors.append(
                f"{ref}: {where} is a '{rel['interaction_type']}' and must carry 'rule_at_time' - "
                f"a rule that has changed over time may only be applied to an event once the record "
                f"shows which version was then in force"
            )

    provenance = item.get("provenance")
    if isinstance(provenance, dict):
        for claim, entry in provenance.items():
            if not isinstance(entry, dict):
                continue
            if "rule_at_time" in entry:
                errors.extend(validate_rule_at_time(item, f"provenance['{claim}']", entry["rule_at_time"], ref))
            for field in ("effective_from", "effective_to"):
                if field in entry and not is_year_or_iso_date(entry[field]):
                    errors.append(f"{ref}: provenance['{claim}'] '{field}' must be a year or an ISO date")
    return errors


def validate_mechanism_audit(
    cluster_name: str, item: dict[str, Any], source_file: str, concept_slugs: set[str]
) -> list[str]:
    """A mechanism audit turns "no mechanism recorded" from a silence into a
    documented decision: what was considered, when, what the record showed, and
    the best sources found. Its finding must agree with the case's patterns, so
    an audit can never say one thing while the tags say another."""
    ref = f"{cluster_name}/{source_file}"
    audit = item.get("mechanism_audit")
    if audit is None:
        return []
    if not isinstance(audit, dict):
        return [f"{ref}: 'mechanism_audit' must be a mapping when present"]

    errors: list[str] = []
    if not is_iso_date(audit.get("search_date")):
        errors.append(f"{ref}: mechanism_audit needs an ISO 'search_date' (the audit is dated evidence)")

    considered = audit.get("considered")
    if not isinstance(considered, list) or not considered:
        errors.append(f"{ref}: mechanism_audit needs a non-empty 'considered' list of mechanisms tested")
    else:
        unknown = [c for c in considered if c not in concept_slugs]
        if unknown:
            errors.append(
                f"{ref}: mechanism_audit considered unknown mechanism(s): {', '.join(map(str, unknown))} "
                f"(each must be a published concept)"
            )

    finding = audit.get("finding")
    if not is_valid_mechanism_finding(finding):
        errors.append(
            f"{ref}: mechanism_audit 'finding' must be one of: {', '.join(sorted(MECHANISM_FINDINGS))}"
        )

    note = audit.get("note")
    if not (isinstance(note, str) and note.strip()):
        errors.append(f"{ref}: mechanism_audit needs a 'note' stating what the record did and did not show")

    sources = item.get("sources") if isinstance(item.get("sources"), list) else []
    for ref_index in audit.get("best_sources") or []:
        if not isinstance(ref_index, int) or not (1 <= ref_index <= len(sources)):
            errors.append(f"{ref}: mechanism_audit best_sources reference #{ref_index} does not exist")

    # The audit and the tags must agree.
    declared = [p for p in (item.get("patterns") or []) if isinstance(p, str)]
    if finding == "no-mechanism-evidenced" and declared:
        errors.append(
            f"{ref}: mechanism_audit says no mechanism is evidenced, but the case declares patterns: "
            f"{', '.join(declared)}"
        )
    if finding == "mechanism-evidenced" and not declared:
        errors.append(
            f"{ref}: mechanism_audit says a mechanism is evidenced, but the case declares no patterns"
        )
    return errors


REPORT_PROSE_FIELDS = ("summary", "question", "scope")

# The engine emits counts, never universals. An observation that says "every",
# "never" or "all" is asserting something the engine did not compute, and it is
# the claim most likely to be quietly falsified by the next audited case - so it
# is rejected in observations. Hypotheses and limits may quantify, because they
# are labelled as interpretation and carry their own refutation conditions.
UNIVERSAL_TERMS: tuple[str, ...] = (
    "every", "never", "always", "all cases", "no case", "none of", "without exception", "invariably",
)


def _report_prose(item: dict[str, Any]) -> list[tuple[str, str]]:
    """Every stretch of report prose, with a label, so the figure-token rules can
    be applied uniformly instead of field by field."""
    blocks: list[tuple[str, str]] = []
    for field in REPORT_PROSE_FIELDS:
        value = item.get(field)
        if isinstance(value, str):
            blocks.append((field, value))
    for index, obs in enumerate(item.get("observations") or [], start=1):
        if isinstance(obs, dict) and isinstance(obs.get("statement"), str):
            blocks.append((f"observation #{index}", obs["statement"]))
    for index, hyp in enumerate(item.get("hypotheses") or [], start=1):
        if isinstance(hyp, dict):
            for field in ("statement", "basis", "refuted_by", "outcome"):
                if isinstance(hyp.get(field), str):
                    blocks.append((f"hypothesis #{index}.{field}", hyp[field]))
    for index, limit in enumerate(item.get("limits") or [], start=1):
        if isinstance(limit, str):
            blocks.append((f"limit #{index}", limit))
    return blocks


def validate_report(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """A synthesis report is prose over a computed corpus, so it is held to two
    rules the rest of the site cannot enforce on prose:

      * it must declare the governed domain it derives from, and
      * it may not type a statistic. Figures appear as tokens resolved from the
        canonical engine at build time; an unknown token or a bare number is a
        validation error, not a style note.

    Observation and hypothesis are kept structurally apart: an observation must
    cite at least one figure, and a hypothesis must say what would refute it.
    """
    if cluster_name != "reports":
        return []
    ref = f"{cluster_name}/{source_file}"
    errors: list[str] = []

    domain = item.get("derives_from")
    if not (isinstance(domain, str) and is_valid_domain(domain)):
        errors.append(f"{ref}: a report must declare 'derives_from' naming a known domain "
                      f"(its evidence is that governed corpus)")
        return errors

    for field in ("question", "scope"):
        value = item.get(field)
        if not (isinstance(value, str) and value.strip()):
            errors.append(f"{ref}: a report needs a non-empty '{field}'")

    from synthesis_figures import bare_numbers, cited_tokens, unknown_tokens  # local: engine import

    figures = figure_map_cached(domain)

    observations = item.get("observations")
    if not isinstance(observations, list) or not observations:
        errors.append(f"{ref}: a report needs a non-empty 'observations' list")
    else:
        for index, obs in enumerate(observations, start=1):
            if not isinstance(obs, dict) or not isinstance(obs.get("statement"), str) or not obs["statement"].strip():
                errors.append(f"{ref}: observation #{index} needs a non-empty 'statement'")
                continue
            universal = [t for t in UNIVERSAL_TERMS if t in obs["statement"].lower()]
            if universal:
                errors.append(
                    f"{ref}: observation #{index} uses the universal term(s) {', '.join(universal)}; "
                    f"the engine computes counts, not universals - state the count with its denominator "
                    f"(a universal claim belongs in 'hypotheses', where it carries a refutation condition)"
                )
            if not cited_tokens(obs["statement"]):
                errors.append(
                    f"{ref}: observation #{index} states no figure; an observation must cite at least one "
                    f"engine figure token (a claim without a figure belongs in 'hypotheses')"
                )
            derived = obs.get("derived_from")
            if not isinstance(derived, list) or not derived:
                errors.append(f"{ref}: observation #{index} needs 'derived_from' naming the engine figures it rests on")
            else:
                unknown = [d for d in derived if d not in figures]
                if unknown:
                    errors.append(f"{ref}: observation #{index} derives from unknown figures: {', '.join(map(str, unknown))}")

    hypotheses = item.get("hypotheses")
    if hypotheses is not None:
        if not isinstance(hypotheses, list) or not hypotheses:
            errors.append(f"{ref}: 'hypotheses' must be a non-empty list when present")
        else:
            for index, hyp in enumerate(hypotheses, start=1):
                if not isinstance(hyp, dict):
                    errors.append(f"{ref}: hypothesis #{index} must be a mapping")
                    continue
                for field in ("statement", "basis", "refuted_by"):
                    value = hyp.get(field)
                    if not (isinstance(value, str) and value.strip()):
                        errors.append(
                            f"{ref}: hypothesis #{index} needs a non-empty '{field}' "
                            f"(a hypothesis that cannot be refuted is not published as one)"
                        )
                state = hyp.get("state", "open")
                if not is_valid_hypothesis_state(state):
                    errors.append(f"{ref}: hypothesis #{index} has unknown state '{state}' (open or refuted)")
                elif state == "refuted" and not (isinstance(hyp.get("outcome"), str) and hyp["outcome"].strip()):
                    errors.append(
                        f"{ref}: hypothesis #{index} is marked refuted and must record an 'outcome' "
                        f"saying what refuted it and when (a refuted hypothesis stays on the record)"
                    )

    limits = item.get("limits")
    if not isinstance(limits, list) or not limits or not all(isinstance(v, str) and v.strip() for v in limits):
        errors.append(f"{ref}: a report needs a non-empty 'limits' list of non-empty statements")

    for label, text in _report_prose(item):
        unknown = unknown_tokens(text, figures)
        if unknown:
            errors.append(f"{ref}: {label} cites unknown figure token(s): {', '.join(unknown)}")
        typed = bare_numbers(text)
        if typed:
            errors.append(
                f"{ref}: {label} types the number(s) {', '.join(typed)} directly; report figures must be "
                f"tokens resolved from the engine (years are the only literal numbers allowed)"
            )
    return errors


_FIGURE_CACHE: dict[str, dict[str, str]] = {}


def figure_map_cached(domain: str) -> dict[str, str]:
    if domain not in _FIGURE_CACHE:
        from synthesis_figures import figure_map
        _FIGURE_CACHE[domain] = figure_map(domain)
    return _FIGURE_CACHE[domain]


def validate_architecture(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """The formal-architecture layer of an award: a mapping whose keys are the
    known architecture fields and whose values are non-empty text or lists."""
    errors: list[str] = []
    architecture = item.get("architecture")
    if architecture is None:
        return errors
    if not isinstance(architecture, dict) or not architecture:
        errors.append(f"{cluster_name}/{source_file}: 'architecture' must be a non-empty mapping when present")
        return errors
    for key, value in architecture.items():
        if key not in AWARD_ARCHITECTURE_KEYS:
            errors.append(
                f"{cluster_name}/{source_file}: architecture has unknown field '{key}' "
                f"(known: {', '.join(sorted(AWARD_ARCHITECTURE_KEYS))})"
            )
        if isinstance(value, str):
            if not value.strip():
                errors.append(f"{cluster_name}/{source_file}: architecture['{key}'] is empty")
        elif isinstance(value, list):
            if not value or not all(isinstance(v, str) and v.strip() for v in value):
                errors.append(f"{cluster_name}/{source_file}: architecture['{key}'] must be a list of non-empty strings")
        else:
            errors.append(f"{cluster_name}/{source_file}: architecture['{key}'] must be text or a list")
    return errors


def validate_corpus_relations(
    cluster_name: str, item: dict[str, Any], source_file: str, case_slugs: set[str]
) -> list[str]:
    """The corpus-interaction layer: each relation ties a case to one architecture
    element with a scoped note. The case must resolve to a published entry, so the
    relation is evidenced by an already-audited case, not asserted editorially."""
    errors: list[str] = []
    relations = item.get("corpus_relations")
    if relations is None:
        return errors
    if not isinstance(relations, list) or not relations:
        errors.append(f"{cluster_name}/{source_file}: 'corpus_relations' must be a non-empty list when present")
        return errors
    tmap = _source_types_by_index(item)
    count = len(tmap)
    for index, rel in enumerate(relations, start=1):
        if not isinstance(rel, dict):
            errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} must be a mapping")
            continue
        case = rel.get("case")
        if not isinstance(case, str) or case not in case_slugs:
            errors.append(
                f"{cluster_name}/{source_file}: corpus_relation #{index} 'case' must be a published case slug"
            )
        if rel.get("architecture_element") not in AWARD_ARCHITECTURE_KEYS:
            errors.append(
                f"{cluster_name}/{source_file}: corpus_relation #{index} 'architecture_element' must be a known architecture field"
            )
        if not is_valid_interaction_type(rel.get("interaction_type")):
            errors.append(
                f"{cluster_name}/{source_file}: corpus_relation #{index} needs an 'interaction_type' from the vocabulary"
            )
        if not isinstance(rel.get("claim"), str) or not rel["claim"].strip():
            errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} needs a non-empty 'claim'")

        # A relation is either anchored to a record-grade source, or carries a
        # documented secondary-sufficient exception - exactly one of the two.
        anchor = rel.get("record_anchor")
        exception = rel.get("exception")
        if (anchor is None) == (exception is None):
            errors.append(
                f"{cluster_name}/{source_file}: corpus_relation #{index} needs exactly one of "
                f"'record_anchor' or 'exception'"
            )
        if anchor is not None:
            if not isinstance(anchor, list) or not anchor:
                errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} record_anchor must be a non-empty list")
            else:
                for ref in anchor:
                    if not isinstance(ref, int) or isinstance(ref, bool) or not (1 <= ref <= count):
                        errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} record_anchor {ref!r} out of range (1..{count})")
                    elif tmap.get(ref) not in RECORD_GRADE_SOURCE_TYPES:
                        errors.append(
                            f"{cluster_name}/{source_file}: corpus_relation #{index} record_anchor [{ref}] is "
                            f"'{tmap.get(ref)}', not record-grade (use 'exception' instead)"
                        )
        if exception is not None:
            if not isinstance(exception, dict):
                errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} 'exception' must be a mapping")
            else:
                for field in ("search_note", "reason"):
                    if not isinstance(exception.get(field), str) or not exception[field].strip():
                        errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} exception needs '{field}'")
                if not is_iso_date(exception.get("search_date")):
                    errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} exception needs an ISO 'search_date'")
                best = exception.get("best_source")
                if best is not None and (not isinstance(best, int) or isinstance(best, bool) or not (1 <= best <= count)):
                    errors.append(f"{cluster_name}/{source_file}: corpus_relation #{index} exception 'best_source' out of range")
    return errors


def _source_types_by_index(item: dict[str, Any]) -> dict[int, str]:
    return {i: (s.get("type") or "?") for i, s in enumerate(item.get("sources") or [], start=1)}


def validate_provenance(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """Claim-level authority. `provenance` maps a claim to a record_anchor (source
    indices) plus a `basis` explaining why that source is authoritative FOR that
    claim. Every anchor index must point to a record-grade source, so a claim
    cannot be closed on a source's mere type."""
    errors: list[str] = []
    provenance = item.get("provenance")
    if provenance is None:
        return errors

    if not isinstance(provenance, dict) or not provenance:
        errors.append(f"{cluster_name}/{source_file}: 'provenance' must be a non-empty mapping when present")
        return errors

    tmap = _source_types_by_index(item)
    count = len(tmap)
    for claim, decl in provenance.items():
        if not isinstance(decl, dict):
            errors.append(f"{cluster_name}/{source_file}: provenance['{claim}'] must be a mapping")
            continue
        anchor = decl.get("record_anchor")
        basis = decl.get("basis")
        if not isinstance(anchor, list) or not anchor:
            errors.append(f"{cluster_name}/{source_file}: provenance['{claim}'] needs a non-empty 'record_anchor'")
        else:
            for ref in anchor:
                if not isinstance(ref, int) or isinstance(ref, bool) or not (1 <= ref <= count):
                    errors.append(
                        f"{cluster_name}/{source_file}: provenance['{claim}'] record_anchor {ref!r} out of range (1..{count})"
                    )
                elif tmap.get(ref) not in RECORD_GRADE_SOURCE_TYPES:
                    errors.append(
                        f"{cluster_name}/{source_file}: provenance['{claim}'] record_anchor [{ref}] is "
                        f"'{tmap.get(ref)}', not a record-grade source (use audit_exceptions instead)"
                    )
        if not is_valid_basis(basis):
            errors.append(
                f"{cluster_name}/{source_file}: provenance['{claim}'] needs a 'basis' from the vocabulary"
            )
    return errors


def validate_audit_exceptions(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """A source-grade exception is a documented decision, not a bare tag: it must
    record the claim, the search date, a note, the best available source, and why
    no stronger record was found."""
    errors: list[str] = []
    exceptions = item.get("audit_exceptions")
    if exceptions is None:
        return errors

    if not isinstance(exceptions, list) or not exceptions:
        errors.append(f"{cluster_name}/{source_file}: 'audit_exceptions' must be a non-empty list when present")
        return errors

    count = len(item.get("sources") or [])
    for index, decision in enumerate(exceptions, start=1):
        if not isinstance(decision, dict):
            errors.append(f"{cluster_name}/{source_file}: audit_exception #{index} must be a mapping")
            continue
        for field in ("claim", "search_note", "reason"):
            if not isinstance(decision.get(field), str) or not decision[field].strip():
                errors.append(f"{cluster_name}/{source_file}: audit_exception #{index} needs a non-empty '{field}'")
        if not is_iso_date(decision.get("search_date")):
            errors.append(f"{cluster_name}/{source_file}: audit_exception #{index} needs an ISO 'search_date'")
        best = decision.get("best_source")
        if not isinstance(best, int) or isinstance(best, bool) or not (1 <= best <= count):
            errors.append(
                f"{cluster_name}/{source_file}: audit_exception #{index} needs 'best_source' in range (1..{count})"
            )
    return errors


def validate_domains(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """`domain` (a single value) and `domains` (a list) must reference known
    domains when present. Both are validated for shape here; the gate decides
    where they are required."""
    errors: list[str] = []

    domain = item.get("domain")
    if domain is not None and not (isinstance(domain, str) and is_valid_domain(domain)):
        errors.append(
            f"{cluster_name}/{source_file}: unknown domain '{domain}' "
            f"(add it to DOMAINS in config.py first)"
        )

    domains = item.get("domains")
    if domains is not None:
        if not isinstance(domains, list) or not domains:
            errors.append(f"{cluster_name}/{source_file}: 'domains' must be a non-empty list when present")
        else:
            for value in domains:
                if not (isinstance(value, str) and is_valid_domain(value)):
                    errors.append(f"{cluster_name}/{source_file}: unknown domain '{value}' in 'domains'")

    return errors


def validate_patterns(
    cluster_name: str, item: dict[str, Any], source_file: str, concept_slugs: set[str]
) -> list[str]:
    """`patterns` links a case to structural-cause concepts by slug. Each slug
    must resolve to a published concept, so the ontology stays connected.
    `pattern_evidence` ties each pattern to specific sources proving the
    mechanism; its keys must be a subset of `patterns` and its refs in range."""
    errors: list[str] = []
    patterns = item.get("patterns")
    if patterns is None:
        return errors

    if not isinstance(patterns, list) or not patterns:
        errors.append(f"{cluster_name}/{source_file}: 'patterns' must be a non-empty list when present")
        return errors

    for slug in patterns:
        if not isinstance(slug, str) or not slug.strip():
            errors.append(f"{cluster_name}/{source_file}: each pattern must be a concept slug string")
        elif slug not in concept_slugs:
            errors.append(
                f"{cluster_name}/{source_file}: pattern '{slug}' does not match any published concept"
            )

    pattern_evidence = item.get("pattern_evidence")
    if pattern_evidence is not None:
        if not isinstance(pattern_evidence, dict) or not pattern_evidence:
            errors.append(f"{cluster_name}/{source_file}: 'pattern_evidence' must be a non-empty mapping")
            return errors
        source_count = len(item.get("sources") or [])
        pattern_set = {p for p in patterns if isinstance(p, str)}
        for slug, refs in pattern_evidence.items():
            if slug not in pattern_set:
                errors.append(
                    f"{cluster_name}/{source_file}: pattern_evidence key '{slug}' is not in 'patterns'"
                )
                continue
            if not isinstance(refs, list) or not refs:
                errors.append(
                    f"{cluster_name}/{source_file}: pattern_evidence['{slug}'] must be a non-empty list"
                )
                continue
            for ref in refs:
                if not isinstance(ref, int) or isinstance(ref, bool) or not (1 <= ref <= source_count):
                    errors.append(
                        f"{cluster_name}/{source_file}: pattern_evidence['{slug}'] has out-of-range "
                        f"source index {ref!r} (1..{source_count})"
                    )

    return errors


def validate_key_facts(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """key_facts is an optional list of {fact, source} where 'source' is a
    1-based index into the entry's 'sources' list, keeping every fact traceable."""
    errors: list[str] = []
    key_facts = item.get("key_facts")
    if key_facts is None:
        return errors

    if not isinstance(key_facts, list) or not key_facts:
        errors.append(f"{cluster_name}/{source_file}: 'key_facts' must be a non-empty list when present")
        return errors

    source_count = len(item.get("sources") or [])
    for index, entry in enumerate(key_facts, start=1):
        if not isinstance(entry, dict):
            errors.append(f"{cluster_name}/{source_file}: key_fact #{index} must be a mapping")
            continue

        fact = entry.get("fact")
        if not isinstance(fact, str) or not fact.strip():
            errors.append(f"{cluster_name}/{source_file}: key_fact #{index} needs a non-empty 'fact'")

        ref = entry.get("source")
        if ref is not None:
            if not isinstance(ref, int) or isinstance(ref, bool) or not (1 <= ref <= source_count):
                errors.append(
                    f"{cluster_name}/{source_file}: key_fact #{index} 'source' must be a 1-based "
                    f"index into 'sources' (1..{source_count})"
                )

    return errors


def validate_analysis(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """analysis is an optional list of {heading, body} sections."""
    errors: list[str] = []
    analysis = item.get("analysis")
    if analysis is None:
        return errors

    if not isinstance(analysis, list) or not analysis:
        errors.append(f"{cluster_name}/{source_file}: 'analysis' must be a non-empty list when present")
        return errors

    for index, section in enumerate(analysis, start=1):
        if not isinstance(section, dict):
            errors.append(f"{cluster_name}/{source_file}: analysis section #{index} must be a mapping")
            continue
        for field in ("heading", "body"):
            value = section.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"{cluster_name}/{source_file}: analysis section #{index} needs a non-empty '{field}'"
                )

    return errors


def _is_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 100


def validate_assessment(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """A DDI assessment is optional, but when present every dimension must carry
    a 0-100 score so the composite is well-defined and reproducible."""
    errors: list[str] = []
    assessment = item.get("assessment")
    if assessment is None:
        return errors

    if not isinstance(assessment, dict):
        errors.append(f"{cluster_name}/{source_file}: 'assessment' must be a mapping when present")
        return errors

    for key in DDI_KEYS:
        if key not in assessment:
            errors.append(f"{cluster_name}/{source_file}: assessment missing dimension '{key}'")
        elif not _is_score(assessment[key]):
            errors.append(f"{cluster_name}/{source_file}: assessment '{key}' must be a number 0-100")

    recognition = assessment.get("observed_recognition")
    if recognition is not None and not _is_score(recognition):
        errors.append(f"{cluster_name}/{source_file}: 'observed_recognition' must be a number 0-100")

    errors.extend(
        validate_evidence(
            cluster_name, item, source_file, "assessment",
            allowed_keys=set(DDI_KEYS) | {"observed_recognition"},
        )
    )

    return errors


def validate_evidence(
    cluster_name: str,
    item: dict[str, Any],
    source_file: str,
    block_name: str,
    allowed_keys: set[str],
) -> list[str]:
    """Score-level provenance: `evidence` maps each dimension (and, for the DDI,
    observed_recognition) to 1-based indices into the entry's `sources`, so every
    judgment is traceable to specific references. Shape-checked when present; the
    quality gate decides where it is required."""
    errors: list[str] = []
    block = item.get(block_name)
    if not isinstance(block, dict):
        return errors
    evidence = block.get("evidence")
    if evidence is None:
        return errors

    if not isinstance(evidence, dict) or not evidence:
        errors.append(f"{cluster_name}/{source_file}: {block_name}.evidence must be a non-empty mapping")
        return errors

    source_count = len(item.get("sources") or [])
    for key, refs in evidence.items():
        if key not in allowed_keys:
            errors.append(f"{cluster_name}/{source_file}: {block_name}.evidence has unknown key '{key}'")
            continue
        if not isinstance(refs, list) or not refs:
            errors.append(
                f"{cluster_name}/{source_file}: {block_name}.evidence['{key}'] must be a non-empty list"
            )
            continue
        for ref in refs:
            if not isinstance(ref, int) or isinstance(ref, bool) or not (1 <= ref <= source_count):
                errors.append(
                    f"{cluster_name}/{source_file}: {block_name}.evidence['{key}'] has out-of-range "
                    f"source index {ref!r} (1..{source_count})"
                )

    return errors


def validate_rls_assessment(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """An RLS assessment (systems) is optional, but when present every legitimacy
    dimension must carry a 0-100 score so the composite is reproducible."""
    errors: list[str] = []
    assessment = item.get("rls_assessment")
    if assessment is None:
        return errors

    if not isinstance(assessment, dict):
        errors.append(f"{cluster_name}/{source_file}: 'rls_assessment' must be a mapping when present")
        return errors

    for key in RLS_KEYS:
        if key not in assessment:
            errors.append(f"{cluster_name}/{source_file}: rls_assessment missing dimension '{key}'")
        elif not _is_score(assessment[key]):
            errors.append(f"{cluster_name}/{source_file}: rls_assessment '{key}' must be a number 0-100")

    errors.extend(
        validate_evidence(
            cluster_name, item, source_file, "rls_assessment", allowed_keys=set(RLS_KEYS)
        )
    )

    return errors


def validate_sources(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """Sourcing is optional, but when present it must meet the editorial protocol shape:
    a non-empty list of references, each with a title and a checkable URL."""
    errors: list[str] = []
    sources = item.get("sources")
    if sources is None:
        return errors

    if not isinstance(sources, list) or not sources:
        errors.append(f"{cluster_name}/{source_file}: 'sources' must be a non-empty list when present")
        return errors

    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"{cluster_name}/{source_file}: source #{index} must be a mapping")
            continue

        title = source.get("title")
        if not isinstance(title, str) or not title.strip():
            errors.append(f"{cluster_name}/{source_file}: source #{index} is missing a non-empty 'title'")

        url = source.get("url")
        if not isinstance(url, str) or not url.strip().startswith(("http://", "https://")):
            errors.append(f"{cluster_name}/{source_file}: source #{index} needs a valid http(s) 'url'")

        source_type = source.get("type")
        if source_type is None:
            errors.append(f"{cluster_name}/{source_file}: source #{index} needs a 'type' from the taxonomy")
        elif not is_valid_source_type(source_type):
            errors.append(
                f"{cluster_name}/{source_file}: source #{index} has unknown type '{source_type}' "
                f"(expected one of: {', '.join(sorted(SOURCE_TYPES))})"
            )

    return errors


def collect_published_slugs(cluster: str) -> set[str]:
    slugs: set[str] = set()
    folder = DATA / cluster
    if not folder.exists():
        return slugs
    for path in sorted(folder.glob("*.yaml")):
        item = load_yaml_file(path)
        status = str(item.get("status", "published")).strip().lower()
        raw_slug = item.get("slug")
        if raw_slug and status == "published":
            slugs.add(normalize_slug(str(raw_slug)))
    return slugs


def main() -> None:
    all_errors: list[str] = []
    concept_slugs = collect_published_slugs("concepts")
    case_slugs = collect_published_slugs("unawarded")

    for cluster_name in CLUSTERS:
        folder = DATA / cluster_name
        if not folder.exists():
            continue

        for path in sorted(folder.glob("*.yaml")):
            item = load_yaml_file(path)
            item_errors = validate_item(cluster_name, item, path.name, concept_slugs, case_slugs)
            all_errors.extend(item_errors)

    if all_errors:
        print("Content validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("Content validation passed successfully.")


if __name__ == "__main__":
    main()
