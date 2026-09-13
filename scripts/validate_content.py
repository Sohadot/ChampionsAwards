from __future__ import annotations

from typing import Any

import yaml

from config import (
    ARCHIVE_VISIBILITY_STATES,
    DOMAIN_SCOPED_CLUSTERS,
    DOMAIN_SCOPE_POSTURES,
    CALIBRATION_REQUIRED_DOMAINS,
    SCORE_INPUT_KEYS,
    calibration_inputs,
    domain_calibration,
    domain_state,
    is_aggregated_domain,
    is_published,
    AUDIT_ELIGIBLE_CONCEPT_TYPES,
    COMPLETENESS_ENFORCED_FROM,
    CURRENT_ONTOLOGY_REVISION,
    LEGACY_REVISION_UNRESOLVED,
    is_valid_mechanism_verdict,
    MECHANISM_VERDICTS,
    asserts_corpus_cases,
    is_valid_ontology_revision,
    revision_is_before,
    revision_mechanisms,
    AWARD_ARCHITECTURE_KEYS,
    FUNDING_SEPARATION_REQUIRED,
    RECURRENCE_CONTEXTS,
    is_valid_recurrence_context,
    SEO_BRAND_SUFFIX,
    SEO_CONTRACT_CLUSTERS,
    SEO_CONTRACT_FIELDS,
    SEO_DESCRIPTION_MAX,
    SEO_DESCRIPTION_MIN,
    SEO_INDEXING_STATES,
    SEO_REQUIRED_SCHEMA_TYPES,
    SEO_TITLE_MAX,
    is_canonical_path,
    is_valid_schema_type,
    CONCEPT_TYPES,
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
    domain_subfields,
    is_composite_domain,
    is_valid_archive_state,
    is_valid_concept_type,
    is_valid_subfield,
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
    mechanism_slugs: set[str] | None = None,
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
    errors.extend(validate_patterns(cluster_name, item, source_file, concept_slugs or set(),
                                    mechanism_slugs if mechanism_slugs is not None else concept_slugs or set()))
    errors.extend(validate_provenance(cluster_name, item, source_file))
    errors.extend(validate_audit_exceptions(cluster_name, item, source_file))
    errors.extend(validate_architecture(cluster_name, item, source_file))
    errors.extend(validate_corpus_relations(cluster_name, item, source_file, case_slugs or set()))
    errors.extend(validate_report(cluster_name, item, source_file))
    errors.extend(validate_mechanism_audit(
        cluster_name, item, source_file,
        mechanism_slugs if mechanism_slugs is not None else concept_slugs or set()))
    errors.extend(validate_mechanism_reaudit(
        cluster_name, item, source_file,
        mechanism_slugs if mechanism_slugs is not None else concept_slugs or set()))
    errors.extend(validate_temporal_validity(cluster_name, item, source_file))
    errors.extend(validate_concept_type(cluster_name, item, source_file))
    errors.extend(validate_subfield(cluster_name, item, source_file))
    errors.extend(validate_rule_history(cluster_name, item, source_file, case_slugs or set()))
    errors.extend(validate_archive_visibility(cluster_name, item, source_file, case_slugs or set()))
    errors.extend(validate_pattern_context(cluster_name, item, source_file))
    errors.extend(validate_seo(cluster_name, item, source_file))
    errors.extend(validate_concept_corpus_claim(cluster_name, item, source_file))
    errors.extend(validate_score_calibration(cluster_name, item, source_file))
    errors.extend(validate_assessment_scope(cluster_name, item, source_file))

    return errors


def validate_subfield(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """In a composite domain, an entry says which side of the join it sits on.
    Without it, a domain can report maturity while one half of its own name is
    empty, and nothing in the record would show it."""
    ref = f"{cluster_name}/{source_file}"
    errors: list[str] = []
    domains = [item["domain"]] if isinstance(item.get("domain"), str) else list(item.get("domains") or [])
    composite = [d for d in domains if is_composite_domain(d)]
    if not composite:
        if "subfield" in item:
            errors.append(f"{ref}: 'subfield' is only meaningful in a composite domain")
        return errors
    value = item.get("subfield")
    if value is None:
        errors.append(
            f"{ref}: entries in {composite[0]} must declare a 'subfield' "
            f"(one of: {', '.join(domain_subfields(composite[0]))})"
        )
    elif not any(is_valid_subfield(d, value) for d in composite):
        errors.append(
            f"{ref}: unknown subfield '{value}' for {composite[0]} "
            f"(expected one of: {', '.join(domain_subfields(composite[0]))})"
        )
    return errors


def validate_rule_history(
    cluster_name: str, item: dict[str, Any], source_file: str, case_slugs: set[str]
) -> list[str]:
    """The historical-rule layer of an award: for each rule element, what is in
    force now, since when, what is known of the state before it, and - for each
    corpus event the rule is asked about - whether the version that governed
    that event is established at all.

    The point of the layer is that the last question usually has the answer
    "no", and a page that cannot say so will silently answer it with today's rule.
    """
    if cluster_name not in ("awards", "recognition-systems"):
        return []
    ref = f"{cluster_name}/{source_file}"
    history = item.get("rule_history")
    if history is None:
        return []
    if not isinstance(history, list) or not history:
        return [f"{ref}: 'rule_history' must be a non-empty list when present"]

    errors: list[str] = []
    for index, entry in enumerate(history, start=1):
        where = f"rule_history #{index}"
        if not isinstance(entry, dict):
            errors.append(f"{ref}: {where} must be a mapping")
            continue
        if entry.get("element") not in AWARD_ARCHITECTURE_KEYS:
            errors.append(
                f"{ref}: {where} 'element' must be a known architecture field "
                f"(got {entry.get('element')!r})"
            )
        for field in ("current_rule", "predecessor_state"):
            if not (isinstance(entry.get(field), str) and entry[field].strip()):
                errors.append(f"{ref}: {where} needs a non-empty '{field}'")
        if "effective_from" in entry and not is_year_or_iso_date(entry["effective_from"]):
            errors.append(f"{ref}: {where} 'effective_from' must be a year or an ISO date")
        has_anchor, has_exception = bool(entry.get("record_anchor")), bool(entry.get("exception"))
        if has_anchor == has_exception:
            errors.append(f"{ref}: {where} needs exactly one of 'record_anchor' or 'exception'")
        if has_anchor:
            bad = _record_grade_refs(item, entry.get("record_anchor"))
            if bad:
                errors.append(f"{ref}: {where} record_anchor must be record-grade: {', '.join(bad)}")

        for sub, event in enumerate(entry.get("events_covered") or [], start=1):
            label = f"{where} event #{sub}"
            if not isinstance(event, dict):
                errors.append(f"{ref}: {label} must be a mapping")
                continue
            if event.get("case") not in case_slugs:
                errors.append(f"{ref}: {label} 'case' must be a published case slug")
            if not is_year_or_iso_date(event.get("event_date")):
                errors.append(f"{ref}: {label} needs an 'event_date'")
            if not isinstance(event.get("established"), bool):
                errors.append(
                    f"{ref}: {label} needs 'established' as true or false - whether the version of "
                    f"this rule that governed this event is established by the record"
                )
            if not (isinstance(event.get("note"), str) and event["note"].strip()):
                errors.append(f"{ref}: {label} needs a 'note'")
            if event.get("established") is True and is_year_or_iso_date(entry.get("effective_from")) \
                    and is_year_or_iso_date(event.get("event_date")) \
                    and temporal_key(event["event_date"]) < temporal_key(entry["effective_from"]):
                errors.append(
                    f"{ref}: {label} claims the governing rule is established, but the rule cited "
                    f"takes effect in {entry['effective_from']}, after the event in {event['event_date']}"
                )
    return errors


def validate_archive_visibility(
    cluster_name: str, item: dict[str, Any], source_file: str, case_slugs: set[str]
) -> list[str]:
    """The archive layer: how far the award's own record is open, and what that
    means for each corpus case. Four states are kept apart, because "we found no
    nomination" and "the years are not released" are different facts."""
    if cluster_name != "awards":
        return []
    ref = f"{cluster_name}/{source_file}"
    block = item.get("archive_visibility")
    if block is None:
        return []
    if not isinstance(block, dict):
        return [f"{ref}: 'archive_visibility' must be a mapping when present"]

    errors: list[str] = []
    if not (isinstance(block.get("secrecy_rule"), str) and block["secrecy_rule"].strip()):
        errors.append(f"{ref}: archive_visibility needs a 'secrecy_rule'")
    if "released_through" in block and not is_year_or_iso_date(block["released_through"]):
        errors.append(f"{ref}: archive_visibility 'released_through' must be a year or an ISO date")
    if not is_iso_date(block.get("as_of")):
        errors.append(f"{ref}: archive_visibility needs an ISO 'as_of' date - a release horizon moves")
    bad = _record_grade_refs(item, block.get("record_anchor"))
    if not block.get("record_anchor") or bad:
        errors.append(f"{ref}: archive_visibility needs a record-grade 'record_anchor'"
                      + (f": {', '.join(bad)}" if bad else ""))

    for index, row in enumerate(block.get("case_status") or [], start=1):
        label = f"archive_visibility case_status #{index}"
        if not isinstance(row, dict):
            errors.append(f"{ref}: {label} must be a mapping")
            continue
        if row.get("case") not in case_slugs:
            errors.append(f"{ref}: {label} 'case' must be a published case slug")
        if not is_valid_archive_state(row.get("status")):
            errors.append(
                f"{ref}: {label} 'status' must be one of: {', '.join(sorted(ARCHIVE_VISIBILITY_STATES))}"
            )
        if not (isinstance(row.get("note"), str) and row["note"].strip()):
            errors.append(f"{ref}: {label} needs a 'note'")
    return errors



def validate_pattern_context(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """A case may declare, per pattern, that its instance belongs to a wider
    context shared with other cases - one institution, one legal regime, one
    apparatus. Declaring it is what stops two observations of one regime being
    counted as two independent replications.

    Declaring none is not an omission: a case that shares nothing with another is
    its own context, which is what every entry written before this rule assumed.
    """
    ref = f"{cluster_name}/{source_file}"
    block = item.get("pattern_context")
    if block is None:
        return []
    if not isinstance(block, dict) or not block:
        return [f"{ref}: 'pattern_context' must be a non-empty mapping when present"]

    errors: list[str] = []
    declared_patterns = set(item.get("patterns") or [])
    for pattern, context in block.items():
        if pattern not in declared_patterns:
            errors.append(
                f"{ref}: pattern_context names '{pattern}', which this case does not declare as a pattern"
            )
        if not is_valid_recurrence_context(context):
            errors.append(
                f"{ref}: unknown recurrence context {context!r} "
                f"(known: {', '.join(sorted(RECURRENCE_CONTEXTS))})"
            )
    return errors


def validate_seo(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """The SEO contract: what this page says it is, to a reader and to a crawler.

    None of it may change what the entry claims - it governs presentation only -
    but it is enforced as data rather than left to whoever writes the next page.
    """
    ref = f"{cluster_name}/{source_file}"
    block = item.get("seo")
    required = cluster_name in SEO_CONTRACT_CLUSTERS

    if block is None:
        return [f"{ref}: entries in '{cluster_name}' need an 'seo' contract "
                f"({', '.join(SEO_CONTRACT_FIELDS)})"] if required else []
    if not isinstance(block, dict):
        return [f"{ref}: 'seo' must be a mapping"]

    errors: list[str] = []
    for field in SEO_CONTRACT_FIELDS:
        if field not in block:
            errors.append(f"{ref}: seo contract is missing '{field}'")
    unknown = sorted(set(block) - set(SEO_CONTRACT_FIELDS))
    if unknown:
        errors.append(f"{ref}: seo contract has unknown field(s): {', '.join(unknown)}")

    def text(field: str) -> str | None:
        value = block.get(field)
        if value is None:
            return None
        if not (isinstance(value, str) and value.strip()):
            errors.append(f"{ref}: seo '{field}' must be non-empty text")
            return None
        return value.strip()

    def path_list(field: str, allow_empty: bool = False) -> list[str]:
        value = block.get(field)
        if value is None:
            return []
        if not isinstance(value, list) or (not value and not allow_empty):
            errors.append(f"{ref}: seo '{field}' must be a non-empty list of site paths")
            return []
        out = []
        for entry in value:
            if not is_canonical_path(entry):
                errors.append(
                    f"{ref}: seo '{field}' entry {entry!r} must be a clean site path - "
                    f"absolute, no trailing slash, no .html, no query or fragment"
                )
            else:
                out.append(entry)
        return out

    query = text("primary_query")
    title = text("title")
    description = text("description")
    h1 = text("h1")
    canonical = block.get("canonical")

    entities = block.get("secondary_entities")
    if entities is not None and (
        not isinstance(entities, list) or not entities
        or not all(isinstance(e, str) and e.strip() for e in entities)
    ):
        errors.append(f"{ref}: seo 'secondary_entities' must be a non-empty list of entity names")

    if title is not None:
        if not title.endswith(SEO_BRAND_SUFFIX):
            errors.append(f"{ref}: seo 'title' must end with {SEO_BRAND_SUFFIX!r}")
        if len(title) > SEO_TITLE_MAX:
            errors.append(f"{ref}: seo 'title' is {len(title)} characters, over the {SEO_TITLE_MAX} limit")
        if query and query.lower() not in title.lower():
            errors.append(
                f"{ref}: seo 'title' does not contain the primary query {query!r} - "
                f"a result heading that omits the entity name cannot be matched to it"
            )

    if description is not None and not (SEO_DESCRIPTION_MIN <= len(description) <= SEO_DESCRIPTION_MAX):
        errors.append(
            f"{ref}: seo 'description' is {len(description)} characters; "
            f"it must be between {SEO_DESCRIPTION_MIN} and {SEO_DESCRIPTION_MAX}"
        )

    # The H1 names the entity; the thesis belongs in a subheading. A page may
    # legitimately target a narrower query than its own name - a legitimacy
    # assessment of an award is not the same page as that award's anatomy - so
    # the rule is that the heading and the query must share their entity, in
    # either direction, not that one must quote the other exactly.
    if h1 is not None and query:
        low_h1, low_q = h1.lower(), query.lower()
        if low_q not in low_h1 and low_h1 not in low_q:
            errors.append(
                f"{ref}: seo 'h1' {h1!r} and primary query {query!r} share no entity - the heading "
                f"must name what the query asks for"
            )

    if canonical is not None and not is_canonical_path(canonical):
        errors.append(
            f"{ref}: seo 'canonical' must be a clean site path - absolute, no trailing slash, no .html"
        )

    schema_types = block.get("schema_types")
    if schema_types is not None:
        # A page may legitimately emit no page-level structured data; what it may
        # not do is emit a type it never declared, which the gate checks against
        # the built HTML.
        if not isinstance(schema_types, list):
            errors.append(f"{ref}: seo 'schema_types' must be a list")
        else:
            for value in schema_types:
                if not is_valid_schema_type(value):
                    errors.append(f"{ref}: seo 'schema_types' has unsupported type {value!r}")
            # The site root has no breadcrumb trail to emit - it IS the root - so
            # the required type is waived there and nowhere else.
            missing = (frozenset() if canonical == "/" else SEO_REQUIRED_SCHEMA_TYPES) - set(schema_types)
            if missing:
                errors.append(f"{ref}: seo 'schema_types' must include {', '.join(sorted(missing))}")

    path_list("incoming_links")
    path_list("outgoing_links")

    indexing = block.get("indexing")
    if indexing is not None and indexing not in SEO_INDEXING_STATES:
        errors.append(
            f"{ref}: seo 'indexing' must be one of: {', '.join(sorted(SEO_INDEXING_STATES))}"
        )

    return errors


def validate_concept_type(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """Every concept declares what kind of thing it is. Only a `mechanism` can
    be evidenced or refuted in a single case; the other kinds structure the
    project's reasoning without ever being case-level claims."""
    if cluster_name != "concepts":
        return []
    value = item.get("concept_type")
    if value is None:
        return [f"{cluster_name}/{source_file}: a concept must declare a 'concept_type' "
                f"(one of: {', '.join(sorted(CONCEPT_TYPES))})"]
    if not is_valid_concept_type(value):
        return [f"{cluster_name}/{source_file}: unknown concept_type '{value}' "
                f"(expected one of: {', '.join(sorted(CONCEPT_TYPES))})"]
    return []


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



def validate_mechanism_reaudit(
    cluster_name: str, item: dict[str, Any], source_file: str, mechanism_slugs: set[str]
) -> list[str]:
    """A re-audit remediates a historical audit defect without erasing it.

    The original audit stays exactly as it was performed, `incomplete_at_revision`
    included, because it is a dated record of what happened. The re-audit is a
    second dated record saying the search was run again, under today's revision
    and therefore against the whole ontology - not only the mechanism the first
    audit missed. Re-opening an audit and testing one concept would produce a
    second partial record and call it a fix.

    The two are kept separate so the corpus can always say: the original audit
    was incomplete; a later re-audit remediated it. Rewriting the original would
    make the past look complete, which it was not.
    """
    ref = f"{cluster_name}/{source_file}"
    reaudit = item.get("mechanism_reaudit")
    if reaudit is None:
        return []
    if not isinstance(reaudit, dict):
        return [f"{ref}: 'mechanism_reaudit' must be a mapping when present"]

    original = item.get("mechanism_audit")
    if not isinstance(original, dict):
        return [f"{ref}: a mechanism_reaudit remediates a mechanism_audit, and this entry has none"]

    errors: list[str] = []
    if not is_iso_date(reaudit.get("search_date")):
        errors.append(f"{ref}: mechanism_reaudit needs an ISO 'search_date'")
    elif is_iso_date(original.get("search_date")) and reaudit["search_date"] < original["search_date"]:
        errors.append(f"{ref}: mechanism_reaudit predates the audit it remediates")

    # The revision rules apply unchanged, which is the point: a re-audit runs
    # under the current revision, so MOR-006 forbids it declaring a gap.
    errors.extend(_validate_audit_revision(f"{ref} reaudit", reaudit))
    # A re-audit must be recorded at the revision in force when it ran, which the
    # gate can only check by ordering: it may not be older than the audit it
    # repairs, or it repairs nothing. Requiring it to EQUAL the current revision
    # was the first shape of this rule and it was wrong - it would have failed
    # every existing re-audit the moment the ontology moved again, which is
    # retroactive invalidation of a dated search. Whether a re-audit still covers
    # today's mechanism set is a measurement, reported as currency, not a gate.
    revision = reaudit.get("ontology_revision")
    if revision == LEGACY_REVISION_UNRESOLVED:
        errors.append(
            f"{ref}: a mechanism_reaudit is performed now, so its revision is always establishable "
            f"and may not be recorded as unresolved"
        )
    elif revision_is_before(revision, str(original.get("ontology_revision"))):
        errors.append(
            f"{ref}: mechanism_reaudit is recorded at {revision}, older than the "
            f"{original.get('ontology_revision')} audit it repairs - a re-audit under a smaller "
            f"ontology cannot remediate a search performed under a larger one"
        )

    considered = [c for c in (reaudit.get("considered") or []) if isinstance(c, str)]
    ineligible = [c for c in considered if c not in mechanism_slugs]
    if ineligible:
        errors.append(f"{ref}: mechanism_reaudit considered {', '.join(ineligible)}, which is not "
                      f"an audit-eligible concept")

    # What it remediates, stated against the original rather than retyped.
    remediates = reaudit.get("remediates")
    if not isinstance(remediates, dict):
        errors.append(f"{ref}: mechanism_reaudit needs a 'remediates' block naming the audit it "
                      f"repairs (its revision, its date, and what it left untested)")
    else:
        if remediates.get("original_revision") != original.get("ontology_revision"):
            errors.append(f"{ref}: remediates.original_revision must match the audit's recorded "
                          f"revision ({original.get('ontology_revision')})")
        if remediates.get("original_search_date") != original.get("search_date"):
            errors.append(f"{ref}: remediates.original_search_date must match the audit's own date")
        declared = sorted(remediates.get("untested_then") or [])
        if declared != sorted(original.get("incomplete_at_revision") or []):
            errors.append(
                f"{ref}: remediates.untested_then must restate the audit's own "
                f"'incomplete_at_revision' exactly "
                f"(expected: {', '.join(sorted(original.get('incomplete_at_revision') or [])) or 'none'})"
            )

    # A verdict per mechanism tested. A bare `considered` list can say a
    # mechanism was tested without saying what the test found, which is the
    # thinness this remediation exists to remove.
    verdicts = reaudit.get("verdicts")
    if not isinstance(verdicts, list) or not verdicts:
        errors.append(f"{ref}: mechanism_reaudit needs a 'verdicts' list, one entry per mechanism "
                      f"considered")
        return errors

    seen: dict[str, str] = {}
    for index, row in enumerate(verdicts, start=1):
        if not isinstance(row, dict):
            errors.append(f"{ref}: mechanism_reaudit verdict #{index} must be a mapping")
            continue
        mechanism = row.get("mechanism")
        if mechanism in seen:
            errors.append(f"{ref}: mechanism_reaudit returns two verdicts for {mechanism}")
        if not is_valid_mechanism_verdict(row.get("verdict")):
            errors.append(f"{ref}: mechanism_reaudit verdict for {mechanism} must be one of: "
                          f"{', '.join(sorted(MECHANISM_VERDICTS))}")
        if not (isinstance(row.get("note"), str) and row["note"].strip()):
            errors.append(f"{ref}: mechanism_reaudit verdict for {mechanism} needs a note stating "
                          f"what the record did and did not show")
        if isinstance(mechanism, str):
            seen[mechanism] = row.get("verdict")

    if sorted(seen) != sorted(set(considered)):
        errors.append(
            f"{ref}: mechanism_reaudit must return a verdict for exactly the mechanisms it "
            f"considered (missing: {', '.join(sorted(set(considered) - set(seen))) or 'none'}; "
            f"unexpected: {', '.join(sorted(set(seen) - set(considered))) or 'none'})"
        )

    # The re-audit is the current statement of record, so what it supports must
    # be what the case declares. Anything else lets a page and its audit disagree.
    supported = sorted(m for m, v in seen.items() if v == "supported")
    declared_patterns = sorted(p for p in (item.get("patterns") or []) if isinstance(p, str))
    if supported != declared_patterns:
        errors.append(
            f"{ref}: mechanism_reaudit supports {', '.join(supported) or 'nothing'}, but the case "
            f"declares patterns {', '.join(declared_patterns) or 'none'}"
        )

    finding = reaudit.get("finding")
    if not is_valid_mechanism_finding(finding):
        errors.append(f"{ref}: mechanism_reaudit 'finding' must be one of: "
                      f"{', '.join(sorted(MECHANISM_FINDINGS))}")
    elif (finding == "mechanism-evidenced") != bool(supported):
        errors.append(f"{ref}: mechanism_reaudit 'finding' disagrees with its own verdicts")

    if not (isinstance(reaudit.get("note"), str) and reaudit["note"].strip()):
        errors.append(f"{ref}: mechanism_reaudit needs an overall 'note'")

    for field in ("patterns_changed", "scores_changed"):
        if not isinstance(reaudit.get(field), bool):
            errors.append(f"{ref}: mechanism_reaudit must state '{field}' explicitly (true/false), "
                          f"so a re-audit that moved nothing says so rather than leaving it to be "
                          f"inferred from a diff")

    sources = item.get("sources") if isinstance(item.get("sources"), list) else []
    for ref_index in reaudit.get("best_sources") or []:
        if not isinstance(ref_index, int) or not (1 <= ref_index <= len(sources)):
            errors.append(f"{ref}: mechanism_reaudit best_sources reference #{ref_index} does not exist")
    return errors



def validate_concept_corpus_claim(
    cluster_name: str, item: dict[str, Any], source_file: str
) -> list[str]:
    """A concept page may claim documented cases only when the engine counts some.

    The claim used to be boilerplate: every concept page carried "Definition &
    Documented Cases" whether the corpus evidenced the concept eleven times, once,
    or never. A title is a claim about the record, and the boilerplate outlived
    the evidence in three places - including a mechanism that a complete re-audit
    had just found in no case at all.

    The check reads the engine rather than a hand-maintained list, so the claim
    cannot drift from the count again: remove the last case evidencing a concept
    and the page that still advertises cases fails the build.
    """
    if cluster_name != "concepts" or not is_published(item):
        return []
    seo = item.get("seo")
    if not isinstance(seo, dict):
        return []

    claimed: list[tuple[str, str]] = []
    for field in ("title", "description", "h1"):
        for phrase in asserts_corpus_cases(seo.get(field)):
            claimed.append((field, phrase))
    if not claimed:
        return []

    from domain_comparison import concept_corpus_support  # local: engine import
    support = concept_corpus_support(item.get("slug"))
    if support["n_cases"]:
        return []

    ref = f"{cluster_name}/{source_file}"
    where = ", ".join(f"{field} claims {phrase!r}" for field, phrase in claimed)
    kind = item.get("concept_type")
    reason = (
        "no case in the corpus evidences it"
        if kind in AUDIT_ELIGIBLE_CONCEPT_TYPES else
        f"a concept of type '{kind}' cannot be evidenced by a case at all"
    )
    return [
        f"{ref}: {where}, but {reason}. A page may not advertise evidence the engine "
        f"does not count."
    ]



def validate_score_calibration(
    cluster_name: str, item: dict[str, Any], source_file: str
) -> list[str]:
    """A domain outside the sciences may not publish a score before its
    calibration is written down.

    The instrument is domain-neutral; its dimension NAMES are not. "Independent
    verification" means one thing in the definition and suggests another in a
    field with no experiments, and the suggestion is what a scorer imports when
    nothing has said otherwise. The calibration is the saying-otherwise, and it
    has to exist before the first score rather than after the first argument
    about one.

    It must account for every input a score depends on - each dimension plus the
    recognition side - either by restating it or by recording that it carries
    over unchanged. Silence about a dimension is precisely where an imported
    assumption survives, so silence is what fails.
    """
    if cluster_name != "unawarded" or not is_published(item):
        return []
    if not isinstance(item.get("assessment"), dict):
        return []
    domain = item.get("domain")
    if domain not in CALIBRATION_REQUIRED_DOMAINS:
        return []

    ref = f"{cluster_name}/{source_file}"
    calibration = domain_calibration(domain)
    if not calibration:
        return [
            f"{ref}: {domain} requires a published score calibration before its first scored case "
            f"(DOMAIN_SCORE_CALIBRATION in config.py). The instrument carries over; the reading of "
            f"its dimensions into a new domain does not carry over silently."
        ]
    covered = calibration_inputs(calibration)
    missing = [k for k in SCORE_INPUT_KEYS if not covered.get(k, "").strip()]
    if missing:
        return [
            f"{ref}: the {domain} calibration leaves {', '.join(missing)} unaddressed. Every score "
            f"input must be either restated for this domain or recorded as carried over unchanged."
        ]
    return []



def validate_assessment_scope(
    cluster_name: str, item: dict[str, Any], source_file: str
) -> list[str]:
    """An RLS score is evidence about what it was scored over, and nothing else.

    A recognition system that governs several categories under one name is the
    easy case to get wrong: the score was fixed by sources describing some of
    them, and extending the system's `domains` costs one line and silently
    converts that score into evidence for a category nobody assessed. The Nobel
    Prize System is exactly that shape - its track-record rationale says "most
    scientific selections", and adding literature to its domains would make that
    sentence a claim about literature.

    So a system may record what its assessment covers and what it explicitly does
    not. `covers` must equal `domains`, so the two cannot drift; a domain named in
    `excludes` may never appear in `domains`; and every exclusion carries a reason,
    because the point is to record a decision rather than a preference. Reversing
    one then requires deleting a written reason, which is a deliberate act that
    leaves a trace.
    """
    if cluster_name != "recognition-systems":
        return []
    ref = f"{cluster_name}/{source_file}"
    scope = item.get("assessment_scope")

    # The rule was bypassable for a day: the check returned early when no scope
    # was declared, so the way to escape a requirement about multi-domain scores
    # was to declare nothing at all - and the corpus's own oldest multi-domain
    # entry was doing exactly that. A score is a claim about what it was
    # evidenced over, so every scored system states that, and omission is the one
    # thing it may not do.
    if scope is None:
        if is_published(item) and isinstance(item.get("rls_assessment"), dict):
            return [
                f"{ref}: a published system carrying an 'rls_assessment' must declare an "
                f"'assessment_scope'. A score with no stated scope is a claim with no stated "
                f"reach, and it is how a multi-domain score avoids having to justify itself."
            ]
        return []
    if not isinstance(scope, dict):
        return [f"{ref}: 'assessment_scope' must be a mapping when present"]

    errors: list[str] = []
    covers = scope.get("covers")
    if not isinstance(covers, list) or not covers:
        errors.append(f"{ref}: assessment_scope needs a non-empty 'covers' list")
        covers = []
    if not (isinstance(scope.get("note"), str) and scope["note"].strip()):
        errors.append(f"{ref}: assessment_scope needs a 'note' stating what the score was "
                      f"evidenced over")

    declared = list(item.get("domains") or [])
    if covers and sorted(map(str, covers)) != sorted(map(str, declared)):
        errors.append(
            f"{ref}: assessment_scope 'covers' must match the system's 'domains' exactly "
            f"(covers: {', '.join(sorted(map(str, covers))) or 'none'}; domains: "
            f"{', '.join(sorted(map(str, declared))) or 'none'}). A system cannot govern a domain "
            f"its assessment does not claim to cover."
        )

    # The sharing rule. Preflight 3 recorded that an RLS scores a deciding body
    # rather than a foundation, and the requalification that followed showed the
    # phrasing was too tight: one deciding body may legitimately be assessed over
    # several domains, and several deciding bodies may not be assessed under one
    # score unless the evidence shows the five dimensions are materially shared.
    # A multi-domain scope must therefore say which it is, per dimension, rather
    # than leaving a reader to assume the architecture is common because the name
    # is. The shared entry this rule replaces asserted five dimensions over two
    # deciding bodies, and two of the five turned out not to be shared at all.
    if len(covers) > 1:
        shared = scope.get("shared_architecture")
        if not isinstance(shared, dict) or not shared:
            errors.append(
                f"{ref}: an assessment covering more than one domain must declare "
                f"'shared_architecture' - for each scored dimension, the evidence that it is "
                f"materially shared across everything this score covers. Several deciding bodies "
                f"may share one RLS only where that is shown, not where the name is common."
            )
        else:
            missing = [k for k in RLS_KEYS if not str(shared.get(k, "")).strip()]
            if missing:
                errors.append(
                    f"{ref}: 'shared_architecture' leaves {', '.join(missing)} unaddressed. Every "
                    f"scored dimension must be shown materially shared, because a score is only as "
                    f"portable as its least portable dimension."
                )

    excludes = scope.get("excludes")
    if excludes is None:
        return errors
    if not isinstance(excludes, list) or not excludes:
        return errors + [f"{ref}: assessment_scope 'excludes' must be a non-empty list when present"]

    for index, row in enumerate(excludes, start=1):
        if not isinstance(row, dict):
            errors.append(f"{ref}: assessment_scope exclusion #{index} must be a mapping")
            continue
        domain = row.get("domain")
        if not (isinstance(domain, str) and is_valid_domain(domain)):
            errors.append(f"{ref}: assessment_scope exclusion #{index} names unregistered domain "
                          f"{domain!r}")
        if not (isinstance(row.get("reason"), str) and row["reason"].strip()):
            errors.append(f"{ref}: assessment_scope exclusion of {domain!r} needs a 'reason' - an "
                          f"exclusion is a recorded decision, not a preference")
        if domain in declared:
            errors.append(
                f"{ref}: {domain!r} is excluded from this system's assessment scope and also "
                f"declared in its 'domains'. Reusing a score as evidence for a domain it excludes "
                f"is the failure this field exists to prevent - widen the assessment on its own "
                f"evidence, or leave the domain to its own system."
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


def _validate_audit_revision(ref: str, audit: dict[str, Any]) -> list[str]:
    """An audit is only interpretable against the ontology it was performed under.
    Without a recorded revision, "considered these five mechanisms" cannot be read
    as either complete or incomplete - the reader has no way to know how many were
    eligible that day, and the number silently drifts as the ontology grows.

    So each audit records its revision, the evidence for that revision, and - for
    audits performed before this model existed - an explicit list of the eligible
    mechanisms it did not test. A gap that is declared is a known defect; a gap
    that is inferred later from a changing denominator is an unnoticed one. The
    declaration is never a substitute for testing going forward: from
    COMPLETENESS_ENFORCED_FROM onward an audit must simply be complete.
    """
    errors: list[str] = []
    revision = audit.get("ontology_revision")
    if not is_valid_ontology_revision(revision):
        errors.append(
            f"{ref}: mechanism_audit needs an 'ontology_revision' (a recorded revision id, or "
            f"'{LEGACY_REVISION_UNRESOLVED}' when history cannot establish one). Without it, "
            f"'considered' cannot be read as complete or incomplete."
        )
        return errors

    basis = audit.get("revision_basis")
    if not (isinstance(basis, str) and basis.strip()):
        errors.append(
            f"{ref}: mechanism_audit needs a 'revision_basis' naming the evidence for its "
            f"ontology_revision (the commit that put it in force, or why none can be established)"
        )

    considered = {c for c in (audit.get("considered") or []) if isinstance(c, str)}
    eligible = revision_mechanisms(revision)
    untested = sorted(eligible - considered)

    declared = audit.get("incomplete_at_revision")
    if declared is None:
        if untested:
            errors.append(
                f"{ref}: mechanism_audit records {revision}, under which "
                f"{', '.join(untested)} {'was' if len(untested) == 1 else 'were'} already "
                f"audit-eligible, but 'considered' does not test "
                f"{'it' if len(untested) == 1 else 'them'}. Either test "
                f"{'it' if len(untested) == 1 else 'them'}, or declare the gap in "
                f"'incomplete_at_revision' - do not adjust the revision to fit the list."
            )
        return errors

    if not isinstance(declared, list) or not declared:
        return errors + [f"{ref}: 'incomplete_at_revision' must be a non-empty list when present"]

    if revision == LEGACY_REVISION_UNRESOLVED:
        return errors + [
            f"{ref}: an audit whose revision is unresolved cannot declare a gap at that revision - "
            f"nothing is established about what was eligible"
        ]

    if not revision_is_before(revision, COMPLETENESS_ENFORCED_FROM):
        return errors + [
            f"{ref}: 'incomplete_at_revision' is only available to audits performed before "
            f"{COMPLETENESS_ENFORCED_FROM}. An audit recorded at {revision} must test every "
            f"audit-eligible mechanism."
        ]

    overlap = sorted(set(declared) & considered)
    if overlap:
        errors.append(
            f"{ref}: {', '.join(overlap)} appears in both 'considered' and "
            f"'incomplete_at_revision' - an audit cannot both test and not test a mechanism"
        )
    outside = sorted(m for m in declared if m not in eligible)
    if outside:
        errors.append(
            f"{ref}: 'incomplete_at_revision' names {', '.join(map(str, outside))}, which "
            f"{'was' if len(outside) == 1 else 'were'} not audit-eligible at {revision}. An audit "
            f"cannot fail to test a mechanism that did not yet exist."
        )
    if not outside and sorted(set(declared)) != untested:
        errors.append(
            f"{ref}: 'incomplete_at_revision' must name exactly the eligible mechanisms left "
            f"untested at {revision} (expected: {', '.join(untested) or 'none'})"
        )
    return errors


def validate_mechanism_audit(
    cluster_name: str, item: dict[str, Any], source_file: str, mechanism_slugs: set[str]
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
        ineligible = [c for c in considered if c not in mechanism_slugs]
        if ineligible:
            errors.append(
                f"{ref}: mechanism_audit considered {', '.join(map(str, ineligible))}, which is not an "
                f"audit-eligible concept. Only concept_type "
                f"{', '.join(sorted(AUDIT_ELIGIBLE_CONCEPT_TYPES))} can be tested against a case - an "
                f"umbrella tendency or a framework distinction cannot be a failed mechanism test."
            )

    errors.extend(_validate_audit_revision(ref, audit))

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
    for index, entry in enumerate(item.get("corrections") or [], start=1):
        if isinstance(entry, dict):
            for field in ("was", "now", "reason"):
                if isinstance(entry.get(field), str):
                    blocks.append((f"correction #{index}.{field}", entry[field]))
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

    # A synthesis derives from a corpus, so the domain it names must have one.
    # A planned domain is registered but unassessed: deriving from it would be
    # deriving from nothing, and every figure token would resolve to zero.
    domain = item.get("derives_from")
    if not (isinstance(domain, str) and is_aggregated_domain(domain)):
        errors.append(f"{ref}: a report must declare 'derives_from' naming a domain with an "
                      f"assessed corpus (its evidence is that governed corpus; a planned domain "
                      f"has none)")
        return errors

    for field in ("question", "scope"):
        value = item.get(field)
        if not (isinstance(value, str) and value.strip()):
            errors.append(f"{ref}: a report needs a non-empty '{field}'")

    from synthesis_figures import bare_numbers, cited_tokens, unknown_tokens  # local: engine import

    figures = figure_map_cached(domain, tuple(item.get("compares_with") or ()))
    for other in item.get("compares_with") or []:
        if not is_aggregated_domain(other):
            errors.append(f"{ref}: 'compares_with' names a domain with no assessed corpus: {other}")

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

    corrections = item.get("corrections")
    if corrections is not None:
        if not isinstance(corrections, list) or not corrections:
            errors.append(f"{ref}: 'corrections' must be a non-empty list when present")
        else:
            for index, entry in enumerate(corrections, start=1):
                if not isinstance(entry, dict):
                    errors.append(f"{ref}: correction #{index} must be a mapping")
                    continue
                if not is_iso_date(entry.get("date")):
                    errors.append(f"{ref}: correction #{index} needs an ISO 'date'")
                for field in ("was", "now", "reason"):
                    if not (isinstance(entry.get(field), str) and entry[field].strip()):
                        errors.append(f"{ref}: correction #{index} needs a non-empty '{field}'")

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


_FIGURE_CACHE: dict[tuple[str, tuple[str, ...]], dict[str, str]] = {}


def figure_map_cached(domain: str, compare: tuple[str, ...] = ()) -> dict[str, str]:
    key = (domain, compare)
    if key not in _FIGURE_CACHE:
        from synthesis_figures import figure_map
        _FIGURE_CACHE[key] = figure_map(domain, compare)
    return _FIGURE_CACHE[key]


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

    decides, pays = FUNDING_SEPARATION_REQUIRED
    if decides in architecture and pays not in architecture:
        errors.append(
            f"{cluster_name}/{source_file}: architecture states '{decides}' without '{pays}' - "
            f"who decides and who pays are separate facts, and an anatomy that gives only the first "
            f"lets the reader infer the second. State the funder, or state that it was not reached."
        )
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
    """`domain` (a single value) and `domains` (a list) must reference a domain in
    the registry, and an entry in a domain-scoped cluster must name one.

    An unscoped entry was previously indistinguishable from a deliberate
    exception. That silence let a published award sit outside every domain
    without anything recording whether that was a decision or an oversight, and
    it let the corpus grow a class of entries no domain page could ever reach.
    The exception now has to be declared at cluster level, in config, where it
    can be read - not inferred from an entry that simply omitted a field.
    """
    errors: list[str] = []
    ref = f"{cluster_name}/{source_file}"

    if cluster_name in DOMAIN_SCOPED_CLUSTERS and is_published(item):
        if not item.get("domain") and not item.get("domains"):
            errors.append(
                f"{ref}: a published entry in a domain-scoped cluster must name a registered "
                f"domain. A domain may be 'planned' - naming one says where the entry belongs "
                f"without claiming a corpus for it. Clusters exempt by declared posture: "
                f"{', '.join(sorted(DOMAIN_SCOPE_POSTURES))}."
            )

    domain = item.get("domain")
    if domain is not None and not (isinstance(domain, str) and is_valid_domain(domain)):
        errors.append(
            f"{cluster_name}/{source_file}: unknown domain '{domain}' "
            f"(register it in DOMAIN_REGISTRY in config.py first)"
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
    cluster_name: str, item: dict[str, Any], source_file: str, concept_slugs: set[str],
    mechanism_slugs: set[str] | None = None,
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
        elif mechanism_slugs is not None and slug not in mechanism_slugs:
            errors.append(
                f"{cluster_name}/{source_file}: pattern '{slug}' is not an audit-eligible concept "
                f"(only concept_type {', '.join(sorted(AUDIT_ELIGIBLE_CONCEPT_TYPES))} can be evidenced in a case)"
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


def collect_concept_slugs_by_type(types: frozenset[str] | set[str]) -> set[str]:
    """Published concepts whose declared type is in `types`."""
    slugs: set[str] = set()
    folder = DATA / "concepts"
    if not folder.exists():
        return slugs
    for path in sorted(folder.glob("*.yaml")):
        item = load_yaml_file(path)
        if str(item.get("status", "published")).strip().lower() != "published":
            continue
        if item.get("concept_type") in types and item.get("slug"):
            slugs.add(normalize_slug(str(item["slug"])))
    return slugs


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
    mechanism_slugs = collect_concept_slugs_by_type(AUDIT_ELIGIBLE_CONCEPT_TYPES)
    case_slugs = collect_published_slugs("unawarded")

    for cluster_name in CLUSTERS:
        folder = DATA / cluster_name
        if not folder.exists():
            continue

        for path in sorted(folder.glob("*.yaml")):
            item = load_yaml_file(path)
            item_errors = validate_item(cluster_name, item, path.name, concept_slugs, case_slugs,
                                        mechanism_slugs)
            all_errors.extend(item_errors)

    if all_errors:
        print("Content validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("Content validation passed successfully.")


if __name__ == "__main__":
    main()
