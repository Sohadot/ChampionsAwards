from __future__ import annotations

from collections import defaultdict
from typing import Any

import yaml

from config import CLUSTERS, DATA, normalize_slug


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def main() -> None:
    errors: list[str] = []
    slug_registry: dict[str, list[str]] = defaultdict(list)

    for cluster_name in CLUSTERS:
        folder = DATA / cluster_name
        if not folder.exists():
            continue

        for path in sorted(folder.glob("*.yaml")):
            item: dict[str, Any] = load_yaml_file(path)
            raw_slug = item.get("slug")
            if not raw_slug:
                continue

            slug = normalize_slug(str(raw_slug))
            if not slug:
                continue

            global_key = f"{cluster_name}/{slug}"
            slug_registry[global_key].append(path.name)

            title = item.get("title")
            summary = item.get("summary")

            if isinstance(title, str) and isinstance(summary, str):
                title_norm = title.strip().lower()
                summary_norm = summary.strip().lower()

                if title_norm and summary_norm and title_norm in summary_norm and len(summary_norm) < 120:
                    errors.append(
                        f"{cluster_name}/{path.name}: summary appears weak or near-placeholder relative to title"
                    )

    for key, files in slug_registry.items():
        if len(files) > 1:
            errors.append(f"Duplicate route '{key}' found in files: {', '.join(files)}")

    if errors:
        print("Quality gate failed:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("Quality gate passed successfully.")


if __name__ == "__main__":
    main()
