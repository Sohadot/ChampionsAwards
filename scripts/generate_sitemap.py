from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "data"
OUT = ROOT / "public"

CORE_URLS = [
    "/",
    "/protocol",
    "/framework",
    "/methodology",
    "/calculator",
    "/about",
]

CLUSTERS = [
    "awards",
    "recognition-systems",
    "concepts",
    "unawarded",
    "sectors",
    "rankings",
    "reports",
    "timeline",
]


def load_yaml_file(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_site_config() -> dict:
    return load_yaml_file(DATA / "site.yaml")


def load_cluster_items(cluster_name: str) -> list[dict]:
    folder = DATA / cluster_name
    if not folder.exists():
        return []

    items: list[dict] = []
    for path in sorted(folder.glob("*.yaml")):
        item = load_yaml_file(path)
        if isinstance(item, dict):
            item["_source_file"] = path.name
            items.append(item)
    return items


def build_url_entry(loc: str, lastmod: str) -> str:
    return f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{lastmod}</lastmod>
  </url>"""


def normalize_domain(domain: str) -> str:
    return domain.rstrip("/")


def main() -> None:
    site = load_site_config()
    domain = normalize_domain(site["domain"])
    lastmod = datetime.now(timezone.utc).date().isoformat()

    urls: list[str] = []

    # الصفحات العليا
    for path in CORE_URLS:
        urls.append(f"{domain}{path}")

    # صفحات العناقيد
    for cluster_name in CLUSTERS:
        items = load_cluster_items(cluster_name)

        # صفحة hub للعنقود نفسه
        if items:
            urls.append(f"{domain}/{cluster_name}")

        # الصفحات المفردة
        for item in items:
            slug = item.get("slug")
            if not slug:
                continue
            urls.append(f"{domain}/{cluster_name}/{slug}")

    # إزالة التكرار مع الحفاظ على الترتيب
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for url in unique_urls:
        lines.append(build_url_entry(url, lastmod))

    lines.append("</urlset>")

    (OUT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")
    print(f"Sitemap generated successfully with {len(unique_urls)} URLs.")


if __name__ == "__main__":
    main()
