from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yaml

from config import CLUSTERS, CORE_URLS, DATA, OUT, normalize_domain


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_site_config() -> dict[str, Any]:
    return load_yaml_file(DATA / "site.yaml")


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


def build_url_entry(loc: str, lastmod: str) -> str:
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
  </url>"""


def main() -> None:
    site = load_site_config()
    domain = normalize_domain(site["domain"])
    lastmod = datetime.now(timezone.utc).date().isoformat()

    urls: list[str] = []

    for core_path in CORE_URLS:
        urls.append(f"{domain}{core_path}")

    for cluster_name in CLUSTERS:
        items = load_cluster_items(cluster_name)

        if items:
            urls.append(f"{domain}/{cluster_name}")

        for item in items:
            slug = item.get("slug")
            if not slug:
                continue
            slug = str(slug).strip().strip("/")
            if not slug:
                continue
            urls.append(f"{domain}/{cluster_name}/{slug}")

    seen = set()
    unique_urls: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for url in unique_urls:
        lines.append(build_url_entry(url, lastmod))

    lines.append("</urlset>")

    (OUT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")
    print(f"Sitemap generated successfully with {len(unique_urls)} URLs.")


if __name__ == "__main__":
    main()
