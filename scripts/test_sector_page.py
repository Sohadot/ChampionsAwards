"""Machine checks for the sector reference page. Run:  python scripts/test_sector_page.py

The sector page is a representation of the engine, so these checks ask one
question in several ways: does the page say anything the engine did not compute?
"""
from __future__ import annotations

from config import OUT, PUBLISHED_SECTORS
import domain_comparison as dc
import generate_sectors as gs

DOMAIN = "physics-astronomy"
failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    print(("PASS" if condition else "FAIL") + f"  {name}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


site = gs.load_site()
sector = gs.build_sector(DOMAIN, site)
engine = dc.build_comparison(DOMAIN)
corpus = engine["observations"]["corpus_distribution"]
patterns = engine["observations"]["structural_patterns"]

# 1. The page is a representation, not a second calculation.
check("sector figures come from the engine unchanged",
      sector["corpus"] == corpus and sector["patterns"] == patterns)
check("sector carries the engine's snapshot id", sector["corpus_snapshot"] == engine["corpus_snapshot"])
check("sector is dated by data_through, not by build time",
      sector["population"]["data_through"] == engine["population"]["data_through"]
      and "snapshot_date" not in sector["population"])

# 2. The distribution figure plots every case, once, inside the axis.
figure = sector["figure"]
check("figure plots one point per case", len(figure["points"]) == corpus["n_cases"])
check("median line sits inside the interquartile box",
      figure["box_x"] <= figure["median_x"] <= figure["box_x"] + figure["box_w"])
check("whiskers span at least the box",
      figure["whisker_lo"] <= figure["box_x"] and figure["whisker_hi"] >= figure["box_x"] + figure["box_w"])
check("figure geometry is deterministic", gs.gap_figure(corpus) == figure)

# 3. Every generated reading carries its denominator and no generalisation.
check("no banned or generalising language in generated readings", not gs.lint_generated_prose(sector), 
      str(gs.lint_generated_prose(sector)))
top = patterns["patterns"][0]
check("top mechanism reading states support over the denominator",
      f"{top['support']} of {top['denominator']}" in sector["pattern_readings"][0],
      sector["pattern_readings"][0])
check("gap reading states the case denominator",
      f"{corpus['n_cases']} governed cases" in sector["gap_reading"])

# 4. Maturity is reported as measured, including what is not met.
measured = {row["requirement"]: (row["have"], row["need"]) for row in sector["dod_rows"]}
check("pattern maturity reports the established count, not the total",
      measured["patterns"][0] == patterns["established_count"], str(measured))
check("maturity flag matches the measurements",
      sector["mature"] == all(row["met"] for row in sector["dod_rows"]))

# 5. Systems are profiled, not ranked: fixed alphabetical order, no podium.
check("systems are ordered alphabetically, not by score",
      [p["title"] for p in sector["profiles"]] == sorted(p["title"] for p in sector["profiles"]))

# 6. Award relations are split without loss, against their own denominator.
for award in sector["award_entries"]:
    check(f"award relations split without loss ({award['title']})",
          len(award["outcomes"]) + len(award["constraints"]) == sector["awards"]["denominator"])

# 7. Publication boundary: the sector page is HTML; no data endpoint is emitted.
if OUT.exists():
    check("no JSON endpoint under public/", not list(OUT.rglob("*.json")))
    for domain in PUBLISHED_SECTORS:
        page = OUT / "sectors" / domain / "index.html"
        if page.is_file():
            html = page.read_text(encoding="utf-8")
            check(f"published page carries the corpus caveat ({domain})",
                  "corpus frequency is not field prevalence" in html.lower())
            check(f"published page carries the reference form ({domain})",
                  sector["reference_form"] in html)
            check(f"published page states the methodological boundary ({domain})",
                  "What this page does not claim" in html)

print("\n" + ("ALL CHECKS PASSED" if not failures else f"{len(failures)} CHECK(S) FAILED: {failures}"))
raise SystemExit(1 if failures else 0)
