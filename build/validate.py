#!/usr/bin/env python3
"""Validate data/tools/*.yml against schema.json and enforce structural rules.

Run in CI on every pull request. Exits non-zero on any failure.

Checks, beyond JSON Schema:
  - category minimum of 3 entries, and no category >50% one vendor's
    self-submissions
  - duplicate entries by website_url and by name (awesome-lint's
    double-link rule only catches URL collisions in the rendered README;
    two entries with different URLs but the same name still need to be
    caught here)
  - description starts uppercase, ends in a period, and uses a plain
    hyphen rather than an en dash or em dash anywhere in the entry text
"""
import argparse
import json
import pathlib
import sys

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_FILE = pathlib.Path(__file__).resolve().parent / "schema.json"

DASH_CHARS = {"–": "en dash (–)", "—": "em dash (—)"}


def load_schema(schema_file):
    with open(schema_file) as f:
        return json.load(f)


def load_categories(categories_file):
    with open(categories_file) as f:
        return yaml.safe_load(f)


def load_tools(tools_dir):
    tools = []
    for path in sorted(pathlib.Path(tools_dir).glob("*.yml")):
        with open(path) as f:
            tools.append((path, yaml.safe_load(f)))
    return tools


def check_dashes(tool, path, errors):
    for char, label in DASH_CHARS.items():
        if char in tool.get("name", "") or char in tool.get("description", ""):
            errors.append(f"{path.name}: contains a {label} — use a plain hyphen")


def check_description_format(tool, path, errors):
    description = tool.get("description", "")
    if description and not description[0].isupper():
        errors.append(f"{path.name}: description must start with an uppercase character")
    if description and not description.endswith("."):
        errors.append(f"{path.name}: description must end with a period")


def validate(categories_file, tools_dir, schema_file=SCHEMA_FILE):
    errors = []
    schema = load_schema(schema_file)
    categories = load_categories(categories_file)
    category_names = {c["name"] for c in categories}

    counts = {c["name"]: 0 for c in categories}
    vendor_counts = {c["name"]: 0 for c in categories}

    seen_urls = {}
    seen_names = {}

    tool_files = load_tools(tools_dir)
    for path, tool in tool_files:
        try:
            jsonschema.validate(tool, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{path.name}: {e.message}")
            continue

        check_dashes(tool, path, errors)
        check_description_format(tool, path, errors)

        url = tool["website_url"].rstrip("/").lower()
        if url in seen_urls:
            errors.append(
                f"{path.name}: duplicate website_url, already used by {seen_urls[url]}"
            )
        else:
            seen_urls[url] = path.name

        name_key = tool["name"].strip().casefold()
        if name_key in seen_names:
            errors.append(
                f"{path.name}: duplicate name, already used by {seen_names[name_key]}"
            )
        else:
            seen_names[name_key] = path.name

        for cat_name in tool["categories"]:
            if cat_name not in category_names:
                errors.append(f"{path.name}: unknown category {cat_name!r}")
                continue
            counts[cat_name] += 1
            if tool.get("submitted_by_vendor"):
                vendor_counts[cat_name] += 1

    for cat in categories:
        name, minimum = cat["name"], cat["min_entries"]
        if counts[name] < minimum:
            errors.append(
                f"category {name!r} has {counts[name]} entries, "
                f"needs at least {minimum}"
            )
        elif vendor_counts[name] * 2 > counts[name]:
            errors.append(
                f"category {name!r} is more than 50% one vendor's "
                f"self-submissions ({vendor_counts[name]}/{counts[name]})"
            )

    return errors, len(tool_files), len(categories)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--categories-file", default=str(ROOT / "data" / "categories.yml"))
    parser.add_argument("--tools-dir", default=str(ROOT / "data" / "tools"))
    args = parser.parse_args(argv)

    errors, tool_count, category_count = validate(args.categories_file, args.tools_dir)

    if errors:
        print(f"{len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"{tool_count} entries valid across {category_count} categories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
