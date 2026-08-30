import sys
import pathlib
from unittest.mock import patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import refresh_metadata  # noqa: E402


class FakeResp:
    def __init__(self, status_code, headers=None, json_data=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._json = json_data or {}

    def json(self):
        return self._json

    def raise_for_status(self):
        pass


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


def test_removal_issue_deduplicated_across_runs(tmp_path, monkeypatch):
    """The same 404'd repo run through refresh() twice must file exactly one
    removal issue, not one per run — a daily workflow that re-files the same
    issue every day is worse than useless."""
    import github_issues

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    write_tool(tools_dir, "a.yml", "https://github.com/a/a")

    monkeypatch.setenv("GITHUB_REPOSITORY", "katekruger/awesome-gtm-engineering")

    created_titles = []

    class FakeResponse:
        def __init__(self, json_data):
            self._json = json_data

        def raise_for_status(self):
            pass

        def json(self):
            return self._json

    def fake_get(url, headers=None, params=None, timeout=None):
        return FakeResponse([{"title": t} for t in created_titles])

    def fake_post(url, headers=None, json=None, timeout=None):
        created_titles.append(json["title"])
        return FakeResponse({})

    monkeypatch.setattr(github_issues.requests, "get", fake_get)
    monkeypatch.setattr(github_issues.requests, "post", fake_post)

    with patch.object(refresh_metadata, "fetch_repo_metadata", return_value=None):
        refresh_metadata.refresh(tools_dir, "fake-token")
        refresh_metadata.refresh(tools_dir, "fake-token")

    assert len(created_titles) == 1


def test_429_raises_rate_limited(monkeypatch):
    monkeypatch.setattr(refresh_metadata.requests, "get", lambda *a, **k: FakeResp(429))
    with pytest.raises(refresh_metadata.RateLimited):
        refresh_metadata.fetch_repo_metadata("a", "a", "fake-token")


def test_403_remaining_zero_raises_rate_limited(monkeypatch):
    monkeypatch.setattr(
        refresh_metadata.requests,
        "get",
        lambda *a, **k: FakeResp(403, {"X-RateLimit-Remaining": "0"}),
    )
    with pytest.raises(refresh_metadata.RateLimited):
        refresh_metadata.fetch_repo_metadata("a", "a", "fake-token")


def test_429_honours_retry_after(monkeypatch):
    monkeypatch.setattr(
        refresh_metadata.requests,
        "get",
        lambda *a, **k: FakeResp(429, {"Retry-After": "30"}),
    )
    with pytest.raises(refresh_metadata.RateLimited) as exc_info:
        refresh_metadata.fetch_repo_metadata("a", "a", "fake-token")
    assert exc_info.value.args[0] == "30"


def test_429_on_release_endpoint_raises_rate_limited(monkeypatch):
    responses = [FakeResp(200, json_data={"full_name": "a/a", "stargazers_count": 1, "pushed_at": "x", "archived": False}), FakeResp(429, {"Retry-After": "5"})]

    def fake_get(*a, **k):
        return responses.pop(0)

    monkeypatch.setattr(refresh_metadata.requests, "get", fake_get)
    with pytest.raises(refresh_metadata.RateLimited):
        refresh_metadata.fetch_repo_metadata("a", "a", "fake-token")
