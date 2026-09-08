from __future__ import annotations

from typing import Any

import yaml

from config import (
    CLUSTERS,
    DATA,
    DDI_KEYS,
    MIN_SUMMARY_LENGTH,
    REQUIRED_FIELDS_BY_CLUSTER,
    is_valid_slug,
    normalize_slug,
)


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def validate_item(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
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

    errors.extend(validate_sources(cluster_name, item, source_file))
    errors.extend(validate_assessment(cluster_name, item, source_file))

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


def main() -> None:
    all_errors: list[str] = []

    for cluster_name in CLUSTERS:
        folder = DATA / cluster_name
        if not folder.exists():
            continue

        for path in sorted(folder.glob("*.yaml")):
            item = load_yaml_file(path)
            item_errors = validate_item(cluster_name, item, path.name)
            all_errors.extend(item_errors)

    if all_errors:
        print("Content validation failed:")
        for error in all_errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("Content validation passed successfully.")


if __name__ == "__main__":
    main()
