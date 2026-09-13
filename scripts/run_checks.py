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

# Directories whose contents decide what the built site should contain.
INPUT_DIRS = ("src", "scripts")


def _newest(root: Path) -> float:
    return max((p.stat().st_mtime for p in root.rglob("*") if p.is_file()), default=0.0)


def assert_build_is_current(project: Path) -> None:
    """Three of these four suites read the BUILT site, not the sources. Run
    against a stale `public/` they answer a question nobody asked - about the
    site as it was some edits ago - and they answer it confidently, in both
    directions: a gate failure for a page the current sources do emit, and a
    gate pass for a page they no longer do. Both happened while opening a domain.

    So staleness is refused rather than tolerated. This is not a build step: the
    checks stay fast and read-only, and the operator is told to build.
    """
    out = project / "public"
    if not out.exists():
        raise SystemExit("public/ does not exist - run: python scripts/build.py")
    built = _newest(out)
    newest_input = max(_newest(project / d) for d in INPUT_DIRS if (project / d).exists())
    if newest_input > built:
        raise SystemExit(
            "The built site is older than its inputs, so the suites that read public/ would be "
            "checking a site these sources no longer describe.\n"
            "Run: python scripts/build.py"
        )


def main() -> None:
    here = Path(__file__).resolve().parent
    assert_build_is_current(here.parent)
    failed = []
    for suite in SUITES:
        print(f"\n=== {suite} " + "=" * (60 - len(suite)))
        if subprocess.run([sys.executable, str(here / suite)], check=False).returncode != 0:
            failed.append(suite)
    print("\n" + ("ALL SUITES PASSED" if not failed else f"FAILED SUITES: {', '.join(failed)}"))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
