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
    PUBLISHED_SECTORS,
    SEO_CONTRACT_CLUSTERS,
    SEO_ROUTE_CONTRACTS,
    is_published,
    sector_route_contract,
)
from validate_content import validate_seo as _validate_seo_shape  # noqa: E402
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

    # Generated routes - hubs, sector references, the methodology pages, the
    # calculator - have no YAML entry to hold a contract, so theirs live in
    # config and are checked by exactly the same rules.
    generated: dict[str, dict] = dict(SEO_ROUTE_CONTRACTS)
    for domain in PUBLISHED_SECTORS:
        generated[f"/sectors/{domain}"] = sector_route_contract(domain)
    for path, seo in generated.items():
        ref = f"route {path}"
        errors.extend(_validate_seo_shape("routes", {"seo": seo}, path))
        if seo.get("canonical") != path:
            errors.append(f"{ref}: contract canonical {seo.get('canonical')!r} is not its own path")
        if path not in routes:
            errors.append(f"{ref}: contract exists for a route the build does not emit")
        for field in ("incoming_links", "outgoing_links"):
            for link in seo.get(field) or []:
                if link not in routes:
                    errors.append(f"{ref}: {field} entry {link!r} resolves to no built route")
        contracts[path] = {"ref": ref, "seo": seo}

    # Every built route must be governed by some contract. An ungoverned route is
    # a page the project publishes and has never said anything about.
    ungoverned = sorted(routes - set(contracts))
    for path in ungoverned:
        errors.append(f"route {path}: is built but has no SEO contract")

    # No orphans, verified against the built graph rather than against two lists
    # agreeing with each other. A declared link is a claim about the site, so it
    # is checked the way every other claim here is: against the artefact.
    import re as _re0

    def links_of(path: str) -> set[str]:
        built = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
        if not built.is_file():
            return set()
        html = built.read_text(encoding="utf-8")
        return {m.rstrip("/") or "/" for m in _re0.findall(r'href="(/[^"#?]*)"', html)}

    link_cache: dict[str, set[str]] = {}

    def links_cached(path: str) -> set[str]:
        if path not in link_cache:
            link_cache[path] = links_of(path)
        return link_cache[path]

    for canonical, entry in contracts.items():
        incoming = entry["seo"].get("incoming_links") or []
        if not incoming and canonical != "/":
            errors.append(f"{entry['ref']}: seo declares no incoming links - the page would be an orphan")
        for source in incoming:
            if canonical not in links_cached(source):
                errors.append(
                    f"{entry['ref']}: declares an incoming link from {source!r}, but the built page "
                    f"there carries no link to {canonical!r}"
                )
        for target in entry["seo"].get("outgoing_links") or []:
            if target not in links_cached(canonical):
                errors.append(
                    f"{entry['ref']}: declares an outgoing link to {target!r}, but the built page "
                    f"carries no link to it"
                )

    # And the graph must actually reach every governed page from somewhere.
    reachable = set()
    for path in routes:
        reachable |= links_cached(path) if path in contracts or path in ("/",) else set()
    for path in routes:
        reachable |= links_cached(path)
    for canonical, entry in contracts.items():
        if canonical != "/" and canonical not in reachable:
            errors.append(f"{entry['ref']}: no built page links to it - it is an orphan")

    # Declared structured data must match what the page actually emits, in both
    # directions. A contract that promises a type the page lacks is a claim about
    # the page; a page that emits a type no contract declares is structured data
    # nobody governed.
    import json as _json
    import re as _re

    for canonical, entry in contracts.items():
        built = OUT / canonical.strip("/") / "index.html"
        if not built.is_file():
            continue
        html = built.read_text(encoding="utf-8")
        emitted = set()
        for block in _re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, _re.S):
            try:
                data = _json.loads(block)
            except Exception:
                errors.append(f"{entry['ref']}: emits JSON-LD that does not parse")
                continue
            if isinstance(data, dict) and isinstance(data.get("@type"), str):
                emitted.add(data["@type"])
        declared = set(entry["seo"].get("schema_types") or [])
        # WebSite is emitted site-wide by the base template, not per page.
        emitted.discard("WebSite")
        if declared - emitted:
            errors.append(
                f"{entry['ref']}: declares schema type(s) the page does not emit: "
                f"{', '.join(sorted(declared - emitted))}"
            )
        if emitted - declared:
            errors.append(
                f"{entry['ref']}: emits undeclared schema type(s): {', '.join(sorted(emitted - declared))}"
            )

    # One page, one query. Two pages competing for the same primary query is one
    # page's traffic split against itself, and usually a sign the two should be
    # answering different questions.
    claimed: dict[str, str] = {}
    for canonical, entry in contracts.items():
        if entry["seo"].get("indexing") == "noindex":
            continue
        query = (entry["seo"].get("primary_query") or "").strip().lower()
        if query and query in claimed:
            errors.append(
                f"{entry['ref']}: primary query {query!r} is already claimed by {claimed[query]} - "
                f"two indexable pages cannot answer the same query"
            )
        elif query:
            claimed[query] = entry["ref"]

    # Every signal must point at the same URL. A canonical is a strong hint, not a
    # command, so the hint only works when the sitemap and the site's own links
    # agree with it.
    for canonical, entry in contracts.items():
        built = OUT / canonical.strip("/") / "index.html"
        if not built.is_file():
            continue
        html = built.read_text(encoding="utf-8")
        match = _re.search(r'<link rel="canonical" href="([^"]+)"', html)
        if not match:
            errors.append(f"{entry['ref']}: built page emits no canonical link")
        else:
            href = match.group(1)
            if not href.endswith(canonical):
                errors.append(
                    f"{entry['ref']}: the built page's canonical {href!r} does not end in the "
                    f"declared path {canonical!r} - the signals disagree"
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
