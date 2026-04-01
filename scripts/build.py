from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
CORE = SRC / "core"
TEMPLATES = SRC / "templates"
ASSETS = SRC / "assets"
DATA = SRC / "data"
OUT = ROOT / "public"

CORE_PAGES = {
    "index.html": "index.html",
    "protocol.html": "protocol/index.html",
    "framework.html": "framework/index.html",
    "methodology.html": "methodology/index.html",
    "calculator.html": "calculator/index.html",
    "about.html": "about/index.html",
}


def load_site_config() -> dict:
    with (DATA / "site.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def clean_output_dir() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)


def create_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader([str(CORE), str(TEMPLATES)]),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_core_pages(env: Environment, site: dict) -> None:
    common_context = {
        "site": site,
        "build_year": datetime.now(timezone.utc).year,
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    for template_name, output_relative_path in CORE_PAGES.items():
        template = env.get_template(template_name)
        html = template.render(**common_context)
        out_path = OUT / output_relative_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")


def copy_assets() -> None:
    if ASSETS.exists():
        shutil.copytree(ASSETS, OUT / "assets")


def copy_root_files() -> None:
    for filename in ["robots.txt", "CNAME"]:
        src_file = ROOT / filename
        if src_file.exists():
            shutil.copy2(src_file, OUT / filename)


def main() -> None:
    site = load_site_config()
    clean_output_dir()
    env = create_environment()
    render_core_pages(env, site)
    copy_assets()
    copy_root_files()
    print("Core build completed successfully.")


if __name__ == "__main__":
    main()
