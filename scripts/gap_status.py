"""Coverage of the Governed Admission Pipeline:  python scripts/gap_status.py

Prints what each admission layer is meant to decide, what actually enforces it,
and where that enforcement runs - generated from the registry in config.py rather
than typed. A standard that described its aspirations as controls would be the
same defect this project keeps finding in its own claims, so the report exists to
make the distance between the two visible on every run.

Two axes, deliberately. A control that refuses what it names is not a gate until
something invokes it on a change and a failure stops the merge.
"""
from __future__ import annotations

from pathlib import Path

from config import (
    GAP_DECISIONS, GAP_ENFORCEMENT, GAP_LAYERS, GAP_VERSION, gap_coverage,
)

IMPL_MARK = {"enforced": "[x]", "partial": "[~]", "absent": "[ ]"}
ENF_MARK = {"required": "GATE", "ci-observed": "watch", "local-only": "manual", "none": "-"}


def main() -> None:
    here = Path(__file__).resolve().parent
    print(f"ChampionsAwards - Governed Admission Pipeline ({GAP_VERSION})")
    print("=" * 68)
    print("Decision states: " + ", ".join(GAP_DECISIONS))
    print()
    for layer in GAP_LAYERS:
        impl, enf = str(layer["implementation"]), str(layer["enforcement"])
        parts = [c for c in layer["components"] if (here / str(c)).exists()]
        missing = [c for c in layer["components"] if not (here / str(c)).exists()]
        print(f"{IMPL_MARK[impl]} {layer['id']}  {layer['name']}")
        print(f"      implementation: {impl}    enforcement: {enf}  [{ENF_MARK[enf]}]")
        print(f"      asks: {layer['question']}")
        print(f"      may decide: {', '.join(layer['decisions'])}")
        for decision, rule in (layer.get("decision_rules") or {}).items():
            print(f"        - {decision}: {rule}")
        print(f"      runs: {', '.join(parts) if parts else 'nothing'}"
              + (f"   MISSING: {', '.join(missing)}" if missing else ""))
        print(f"      {layer['note']}")
        print()
    c = gap_coverage()
    total = c["total"]
    i, e = c["implementation"], c["enforcement"]
    print(f"Implementation: {i['enforced']}/{total} enforced, {i['partial']} partial, "
          f"{i['absent']} absent.")
    print("Enforcement:    " + ", ".join(f"{v} {k}" for k, v in e.items() if v))
    print()
    print(f"EFFECTIVELY ENFORCED: {c['effective']}/{total}")
    print("  A layer governs admission only when it is implemented AND required - implemented so")
    print("  that it refuses what it names, required so that a failure stops the merge. Anything")
    print("  short of both is a detector. " + GAP_ENFORCEMENT["required"])


if __name__ == "__main__":
    main()
