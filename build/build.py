#!/usr/bin/env python3
"""Generate README.md from data/categories.yml and data/tools/*.yml.

Deterministic: same input always produces the same bytes. Do not add
anything here that depends on wall-clock time, random ordering, or
filesystem iteration order.
"""
import pathlib
import sys

import jinja2
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TOOLS_DIR = DATA / "tools"
TEMPLATE_DIR = pathlib.Path(__file__).resolve().parent / "templates"


def legend(tool):
    marks = []
    marks.append("🔓" if tool["pricing_model"] == "open_source" else None)
    marks.append("💰" if tool["pricing_model"] == "commercial" else None)
    marks.append("🧩" if tool["pricing_model"] in ("freemium", "open_core") else None)
    marks.append("🔌" if tool.get("has_api") else None)
    if tool.get("has_mcp_server"):
        marks.append("🎖️🤖" if tool.get("mcp_server_kind") == "official" else "🤖")
    marks.append("⌨️" if tool.get("has_cli") else None)
    marks.append("🏠" if tool.get("self_hostable") else None)
    marks = [m for m in marks if m]
    return f" {''.join(marks)}" if marks else ""


def load_categories():
    with open(DATA / "categories.yml") as f:
        return yaml.safe_load(f)


def load_tools():
    tools = []
    for path in sorted(TOOLS_DIR.glob("*.yml")):
        with open(path) as f:
            tool = yaml.safe_load(f)
        tool["_source"] = path.name
        tools.append(tool)
    return tools


def group_by_category(categories, tools):
    by_slug = {c["slug"]: {**c, "tools": []} for c in categories}
    for tool in tools:
        for cat_name in tool["categories"]:
            slug = next(
                (c["slug"] for c in categories if c["name"] == cat_name), None
            )
            if slug is None:
                raise ValueError(
                    f"{tool['_source']}: unknown category {cat_name!r}"
                )
            by_slug[slug]["tools"].append(tool)
    for cat in by_slug.values():
        cat["tools"].sort(key=lambda t: t["name"].lower())
    return list(by_slug.values())


def render(categories):
    for cat in categories:
        for tool in cat["tools"]:
            tool["legend"] = legend(tool)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("readme.md.j2")
    return template.render(categories=categories)


def main():
    categories = load_categories()
    tools = load_tools()
    grouped = group_by_category(categories, tools)
    output = render(grouped)
    (ROOT / "README.md").write_text(output)
    print(f"wrote README.md — {len(tools)} entries across {len(grouped)} categories")


if __name__ == "__main__":
    sys.exit(main())
