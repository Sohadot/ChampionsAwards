"""Coverage of the Governed Admission Pipeline:  python scripts/gap_status.py

Prints what each admission layer is meant to decide and what actually enforces
it, generated from the registry in config.py rather than typed. A standard that
described its aspirations as controls would be the same defect this project
keeps finding in its own claims, so the report exists to make the distance
between the two visible on every run.
"""
from __future__ import annotations

from pathlib import Path

from config import GAP_DECISIONS, GAP_LAYERS, GAP_VERSION, gap_coverage

MARK = {"enforced": "[x]", "partial": "[~]", "absent": "[ ]"}


def main() -> None:
    here = Path(__file__).resolve().parent
    print(f"ChampionsAwards - Governed Admission Pipeline ({GAP_VERSION})")
    print("=" * 64)
    print("Decision states: " + ", ".join(GAP_DECISIONS))
    print()
    for layer in GAP_LAYERS:
        status = str(layer["status"])
        parts = [c for c in layer["components"] if (here / str(c)).exists()]
        missing = [c for c in layer["components"] if not (here / str(c)).exists()]
        print(f"{MARK[status]} {layer['id']}  {layer['name']}  ({status})")
        print(f"      asks: {layer['question']}")
        print(f"      may decide: {', '.join(layer['decisions'])}")
        print(f"      enforced by: {', '.join(parts) if parts else 'nothing'}"
              + (f"   MISSING: {', '.join(missing)}" if missing else ""))
        print(f"      {layer['note']}")
        print()
    counts = gap_coverage()
    total = sum(counts.values())
    print(f"Coverage: {counts['enforced']}/{total} enforced, {counts['partial']} partial, "
          f"{counts['absent']} absent.")
    print("Reported, not a target. A layer becomes 'enforced' when a component refuses "
          "the thing it names, not when the intention is written down.")


if __name__ == "__main__":
    main()
