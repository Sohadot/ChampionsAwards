from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import shutil
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import CORE_PAGES, DATA, OUT, SRC, TEMPLATES


def load_yaml_file(path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def load_site_config() -> dict[str, Any]:
    return load_yaml_file(DATA / "site.yaml")


def create_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader([str(SRC / "core"), str(TEMPLATES)]),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def copy_assets() -> None:
    assets_src = SRC / "assets"
    assets_out = OUT / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, assets_out, dirs_exist_ok=True)


def copy_root_files() -> None:
    root_files = ["robots.txt", "CNAME"]
    for filename in root_files:
        src_path = OUT.parent / filename
        if src_path.exists():
            shutil.copy2(src_path, OUT / filename)


def render_core_pages(env: Environment, site: dict[str, Any]) -> None:
    common_context = {
        "site": site,
        "build_year": datetime.now(timezone.utc).year,
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    for template_name, output_relative_path in CORE_PAGES.items():
        template = env.get_template(template_name)
        html = template.render(**common_context)

        output_path = OUT / output_relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")


def main() -> None:
    site = load_site_config()
    env = create_environment()
    render_core_pages(env, site)
    copy_assets()
    copy_root_files()
    print("Core pages generated successfully.")


if __name__ == "__main__":
    main()
