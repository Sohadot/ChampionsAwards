from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import (
    AWARD_ARCHITECTURE_FIELDS,
    CLUSTERS,
    DATA,
    DDI_DIMENSIONS,
    HUB_TITLES,
    OUT,
    TEMPLATES,
    RLS_DIMENSIONS,
    SEO_BREADCRUMB_LABELS,
    SEO_ROUTE_ANCHORS,
    route_contract,
    seo_render_vars,
    compute_ddi,
    compute_rls,
    ddi_band,
    is_published,
    is_valid_slug,
    normalize_domain,
    normalize_slug,
    recognition_gap_label,
    rls_band,
)


def attach_assessment(item: dict[str, Any]) -> None:
    """When an entry carries a DDI assessment, compute its score, band, and
    recognition gap at build time so pages never hand-transcribe the numbers."""
    assessment = item.get("assessment")
    if not isinstance(assessment, dict):
        return

    score = compute_ddi(assessment)
    rationale = assessment.get("rationale") or {}
    evidence = assessment.get("evidence") or {}

    item["ddi_score"] = score
    item["ddi_band"] = ddi_band(score)
    item["ddi_rows"] = [
        {
            "label": label,
            "weight": weight,
            "score": assessment.get(key),
            "rationale": rationale.get(key),
            "evidence": evidence.get(key) or [],
        }
        for key, label, weight in DDI_DIMENSIONS
    ]

    recognition = assessment.get("observed_recognition")
    if isinstance(recognition, (int, float)):
        gap = score - recognition
        item["observed_recognition"] = recognition
        item["observed_recognition_evidence"] = evidence.get("observed_recognition") or []
        item["recognition_gap"] = gap
        item["recognition_gap_label"] = recognition_gap_label(gap)


def attach_rls(item: dict[str, Any]) -> None:
    """When a system entry carries an RLS assessment, compute its legitimacy
    score and band at build time (companion to attach_assessment)."""
    assessment = item.get("rls_assessment")
    if not isinstance(assessment, dict):
        return

    score = compute_rls(assessment)
    rationale = assessment.get("rationale") or {}
    evidence = assessment.get("evidence") or {}

    item["rls_score"] = score
    item["rls_band"] = rls_band(score)
    item["rls_rows"] = [
        {
            "label": label,
            "weight": weight,
            "score": assessment.get(key),
            "rationale": rationale.get(key),
            "evidence": evidence.get(key) or [],
        }
        for key, label, weight in RLS_DIMENSIONS
    ]


ARCH_LABELS = dict(AWARD_ARCHITECTURE_FIELDS)


def build_case_index() -> dict[str, dict[str, str]]:
    """slug -> {title, url} for published individual cases, so award pages can
    resolve corpus relations to real, linkable entries."""
    index: dict[str, dict[str, str]] = {}
    folder = DATA / "unawarded"
    if not folder.exists():
        return index
    for path in sorted(folder.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            item = yaml.safe_load(f) or {}
        if str(item.get("status", "published")).strip().lower() != "published":
            continue
        slug = item.get("slug")
        if slug:
            slug = str(slug).strip().strip("/")
            index[slug] = {"title": item.get("title", slug), "url": f"/unawarded/{slug}"}
    return index


def attach_award_architecture(item: dict[str, Any], case_index: dict[str, dict[str, str]]) -> None:
    """Expose the award layers to the template: formal architecture rows
    (each with its provenance anchor), and corpus-interaction relations resolved
    to real cases plus a computed count per architecture element."""
    provenance = item.get("provenance") or {}
    architecture = item.get("architecture")
    if isinstance(architecture, dict):
        rows = []
        for key, label in AWARD_ARCHITECTURE_FIELDS:
            if key not in architecture:
                continue
            prov = provenance.get(f"architecture:{key}") or {}
            rows.append(
                {
                    "label": label,
                    "value": architecture[key],
                    "is_list": isinstance(architecture[key], list),
                    "anchor": prov.get("record_anchor") or [],
                    "basis": prov.get("basis"),
                }
            )
        item["architecture_rows"] = rows

    # Layer 2: historical rule state - what is in force, since when, and whether
    # the version that governed each corpus event is established at all.
    history = item.get("rule_history")
    if isinstance(history, list):
        item["rule_history_rows"] = [
            {
                "label": ARCH_LABELS.get(entry.get("element"), entry.get("element")),
                "current_rule": entry.get("current_rule"),
                "effective_from": entry.get("effective_from"),
                "predecessor_state": entry.get("predecessor_state"),
                "anchor": entry.get("record_anchor") or [],
                "has_exception": bool(entry.get("exception")),
                "events": [
                    {
                        "case_title": (case_index.get(event.get("case")) or {}).get("title", event.get("case")),
                        "case_url": (case_index.get(event.get("case")) or {}).get("url", "#"),
                        "event_date": event.get("event_date"),
                        "established": bool(event.get("established")),
                        "note": event.get("note"),
                    }
                    for event in entry.get("events_covered") or []
                ],
            }
            for entry in history
        ]

    # Layer 3: archive visibility - how far the award's own record is open.
    archive = item.get("archive_visibility")
    if isinstance(archive, dict):
        item["archive_rows"] = [
            {
                "case_title": (case_index.get(row.get("case")) or {}).get("title", row.get("case")),
                "case_url": (case_index.get(row.get("case")) or {}).get("url", "#"),
                "years": row.get("years"),
                "status": row.get("status"),
                "status_label": str(row.get("status") or "").replace("-", " "),
                "note": row.get("note"),
                "anchor": row.get("record_anchor") or [],
            }
            for row in archive.get("case_status") or []
        ]

    relations = item.get("corpus_relations")
    if isinstance(relations, list):
        rel_rows = []
        counts: dict[str, int] = {}
        for rel in relations:
            element = rel.get("architecture_element")
            interaction = rel.get("interaction_type")
            info = case_index.get(rel.get("case"), {})
            rel_rows.append(
                {
                    "case_slug": rel.get("case"),
                    "case_title": info.get("title", rel.get("case")),
                    "case_url": info.get("url", "#"),
                    "element_label": ARCH_LABELS.get(element, element),
                    "interaction": interaction,
                    "interaction_label": (interaction or "").replace("-", " "),
                    "claim": rel.get("claim"),
                    "anchor": rel.get("record_anchor") or [],
                    "has_exception": bool(rel.get("exception")),
                }
            )
            # The comparison variable is the interaction type (homogeneous in
            # meaning), not the architecture element.
            counts[interaction] = counts.get(interaction, 0) + 1
        item["corpus_relation_rows"] = rel_rows
        item["relation_counts"] = sorted(
            ({"label": (k or "").replace("-", " "), "count": v} for k, v in counts.items()),
            key=lambda r: (-r["count"], r["label"]),
        )


def attach_report(item: dict[str, Any]) -> None:
    """A synthesis report states figures as tokens; this resolves them from the
    canonical engine at build time. Nothing numeric on the rendered page was
    typed by an author - validation rejects a bare number in report prose - so a
    report cannot drift from the corpus it derives from.
    """
    domain = item.get("derives_from")
    if not isinstance(domain, str):
        return
    from domain_comparison import build_comparison
    from synthesis_figures import figure_map, resolve

    figures = figure_map(domain, tuple(item.get("compares_with") or ()))
    comparison = build_comparison(domain)

    def r(text: Any) -> Any:
        return resolve(text, figures) if isinstance(text, str) else text

    item["summary"] = r(item.get("summary"))
    item["question"] = r(item.get("question"))
    item["scope"] = r(item.get("scope"))
    item["observation_rows"] = [
        {"statement": r(obs.get("statement")), "derived_from": obs.get("derived_from") or []}
        for obs in item.get("observations") or []
    ]
    item["hypothesis_rows"] = [
        {
            "statement": r(hyp.get("statement")),
            "basis": r(hyp.get("basis")),
            "refuted_by": r(hyp.get("refuted_by")),
            # A refuted hypothesis stays on the page, marked. Removing it would
            # hide the one thing a reader most needs to see: that the corpus was
            # allowed to overturn a published interpretation.
            "state": hyp.get("state", "open"),
            "outcome": r(hyp.get("outcome")),
        }
        for hyp in item.get("hypotheses") or []
    ]
    item["limit_rows"] = [r(limit) for limit in item.get("limits") or []]
    item["correction_rows"] = [
        {"date": entry.get("date"), "was": r(entry.get("was")), "now": r(entry.get("now")),
         "reason": r(entry.get("reason"))}
        for entry in item.get("corrections") or []
    ]
    item["comparison"] = comparison
    item["corpus_cases"] = comparison["observations"]["corpus_distribution"]["ranked_cases"]
    # Only link the sector reference where one is actually published; a report
    # may derive from a domain whose sector page has not been built yet.
    from config import PUBLISHED_SECTORS
    item["sector_url"] = f"/sectors/{domain}" if domain in PUBLISHED_SECTORS else None


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



def attach_seo(item: dict[str, Any], cluster_name: str, slug: str, site_domain: str) -> None:
    """Turn the entry's SEO contract into what the page renders: the title and
    description a result shows, the visible H1, the robots directive, and a
    breadcrumb trail derived from the canonical path.

    Where an entry carries no contract, the old behaviour stands, so this can be
    rolled out cluster by cluster without a silent gap in between.
    """
    seo = item.get("seo") if isinstance(item.get("seo"), dict) else {}
    path = seo.get("canonical") or f"/{cluster_name}/{slug}"

    item["seo_title"] = seo.get("title")
    item["seo_description"] = seo.get("description")
    item["seo_h1"] = seo.get("h1")
    item["seo_robots"] = (
        "noindex,follow" if seo.get("indexing") == "noindex" else "index,follow,max-image-preview:large"
    )

    from config import AWARD_SYSTEM_PAIRS, DOMAINS, PUBLISHED_SECTORS

    trail = [{"name": SEO_BREADCRUMB_LABELS.get("", "Home"), "url": "/"}]
    segments = [part for part in path.split("/") if part]
    if segments:
        cluster_segment = segments[0]
        trail.append({
            "name": SEO_BREADCRUMB_LABELS.get(cluster_segment, cluster_segment.replace("-", " ").title()),
            "url": f"/{cluster_segment}",
        })

    # A domain rung, but only where it resolves. An entry that serves several
    # domains has no single parent, and a domain whose sector page is not yet
    # published would give the crawler and the reader a link to nothing.
    entry_domain = item.get("domain") if isinstance(item.get("domain"), str) else None
    if entry_domain and entry_domain in PUBLISHED_SECTORS:
        trail.append({
            "name": DOMAINS.get(entry_domain, entry_domain.replace("-", " ").title()),
            "url": f"/sectors/{entry_domain}",
        })

    trail.append({"name": item.get("title", slug), "url": path})
    item["breadcrumbs"] = trail
    item["breadcrumb_jsonld"] = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": crumb["name"],
             "item": crumb["url"] if crumb["url"].startswith("http") else site_domain + crumb["url"].rstrip("/")}
            for i, crumb in enumerate(trail, start=1)
        ],
    }



_RELATED_CACHE: dict[str, dict[str, list[dict[str, str]]]] | None = None


def related_links(cluster_name: str, slug: str) -> list[dict[str, str]]:
    """Memoised lookup into the graph built by attach_related."""
    global _RELATED_CACHE
    if _RELATED_CACHE is None:
        items_by_cluster = {c: load_cluster_items(c) for c in CLUSTERS}
        for cluster, items in items_by_cluster.items():
            items_by_cluster[cluster] = [i for i in items if is_published(i) and i.get("slug")]
        attach_related(items_by_cluster)
        _RELATED_CACHE = {
            cluster: {i["slug"]: i.get("related_links") or [] for i in items}
            for cluster, items in items_by_cluster.items()
        }
    return _RELATED_CACHE.get(cluster_name, {}).get(slug, [])


def attach_related(items_by_cluster: dict[str, list[dict[str, Any]]]) -> None:
    """Build the internal graph the SEO contract declares, from the data rather
    than by hand: person to mechanism, person to award, concept to the cases that
    evidence it, system to its own anatomy, report to its sector.

    Anchors are descriptive because a crawler and a reader both learn from the
    anchor text; "read more" teaches neither anything.
    """
    from config import AWARD_SYSTEM_PAIRS, DOMAINS, PUBLISHED_SECTORS

    cases = items_by_cluster.get("unawarded", [])
    concepts = {c["slug"]: c for c in items_by_cluster.get("concepts", [])}
    systems = items_by_cluster.get("recognition-systems", [])
    awards = items_by_cluster.get("awards", [])

    case_title = {c["slug"]: c.get("title", c["slug"]) for c in cases}
    award_for_case: dict[str, list[dict[str, str]]] = {}
    for award in awards:
        for rel in award.get("corpus_relations") or []:
            award_for_case.setdefault(rel["case"], []).append(
                {"url": f"/awards/{award['slug']}", "title": award.get("title", award["slug"])})

    system_by_slug = {s["slug"]: s for s in systems}
    award_by_slug = {a["slug"]: a for a in awards}
    systems_for_award = {a: system_by_slug.get(sysslug)
                         for a, sysslug in AWARD_SYSTEM_PAIRS.items()}
    awards_for_system: dict[str, list[dict[str, Any]]] = {}
    for aslug, sysslug in AWARD_SYSTEM_PAIRS.items():
        if aslug in award_by_slug:
            awards_for_system.setdefault(sysslug, []).append(award_by_slug[aslug])

    for case in cases:
        links = []
        for slug in case.get("patterns") or []:
            concept = concepts.get(slug)
            if concept:
                links.append({
                    "url": f"/concepts/{slug}",
                    "text": f"{concept.get('title', slug)} — the mechanism evidenced in this case",
                })
        for entry in sorted(award_for_case.get(case["slug"], []), key=lambda e: e["url"]):
            links.append({"url": entry["url"],
                          "text": f"{entry['title']} — the award architecture this case meets"})
        domain = case.get("domain")
        if domain in PUBLISHED_SECTORS:
            links.append({"url": f"/sectors/{domain}",
                          "text": f"{DOMAINS.get(domain, domain)} — every governed case in this domain"})
        links.append({"url": "/methodology",
                      "text": "How the Deservingness Index and the recognition gap are computed"})
        case["related_links"] = links

    for slug, concept in concepts.items():
        evidencing = [c for c in cases if slug in (c.get("patterns") or [])]
        links = [{"url": f"/unawarded/{c['slug']}",
                  "text": f"{case_title[c['slug']]} — a governed case evidencing this mechanism"}
                 for c in sorted(evidencing, key=lambda c: c["slug"])]
        links.append({"url": "/methodology",
                      "text": "How a mechanism is evidenced, and what counts as pattern evidence"})
        concept["related_links"] = links

    for system in systems:
        links = []
        for twin in sorted(awards_for_system.get(system["slug"], []), key=lambda a: a["slug"]):
            links.append({"url": f"/awards/{twin['slug']}",
                          "text": f"{twin.get('title')} — the award's formal architecture, rule by rule"})
        for domain in system.get("domains") or []:
            if domain in PUBLISHED_SECTORS:
                links.append({"url": f"/sectors/{domain}",
                              "text": f"{DOMAINS.get(domain, domain)} — the domain this system governs"})
        links.append({"url": "/methodology",
                      "text": "How the Recognition Legitimacy Score is computed"})
        system["related_links"] = links

    for award in awards:
        links = []
        twin = systems_for_award.get(award["slug"])
        if twin:
            links.append({"url": f"/recognition-systems/{twin['slug']}",
                          "text": f"{twin.get('title')} — this system's legitimacy assessment"})
        award["related_links"] = links

    for report in items_by_cluster.get("reports", []):
        domain = report.get("derives_from")
        links = []
        if domain in PUBLISHED_SECTORS:
            links.append({"url": f"/sectors/{domain}",
                          "text": f"{DOMAINS.get(domain, domain)} — the corpus this synthesis derives from"})
        links.append({"url": "/methodology", "text": "The instruments every figure here comes from"})
        report["related_links"] = links


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
    case_index: dict[str, dict[str, str]] | None = None,
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

        if not is_published(item):
            print(f"Skipping draft: {cluster_name}/{item['_source_file']}")
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
        attach_seo(item, cluster_name, slug, domain)
        item["related_links"] = related_links(cluster_name, slug)
        attach_assessment(item)
        attach_rls(item)
        attach_award_architecture(item, case_index or {})
        attach_report(item)

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
        "page": {
            **seo_render_vars(route_contract(f"/{cluster_name}"), f"/{cluster_name}",
                              HUB_TITLES.get(cluster_name, cluster_name)),
            "contract": route_contract(f"/{cluster_name}"),
        },
    }

    render_page(env, "hub.html", output_path, context)


def main() -> None:
    site = load_site_config()
    env = create_environment()

    common_context = {
        "site": site,
        "seo_route_anchors": SEO_ROUTE_ANCHORS,
        "build_year": datetime.now(timezone.utc).year,
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    total_generated = 0
    case_index = build_case_index()

    for cluster_name, template_name in CLUSTERS.items():
        generated_count, published_items = build_cluster_item_pages(
            env=env,
            site=site,
            cluster_name=cluster_name,
            template_name=template_name,
            common_context=common_context,
            case_index=case_index,
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
