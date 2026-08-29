#!/usr/bin/env python3
"""Validate data/tools/*.yml against schema.json and enforce category minimums.

Run in CI on every pull request. Exits non-zero on any failure.
"""
import json
import pathlib
import sys

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TOOLS_DIR = DATA / "tools"


def main():
    errors = []

    with open(pathlib.Path(__file__).resolve().parent / "schema.json") as f:
        schema = json.load(f)

    with open(DATA / "categories.yml") as f:
        categories = yaml.safe_load(f)
    category_names = {c["name"] for c in categories}

    counts = {c["name"]: 0 for c in categories}
    vendor_counts = {c["name"]: 0 for c in categories}

    tool_files = sorted(TOOLS_DIR.glob("*.yml"))
    for path in tool_files:
        with open(path) as f:
            tool = yaml.safe_load(f)
        try:
            jsonschema.validate(tool, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{path.name}: {e.message}")
            continue
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

    if errors:
        print(f"{len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"{len(tool_files)} entries valid across {len(categories)} categories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
