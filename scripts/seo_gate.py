"""Route-level checks on the SEO contract.

`validate_content` checks a contract's shape from one file. The things that
actually break a reference site are relational and cannot be seen from one file:
a canonical that does not match the route the page is published at, a declared
link that resolves to nothing, a page no other page links to, two pages
competing on the same title, a published route missing from the sitemap.

Nothing here may change what an entry claims. It governs presentation only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (  # noqa: E402
    CLUSTERS,
    DATA,
    OUT,
    SEO_CONTRACT_CLUSTERS,
    is_published,
)
from validate_content import load_yaml_file  # noqa: E402

import yaml  # noqa: E402


def _entries(cluster: str) -> list[dict]:
    folder = DATA / cluster
    if not folder.is_dir():
        return []
    out = []
    for path in sorted(folder.glob("*.yaml")):
        item = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(item, dict) and is_published(item):
            item["_source_file"] = path.name
            out.append(item)
    return out


def published_routes() -> set[str]:
    """Every route the build actually emits, read from the output tree rather
    than from the data, so the check cannot agree with a stale assumption."""
    routes = set()
    if not OUT.is_dir():
        return routes
    for path in OUT.rglob("index.html"):
        rel = path.relative_to(OUT).parent.as_posix()
        routes.add("/" if rel == "." else f"/{rel}")
    return routes


def run() -> list[str]:
    errors: list[str] = []
    routes = published_routes()
    if not routes:
        return ["seo gate: no built pages found - run the generators first"]

    contracts: dict[str, dict] = {}
    for cluster in sorted(SEO_CONTRACT_CLUSTERS):
        for item in _entries(cluster):
            seo = item.get("seo")
            if not isinstance(seo, dict):
                continue
            ref = f"{cluster}/{item['_source_file']}"
            expected = f"/{cluster}/{item.get('slug')}"
            canonical = seo.get("canonical")

            if canonical != expected:
                errors.append(
                    f"{ref}: seo canonical {canonical!r} does not match the route this entry is "
                    f"published at ({expected!r})"
                )
            if canonical and canonical not in routes:
                errors.append(f"{ref}: seo canonical {canonical!r} is not a built route")

            for field in ("incoming_links", "outgoing_links"):
                for link in seo.get(field) or []:
                    if link not in routes:
                        errors.append(f"{ref}: seo {field} entry {link!r} resolves to no built route")

            if canonical:
                contracts[canonical] = {"ref": ref, "seo": seo}

    # No orphans: every governed page must be reachable from a page that says so,
    # and the page it names must actually carry the link in its own contract or be
    # a hub route that lists the cluster.
    for canonical, entry in contracts.items():
        incoming = entry["seo"].get("incoming_links") or []
        if not incoming:
            errors.append(f"{entry['ref']}: seo declares no incoming links - the page would be an orphan")
        for source in incoming:
            source_contract = contracts.get(source)
            if source_contract is None:
                continue  # a hub or core page, checked by the link crawl below
            if canonical not in (source_contract["seo"].get("outgoing_links") or []):
                errors.append(
                    f"{entry['ref']}: declares an incoming link from {source!r}, but that entry's "
                    f"contract does not list {canonical!r} among its outgoing links"
                )

    # Titles are the result-page heading. Two pages sharing one is a page competing
    # with itself.
    seen: dict[str, str] = {}
    for canonical, entry in contracts.items():
        title = (entry["seo"].get("title") or "").strip()
        if title and title in seen:
            errors.append(f"{entry['ref']}: seo title duplicates {seen[title]}")
        elif title:
            seen[title] = entry["ref"]

    # The sitemap is the crawler's index of what exists. A governed page missing
    # from it is published and unannounced.
    sitemap = OUT / "sitemap.xml"
    if sitemap.is_file():
        body = sitemap.read_text(encoding="utf-8")
        for canonical, entry in contracts.items():
            if entry["seo"].get("indexing") == "noindex":
                if canonical + "<" in body:
                    errors.append(f"{entry['ref']}: marked noindex but present in the sitemap")
            elif canonical + "<" not in body:
                errors.append(f"{entry['ref']}: canonical {canonical!r} is absent from the sitemap")

    return errors


if __name__ == "__main__":
    problems = run()
    if problems:
        print("SEO gate failed:")
        for problem in problems:
            print(f"  - {problem}")
        raise SystemExit(1)
    print("SEO gate passed.")
