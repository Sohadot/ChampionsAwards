from __future__ import annotations

from collections import defaultdict
from typing import Any

import yaml

from config import (
    ASSESSMENT_CLUSTERS,
    CLUSTERS,
    DATA,
    DDI_KEYS,
    REQUIRE_DOMAIN,
    REQUIRE_LAST_REVIEWED,
    REQUIRE_OBSERVED_RECOGNITION,
    REQUIRE_PATTERN_EVIDENCE,
    REQUIRE_SOURCES,
    RLS_CLUSTERS,
    RLS_KEYS,
    find_banned_terms,
    get_status,
    is_iso_date,
    is_published,
    is_valid_domain,
    normalize_slug,
)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

# Minimum sourced facts a published entry must carry, so "published" always
# means "load-bearing and checkable", never a bare stub.
MIN_SOURCES_PUBLISHED = 1


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def enforce_publication_policy(cluster_name: str, item: dict[str, Any], source_file: str) -> list[str]:
    """The publication gate. Applies only to entries that declare themselves
    published; drafts are exempt so work-in-progress can live in the repo."""
    ref = f"{cluster_name}/{source_file}"
    errors: list[str] = []

    # Neutrality discipline applies to every entry, published or draft.
    for hit in find_banned_terms(item):
        errors.append(f"{ref}: banned unscoped superlative in {hit} (see /protocol)")

    # Type boundaries are structural: a DDI assessment belongs only on individual
    # contributions, an RLS assessment only on systems. Enforced regardless of status.
    if "assessment" in item and cluster_name not in ASSESSMENT_CLUSTERS:
        errors.append(
            f"{ref}: a DDI 'assessment' is only valid in {sorted(ASSESSMENT_CLUSTERS)} "
            f"(the DDI scores individuals, not this cluster)"
        )
    if "rls_assessment" in item and cluster_name not in RLS_CLUSTERS:
        errors.append(
            f"{ref}: an 'rls_assessment' is only valid in {sorted(RLS_CLUSTERS)} "
            f"(the RLS scores systems, not this cluster)"
        )

    if not is_published(item):
        return errors

    if REQUIRE_SOURCES:
        sources = item.get("sources")
        count = len(sources) if isinstance(sources, list) else 0
        if count < MIN_SOURCES_PUBLISHED:
            errors.append(
                f"{ref}: published entries need at least {MIN_SOURCES_PUBLISHED} source(s); "
                f"mark it 'status: draft' until sourced"
            )

    if REQUIRE_LAST_REVIEWED:
        last_reviewed = item.get("last_reviewed")
        if last_reviewed is None:
            errors.append(f"{ref}: published entries need a 'last_reviewed' date")
        elif not is_iso_date(last_reviewed):
            errors.append(f"{ref}: 'last_reviewed' must be an ISO date (YYYY-MM-DD)")

    # Any assessment on a published entry must justify every dimension, and
    # carry score-level provenance: an evidence trail from each dimension to
    # specific sources (Source -> evidence -> judgment -> score -> gap -> rank).
    required_evidence_keys = {
        "assessment": list(DDI_KEYS) + ["observed_recognition"],
        "rls_assessment": list(RLS_KEYS),
    }
    for block in ("assessment", "rls_assessment"):
        assessment = item.get(block)
        if isinstance(assessment, dict):
            rationale = assessment.get("rationale")
            if not isinstance(rationale, dict) or not rationale:
                errors.append(f"{ref}: a published {block} must include a 'rationale' for its scores")

            evidence = assessment.get("evidence")
            if not isinstance(evidence, dict) or not evidence:
                errors.append(f"{ref}: a published {block} must include 'evidence' mapping each score to sources")
            else:
                missing = [k for k in required_evidence_keys[block] if not evidence.get(k)]
                if missing:
                    errors.append(
                        f"{ref}: {block}.evidence is missing source refs for: {', '.join(missing)}"
                    )

    # A published DDI assessment must state observed_recognition so its
    # recognition gap is computable and the Gap Index is complete.
    if REQUIRE_OBSERVED_RECOGNITION:
        ddi = item.get("assessment")
        if isinstance(ddi, dict) and not _is_number(ddi.get("observed_recognition")):
            errors.append(
                f"{ref}: a published DDI assessment must include a numeric 'observed_recognition' "
                f"(required for the Recognition Gap Index)"
            )

    # Every declared pattern on a published case must carry evidence proving the
    # mechanism, so a pattern is a sourced claim rather than a bare tag.
    if REQUIRE_PATTERN_EVIDENCE:
        patterns = item.get("patterns")
        if isinstance(patterns, list) and patterns:
            pattern_evidence = item.get("pattern_evidence")
            if not isinstance(pattern_evidence, dict) or not pattern_evidence:
                errors.append(f"{ref}: a published entry with 'patterns' must include 'pattern_evidence'")
            else:
                missing = [p for p in patterns if not pattern_evidence.get(p)]
                if missing:
                    errors.append(
                        f"{ref}: pattern_evidence is missing source refs for: {', '.join(missing)}"
                    )

    # Domain placement: no orphaned scored entries. Individuals carry a single
    # 'domain'; systems carry a non-empty 'domains' list.
    if REQUIRE_DOMAIN:
        if cluster_name in ASSESSMENT_CLUSTERS:
            domain = item.get("domain")
            if not (isinstance(domain, str) and is_valid_domain(domain)):
                errors.append(f"{ref}: a published entry here must declare a known 'domain'")
        if cluster_name in RLS_CLUSTERS:
            domains = item.get("domains")
            if not isinstance(domains, list) or not domains:
                errors.append(f"{ref}: a published system must declare a non-empty 'domains' list")

    return errors


def main() -> None:
    errors: list[str] = []
    slug_registry: dict[str, list[str]] = defaultdict(list)
    published_count = 0
    draft_count = 0

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

            if is_published(item):
                published_count += 1
            else:
                draft_count += 1

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

            errors.extend(enforce_publication_policy(cluster_name, item, path.name))

    for key, files in slug_registry.items():
        if len(files) > 1:
            errors.append(f"Duplicate route '{key}' found in files: {', '.join(files)}")

    if errors:
        print("Quality gate failed:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print(
        f"Quality gate passed successfully. Published: {published_count} | Draft (skipped): {draft_count}."
    )


if __name__ == "__main__":
    main()
