from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import (
    ASSESSMENT_CLUSTERS,
    CLUSTERS,
    DATA,
    OUT,
    RLS_CLUSTERS,
    TEMPLATES,
    compute_ddi,
    compute_rls,
    ddi_band,
    is_published,
    normalize_domain,
    normalize_slug,
    recognition_gap_label,
    rls_band,
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


def collect_scored_entries(domain: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Walk every content cluster and pull out published entries that carry a
    computable assessment. Returns (deservingness rows, legitimacy rows)."""
    deservingness: list[dict[str, Any]] = []
    legitimacy: list[dict[str, Any]] = []

    for cluster_name in CLUSTERS:
        folder = DATA / cluster_name
        if not folder.exists():
            continue

        for path in sorted(folder.glob("*.yaml")):
            item = load_yaml_file(path)
            if not is_published(item):
                continue

            raw_slug = item.get("slug")
            if not raw_slug:
                continue
            slug = normalize_slug(str(raw_slug))
            url = f"{domain}/{cluster_name}/{slug}"

            # DDI: only from individual clusters, and only when the gap is computable.
            ddi_assessment = item.get("assessment")
            if cluster_name in ASSESSMENT_CLUSTERS and isinstance(ddi_assessment, dict):
                recognition = ddi_assessment.get("observed_recognition")
                if isinstance(recognition, (int, float)) and not isinstance(recognition, bool):
                    score = compute_ddi(ddi_assessment)
                    gap = score - recognition
                    deservingness.append(
                        {
                            "title": item.get("title", slug),
                            "url": url,
                            "cluster": cluster_name,
                            "score": score,
                            "band": ddi_band(score),
                            "recognition": recognition,
                            "gap": gap,
                            "gap_label": recognition_gap_label(gap),
                        }
                    )

            # RLS: only from system clusters.
            rls_assessment = item.get("rls_assessment")
            if cluster_name in RLS_CLUSTERS and isinstance(rls_assessment, dict):
                score = compute_rls(rls_assessment)
                legitimacy.append(
                    {
                        "title": item.get("title", slug),
                        "url": url,
                        "cluster": cluster_name,
                        "score": score,
                        "band": rls_band(score),
                    }
                )

    # Recognition Gap Index: largest positive gap first, then by raw DDI.
    deservingness.sort(key=lambda r: (r["gap"], r["score"]), reverse=True)
    # Legitimacy Index: strongest legitimacy first.
    legitimacy.sort(key=lambda r: r["score"], reverse=True)
    return deservingness, legitimacy


def build_itemlist(name: str, description: str, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    """A complete schema.org ItemList describing the published ranking order."""
    if not rows:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": name,
        "description": description,
        "itemListOrder": "https://schema.org/ItemListOrderDescending",
        "numberOfItems": len(rows),
        "itemListElement": [
            {"@type": "ListItem", "position": index, "name": row["title"], "url": row["url"]}
            for index, row in enumerate(rows, start=1)
        ],
    }


def main() -> None:
    site = load_site_config()
    domain = normalize_domain(site["domain"])
    env = create_environment()

    deservingness, legitimacy = collect_scored_entries(domain)

    context = {
        "site": site,
        "build_year": datetime.now(timezone.utc).year,
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "deservingness": deservingness,
        "legitimacy": legitimacy,
        "rankings_canonical_url": f"{domain}/rankings",
        "jsonld_deservingness": build_itemlist(
            "Recognition Gap Index",
            "Individuals ranked by recognition gap (assessed DDI minus observed recognition).",
            deservingness,
        ),
        "jsonld_legitimacy": build_itemlist(
            "Recognition Legitimacy Index",
            "Recognition systems ranked by Recognition Legitimacy Score (RLS).",
            legitimacy,
        ),
    }

    output_path = OUT / "rankings" / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(env.get_template("rankings.html").render(**context), encoding="utf-8")

    print(
        f"Rankings generated successfully. Deservingness rows: {len(deservingness)} | "
        f"Legitimacy rows: {len(legitimacy)}."
    )


if __name__ == "__main__":
    main()
