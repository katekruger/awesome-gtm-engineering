import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import validate as validate_module  # noqa: E402


def test_valid_fixture_passes(valid_fixture_dir):
    errors, tool_count, category_count = validate_module.validate(
        valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools"
    )
    assert errors == []
    assert tool_count == 6
    assert category_count == 2


def test_category_below_minimum_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example"),
            tool_factory(name="B", website_url="https://b.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("needs at least 3" in e for e in errors)


def test_duplicate_url_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://same.example"),
            tool_factory(name="B", website_url="https://same.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("duplicate website_url" in e for e in errors)


def test_duplicate_name_with_different_urls_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="Clay", website_url="https://clay.com"),
            tool_factory(name="clay", website_url="https://clay-other.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("duplicate name" in e for e in errors)


def test_missing_period_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", description="No period here"),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("must end with a period" in e for e in errors)


def test_lowercase_start_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", description="lowercase start."),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("uppercase" in e for e in errors)


def test_en_dash_in_description_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(
                name="A",
                website_url="https://a.example",
                description="Enrichment – with an en dash.",
            ),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("en dash" in e for e in errors)


def test_vendor_capture_over_50_percent_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", submitted_by_vendor=True),
            tool_factory(name="B", website_url="https://b.example", submitted_by_vendor=True),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("50%" in e for e in errors)


def test_unknown_category_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", categories=["Nonexistent"]),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("unknown category" in e for e in errors)


def test_schema_violation_fails(workspace, tool_factory):
    bad = tool_factory(name="A", website_url="https://a.example")
    del bad["has_api"]
    categories_file, tools_dir = workspace(
        tools=[
            bad,
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert len(errors) >= 1
