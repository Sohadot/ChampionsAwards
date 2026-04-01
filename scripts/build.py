from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"


def clean_output_dir() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)


def run_step(script_name: str) -> None:
    script_path = ROOT / "scripts" / script_name
    result = subprocess.run([sys.executable, str(script_path)], check=True)
    if result.returncode != 0:
        raise RuntimeError(f"{script_name} failed")


def main() -> None:
    clean_output_dir()
    run_step("generate_core.py")
    run_step("generate_pages.py")
    run_step("generate_sitemap.py")
    print("Full build completed successfully.")


if __name__ == "__main__":
    main()
