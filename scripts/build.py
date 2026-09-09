from __future__ import annotations

import shutil
import subprocess
import sys

from config import OUT


def clean_output_dir() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)


def run_step(script_name: str) -> None:
    script_path = OUT.parent / "scripts" / script_name
    result = subprocess.run([sys.executable, str(script_path)], check=False)

    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")


def main() -> None:
    clean_output_dir()

    run_step("validate_content.py")
    run_step("quality_gate.py")
    run_step("generate_core.py")
    run_step("generate_pages.py")
    run_step("generate_rankings.py")
    run_step("generate_sitemap.py")

    print("Full build completed successfully.")

    # Informational: report domain maturity against the Definition of Done,
    # and the source-grade provenance audit. Neither fails the build; an
    # immature domain or a claim resting on secondary sources is a status.
    run_step("domain_status.py")
    run_step("source_audit.py")
    run_step("domain_comparison.py")


if __name__ == "__main__":
    main()
