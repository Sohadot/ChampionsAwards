from __future__ import annotations

from typing import Any

import yaml

from config import (
    CLUSTERS,
    DATA,
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
