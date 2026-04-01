from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import (
    CLUSTERS,
    DATA,
    HUB_TITLES,
    OUT,
    TEMPLATES,
    is_valid_slug,
    normalize_domain,
    normalize_slug,
)


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_site_config() -> dict[str, Any]:
    return load_yaml_file(DATA / "site.yaml")


def create_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def load_cluster_items(cluster_name: str) -> list[dict[str, Any]]:
    folder = DATA / cluster_name
    if not folder.exists():
        return []

    items: list[dict[str, Any]] = []
    for path in sorted(folder.glob("*.yaml")):
        item = load_yaml_file(path)
        item["_source_file"] = path.name
        items.append(item)

    return items


def render_page(env: Environment, template_name: str, output_path, context: dict[str, Any]) -> None:
    template = env.get_template(template_name)
    html = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def build_cluster_item_pages(
    env: Environment,
    site: dict[str, Any],
    cluster_name: str,
    template_name: str,
    common_context: dict[str, Any],
) -> tuple[int, list[dict[str, Any]]]:
    items = load_cluster_items(cluster_name)
    if not items:
        return 0, []

    published_items: list[dict[str, Any]] = []
    generated_count = 0
    domain = normalize_domain(site["domain"])

    for item in items:
        raw_slug = item.get("slug")

        if not raw_slug:
            print(f"Warning: missing slug in {cluster_name}/{item['_source_file']}")
            continue

        slug = normalize_slug(str(raw_slug))
        if not slug:
            print(f"Warning: empty slug after normalization in {cluster_name}/{item['_source_file']}")
            continue

        if not is_valid_slug(slug):
            print(f"Warning: invalid slug '{slug}' in {cluster_name}/{item['_source_file']}")
            continue

        item["slug"] = slug
        item["cluster"] = cluster_name
        item["url"] = f"/{cluster_name}/{slug}"
        item["canonical_url"] = f"{domain}/{cluster_name}/{slug}"

        output_path = OUT / cluster_name / slug / "index.html"

        context = {
            **common_context,
            "item": item,
            "cluster_name": cluster_name,
            "hub_title": HUB_TITLES.get(cluster_name, cluster_name.replace("-", " ").title()),
        }

        render_page(env, template_name, output_path, context)
        published_items.append(item)
        generated_count += 1

    return generated_count, published_items


def build_cluster_hub_page(
    env: Environment,
    site: dict[str, Any],
    cluster_name: str,
    items: list[dict[str, Any]],
    common_context: dict[str, Any],
) -> None:
    if not items:
        return

    output_path = OUT / cluster_name / "index.html"
    context = {
        **common_context,
        "site": site,
        "cluster_name": cluster_name,
        "hub_title": HUB_TITLES.get(cluster_name, cluster_name.replace("-", " ").title()),
        "items": items,
        "hub_url": f"/{cluster_name}",
        "hub_canonical_url": f"{normalize_domain(site['domain'])}/{cluster_name}",
    }

    render_page(env, "hub.html", output_path, context)


def main() -> None:
    site = load_site_config()
    env = create_environment()

    common_context = {
        "site": site,
        "build_year": datetime.now(timezone.utc).year,
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    total_generated = 0

    for cluster_name, template_name in CLUSTERS.items():
        generated_count, published_items = build_cluster_item_pages(
            env=env,
            site=site,
            cluster_name=cluster_name,
            template_name=template_name,
            common_context=common_context,
        )

        if published_items:
            build_cluster_hub_page(
                env=env,
                site=site,
                cluster_name=cluster_name,
                items=published_items,
                common_context=common_context,
            )

        print(
            f"Cluster: {cluster_name} | Generated item pages: {generated_count} | "
            f"Hub page: {'yes' if published_items else 'no'}"
        )

        total_generated += generated_count

    print(f"Cluster generation completed successfully. Total item pages generated: {total_generated}")


if __name__ == "__main__":
    main()
