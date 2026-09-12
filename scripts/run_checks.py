"""Run every machine check in one command:  python scripts/run_checks.py

These are the checks that keep claims and code aligned - frozen statistics,
determinism, denominators, the publication boundary, the sector page's fidelity
to the engine, the synthesis rules, and the SEO contract every governed page
carries. A failure here means a claim the project makes - about its evidence or
about what its pages announce themselves to be - is no longer enforced.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SUITES = ("test_domain_comparison.py", "test_sector_page.py", "test_synthesis.py", "seo_gate.py")


def main() -> None:
    here = Path(__file__).resolve().parent
    failed = []
    for suite in SUITES:
        print(f"\n=== {suite} " + "=" * (60 - len(suite)))
        if subprocess.run([sys.executable, str(here / suite)], check=False).returncode != 0:
            failed.append(suite)
    print("\n" + ("ALL SUITES PASSED" if not failed else f"FAILED SUITES: {', '.join(failed)}"))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
