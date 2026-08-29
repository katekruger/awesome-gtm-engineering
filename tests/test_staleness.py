import sys
import pathlib
from datetime import datetime, timezone
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import staleness  # noqa: E402


AS_OF = datetime(2026, 8, 29, tzinfo=timezone.utc)


def write_tool(tools_dir, filename, **overrides):
    import yaml

    base = {
        "name": "A",
        "website_url": "https://a.example",
        "description": "A tool.",
        "categories": ["Enrichment & Data"],
        "pricing_model": "open_source",
        "source_code_url": "https://github.com/a/a",
        "license": "MIT",
        "has_api": True,
        "has_mcp_server": False,
        "has_cli": False,
        "self_hostable": True,
    }
    base.update(overrides)
    (tools_dir / filename).write_text(yaml.safe_dump(base))


def test_no_source_code_url_never_flagged(tmp_path):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", source_code_url=None, last_commit_at=None)
    assert staleness.find_stale(tools_dir, AS_OF) == []


def test_recent_commit_not_flagged(tmp_path):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", last_commit_at="2026-08-01T00:00:00Z")
    assert staleness.find_stale(tools_dir, AS_OF) == []


def test_stale_commit_flagged(tmp_path):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", last_commit_at="2024-01-01T00:00:00Z")
    stale = staleness.find_stale(tools_dir, AS_OF)
    assert len(stale) == 1
    assert stale[0]["file"] == "a.yml"
    assert "no commits" in stale[0]["reason"]


def test_archived_flagged_regardless_of_last_commit(tmp_path):
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", archived=True, last_commit_at="2026-08-01T00:00:00Z")
    stale = staleness.find_stale(tools_dir, AS_OF)
    assert len(stale) == 1
    assert "archived" in stale[0]["reason"]


def test_a_deliberately_stale_entry_opens_exactly_one_issue(tmp_path):
    """Definition of done: a deliberately stale entry opens exactly one
    issue, and re-running does not file a duplicate."""
    import github_issues

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", last_commit_at="2024-01-01T00:00:00Z")

    stale = staleness.find_stale(tools_dir, AS_OF)
    assert len(stale) == 1

    created = []

    class FakeResponse:
        status_code = 201

        def raise_for_status(self):
            pass

    def fake_post(url, headers=None, json=None, timeout=None):
        created.append(json["title"])
        return FakeResponse()

    existing_titles = set()
    with patch("github_issues.requests.post", side_effect=fake_post):
        filed = 0
        for entry in stale:
            title = f"Staleness review: {entry['name']}"
            if github_issues.create_issue_if_new(
                "owner/repo", title, "body", ["staleness-review"], "token", existing_titles
            ):
                filed += 1
    assert filed == 1
    assert len(created) == 1

    # Second run finds the same stale entry, but the issue already exists.
    stale2 = staleness.find_stale(tools_dir, AS_OF)
    with patch("github_issues.requests.post", side_effect=fake_post):
        filed_second_run = 0
        for entry in stale2:
            title = f"Staleness review: {entry['name']}"
            if github_issues.create_issue_if_new(
                "owner/repo", title, "body", ["staleness-review"], "token", existing_titles
            ):
                filed_second_run += 1
    assert filed_second_run == 0
    assert len(created) == 1
