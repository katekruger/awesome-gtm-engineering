import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import build as build_module  # noqa: E402


def test_deterministic(valid_fixture_dir):
    categories_file = valid_fixture_dir / "categories.yml"
    tools_dir = valid_fixture_dir / "tools"

    first, _, _ = build_module.build(categories_file, tools_dir)
    second, _, _ = build_module.build(categories_file, tools_dir)

    assert first == second


def test_sorted_alphabetically_case_insensitive(valid_fixture_dir):
    output, _, _ = build_module.build(
        valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools"
    )

    section = output.split("## Outbound & Sequencing")[1].split("## ")[0]
    names = [line.split("]")[0].lstrip("- [") for line in section.splitlines() if line.startswith("- [")]

    assert names == sorted(names, key=str.casefold)


def test_github_slug_matches_actual_github_algorithm():
    # Verified against github-slugger (the library GitHub/remark actually use)
    # for headings containing "&" — a naive single-hyphen slug does not match
    # what GitHub renders, and awesome-lint's ToC rule checks the real anchor.
    assert build_module.github_slug("Enrichment & Data") == "enrichment--data"
    assert build_module.github_slug("Agents & MCP Servers") == "agents--mcp-servers"
    assert build_module.github_slug("Contents") == "contents"


def test_toc_anchors_match_heading_anchors(valid_fixture_dir):
    output, _, _ = build_module.build(
        valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools"
    )
    assert "(#enrichment--data)" in output
    assert "## Enrichment & Data" in output


def test_badge_is_on_the_same_line_as_the_h1(valid_fixture_dir):
    output, _, _ = build_module.build(
        valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools"
    )
    first_line = output.splitlines()[0]
    assert first_line.startswith("# Awesome GTM Engineering")
    assert "https://awesome.re/badge.svg" in first_line
    assert "https://awesome.re" in first_line


def test_ends_with_final_newline(valid_fixture_dir):
    output, _, _ = build_module.build(
        valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools"
    )
    assert output.endswith("\n")
    assert not output.endswith("\n\n\n")


def test_empty_data_still_renders_all_category_headings(workspace):
    categories_file, tools_dir = workspace(tools=[])
    output, tool_count, category_count = build_module.build(categories_file, tools_dir)
    assert tool_count == 0
    assert "## Enrichment & Data" in output
