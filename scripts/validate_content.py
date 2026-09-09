from __future__ import annotations

from typing import Any

import yaml

from config import (
    CLUSTERS,
    DATA,
    DDI_KEYS,
    MIN_SUMMARY_LENGTH,
    REQUIRED_FIELDS_BY_CLUSTER,
    RLS_KEYS,
    VALID_STATUSES,
    is_valid_domain,
    is_valid_slug,
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
    must resolve to a published concept, so the ontology stays connected."""
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

    return errors


def collect_published_concept_slugs() -> set[str]:
    slugs: set[str] = set()
    folder = DATA / "concepts"
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
    concept_slugs = collect_published_concept_slugs()

    for cluster_name in CLUSTERS:
        folder = DATA / cluster_name
        if not folder.exists():
            continue

        for path in sorted(folder.glob("*.yaml")):
            item = load_yaml_file(path)
            item_errors = validate_item(cluster_name, item, path.name, concept_slugs)
            all_errors.extend(item_errors)

    if all_errors:
        print("Content validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("Content validation passed successfully.")


if __name__ == "__main__":
    main()
