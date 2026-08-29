import json
import sys
import pathlib

import jsonschema

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import build as build_module  # noqa: E402

SCHEMA_DIR = pathlib.Path(__file__).resolve().parent.parent / "build"


def validate_index(index_dict):
    with open(SCHEMA_DIR / "index-schema.json") as f:
        schema = json.load(f)
    resolver = jsonschema.RefResolver(base_uri=f"{SCHEMA_DIR.as_uri()}/", referrer=schema)
    jsonschema.validate(index_dict, schema, resolver=resolver)


def test_index_validates_against_schema(valid_fixture_dir):
    output = build_module.build_index(
        valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools"
    )
    index = json.loads(output)
    validate_index(index)


def test_index_deterministic(valid_fixture_dir):
    first = build_module.build_index(valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools")
    second = build_module.build_index(valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools")
    assert first == second


def test_index_tools_sorted_and_no_internal_fields(valid_fixture_dir):
    output = build_module.build_index(valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools")
    index = json.loads(output)
    names = [t["name"] for t in index["tools"]]
    assert names == sorted(names, key=str.casefold)
    assert all("_source" not in t for t in index["tools"])


def test_index_has_ending_newline(valid_fixture_dir):
    output = build_module.build_index(valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools")
    assert output.endswith("\n")
