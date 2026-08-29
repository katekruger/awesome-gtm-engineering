#!/usr/bin/env python3
"""Generate README.md from data/categories.yml and data/tools/*.yml.

Deterministic: same input always produces the same bytes. Do not add
anything here that depends on wall-clock time, random ordering, or
filesystem iteration order.
"""
import argparse
import pathlib
import re
import sys

import jinja2
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE_DIR = pathlib.Path(__file__).resolve().parent / "templates"

# Mirrors github-slugger's ASCII punctuation strip: everything is kept except
# this set, spaces become hyphens, and — critically — consecutive hyphens are
# NOT collapsed. "Enrichment & Data" must become "enrichment--data" to match
# the anchor GitHub actually generates for the rendered heading; a naive
# single-hyphen slug fails awesome-lint's ToC-link-must-match-heading-anchor
# check even though the text looks identical.
_SLUG_STRIP = re.compile(r"[!\"#$%&'()*+,./:;<=>?@\[\\\]^`{|}~]")


def github_slug(text):
    return _SLUG_STRIP.sub("", text.lower()).replace(" ", "-")


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


def load_categories(categories_file):
    with open(categories_file) as f:
        return yaml.safe_load(f)


def load_tools(tools_dir):
    tools = []
    for path in sorted(pathlib.Path(tools_dir).glob("*.yml")):
        with open(path) as f:
            tool = yaml.safe_load(f)
        tool["_source"] = path.name
        tools.append(tool)
    return tools


def group_by_category(categories, tools):
    by_slug = {
        c["slug"]: {**c, "anchor": github_slug(c["name"]), "tools": []}
        for c in categories
    }
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
        # Stable, case-insensitive, alphabetical — the whole point is that
        # running this twice on unchanged data produces byte-identical output.
        cat["tools"].sort(key=lambda t: t["name"].casefold())
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
    output = template.render(categories=categories)
    if not output.endswith("\n"):
        output += "\n"
    return output


def build(categories_file, tools_dir):
    categories = load_categories(categories_file)
    tools = load_tools(tools_dir)
    grouped = group_by_category(categories, tools)
    return render(grouped), len(tools), len(grouped)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--categories-file", default=str(ROOT / "data" / "categories.yml"))
    parser.add_argument("--tools-dir", default=str(ROOT / "data" / "tools"))
    parser.add_argument("--output", default=str(ROOT / "README.md"))
    args = parser.parse_args(argv)

    output, tool_count, category_count = build(args.categories_file, args.tools_dir)
    pathlib.Path(args.output).write_text(output)
    print(f"wrote {args.output} — {tool_count} entries across {category_count} categories")


if __name__ == "__main__":
    sys.exit(main())
