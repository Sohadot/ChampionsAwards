from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import (
    CLUSTERS,
    DATA,
    OUT,
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

            ddi_assessment = item.get("assessment")
            if isinstance(ddi_assessment, dict):
                score = compute_ddi(ddi_assessment)
                recognition = ddi_assessment.get("observed_recognition")
                row = {
                    "title": item.get("title", slug),
                    "url": url,
                    "cluster": cluster_name,
                    "score": score,
                    "band": ddi_band(score),
                }
                if isinstance(recognition, (int, float)):
                    gap = score - recognition
                    row["recognition"] = recognition
                    row["gap"] = gap
                    row["gap_label"] = recognition_gap_label(gap)
                deservingness.append(row)

            rls_assessment = item.get("rls_assessment")
            if isinstance(rls_assessment, dict):
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
    deservingness.sort(key=lambda r: (r.get("gap", float("-inf")), r["score"]), reverse=True)
    # Legitimacy Index: strongest legitimacy first.
    legitimacy.sort(key=lambda r: r["score"], reverse=True)
    return deservingness, legitimacy


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
