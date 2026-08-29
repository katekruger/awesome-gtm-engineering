import sys
import pathlib
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import refresh_metadata  # noqa: E402


def write_tool(tools_dir, filename, source_code_url):
    import yaml

    tool = {
        "name": "A",
        "website_url": "https://a.example",
        "description": "A tool.",
        "categories": ["Enrichment & Data"],
        "pricing_model": "open_source",
        "source_code_url": source_code_url,
        "license": "MIT",
        "has_api": True,
        "has_mcp_server": False,
        "has_cli": False,
        "self_hostable": True,
    }
    (tools_dir / filename).write_text(yaml.safe_dump(tool))


def test_rate_limit_stops_without_partial_write(tmp_path):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", "https://github.com/a/a")
    write_tool(tools_dir, "b.yml", "https://github.com/b/b")

    before = (tools_dir / "b.yml").read_text()

    with patch.object(refresh_metadata, "fetch_repo_metadata", side_effect=refresh_metadata.RateLimited("soon")):
        updated, notes, rate_limited = refresh_metadata.refresh(tools_dir, "fake-token")

    assert rate_limited is True
    assert updated == 0
    # Untouched file must be byte-identical — never partially written.
    assert (tools_dir / "b.yml").read_text() == before


def test_main_exits_nonzero_on_rate_limit(tmp_path, monkeypatch):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", "https://github.com/a/a")

    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    with patch.object(refresh_metadata, "fetch_repo_metadata", side_effect=refresh_metadata.RateLimited("soon")):
        exit_code = refresh_metadata.main(["--tools-dir", str(tools_dir)])

    assert exit_code == 1


def test_main_exits_zero_when_not_rate_limited(tmp_path, monkeypatch):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", None)  # no source_code_url, nothing to fetch

    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    exit_code = refresh_metadata.main(["--tools-dir", str(tools_dir)])
    assert exit_code == 0
