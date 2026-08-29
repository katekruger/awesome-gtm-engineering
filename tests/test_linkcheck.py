import sys
import pathlib
from unittest.mock import patch

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import linkcheck  # noqa: E402


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code

    def raise_for_status(self):
        pass

    def json(self):
        return []

    def close(self):
        pass


class FakeSession:
    """url -> list of status codes, consumed in order (repeats last if exhausted).
    A status of 'raise' raises a RequestException instead of returning."""

    def __init__(self, plan):
        self.plan = {url: list(codes) for url, codes in plan.items()}
        self.calls = []

    def _next(self, url):
        self.calls.append(url)
        codes = self.plan[url]
        code = codes.pop(0) if len(codes) > 1 else codes[0]
        if code == "raise":
            raise requests.RequestException("boom")
        return FakeResponse(code)

    def head(self, url, headers=None, timeout=None, allow_redirects=None):
        return self._next(url)

    def get(self, url, headers=None, timeout=None, allow_redirects=None, stream=None):
        return self._next(url)


def test_check_url_ok():
    session = FakeSession({"https://a.example": [200]})
    assert linkcheck.check_url("https://a.example", session, sleep=lambda s: None) == "ok"


def test_check_url_dead_on_404():
    session = FakeSession({"https://a.example": [404]})
    assert linkcheck.check_url("https://a.example", session, sleep=lambda s: None) == "dead"


def test_check_url_dead_on_connection_error():
    session = FakeSession({"https://a.example": ["raise"]})
    assert linkcheck.check_url("https://a.example", session, sleep=lambda s: None) == "dead"


def test_check_url_inconclusive_on_401():
    # Live API/MCP endpoints routinely 401 a bare unauthenticated request —
    # that's not a dead link, it's the server correctly enforcing auth.
    session = FakeSession({"https://a.example": [401]})
    assert linkcheck.check_url("https://a.example", session, sleep=lambda s: None) == "inconclusive"


def test_check_url_inconclusive_on_403():
    session = FakeSession({"https://a.example": [403]})
    assert linkcheck.check_url("https://a.example", session, sleep=lambda s: None) == "inconclusive"


def test_check_url_dead_on_410():
    session = FakeSession({"https://a.example": [410]})
    assert linkcheck.check_url("https://a.example", session, sleep=lambda s: None) == "dead"


def test_check_url_server_error():
    session = FakeSession({"https://a.example": [500]})
    assert linkcheck.check_url("https://a.example", session, sleep=lambda s: None) == "server_error"


def test_check_url_rate_limited_exhausts_retries():
    session = FakeSession({"https://a.example": [429]})
    slept = []
    result = linkcheck.check_url("https://a.example", session, sleep=slept.append, max_retries=3)
    assert result == "rate_limited"
    assert len(slept) == 3


def test_check_url_rate_limited_then_recovers():
    session = FakeSession({"https://a.example": [429, 429, 200]})
    result = linkcheck.check_url("https://a.example", session, sleep=lambda s: None, max_retries=3)
    assert result == "ok"


def test_hostile_host_skipped(tmp_path, tool_factory):
    import yaml

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool = tool_factory(name="A", website_url="https://www.linkedin.com/company/a")
    (tools_dir / "a.yml").write_text(yaml.safe_dump(tool))

    with patch.object(linkcheck, "check_url") as mock_check:
        dead, skipped = linkcheck.check_all(tools_dir, state={})
        mock_check.assert_not_called()
    assert dead == []
    assert any("linkedin.com" in s for s in skipped)


def test_dead_link_filed_immediately(tmp_path, tool_factory):
    import yaml

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool = tool_factory(name="A", website_url="https://dead.example")
    (tools_dir / "a.yml").write_text(yaml.safe_dump(tool))

    with patch.object(linkcheck, "check_url", return_value="dead"):
        dead, skipped = linkcheck.check_all(tools_dir, state={})

    assert len(dead) == 1
    assert dead[0]["file"] == "a.yml"
    assert dead[0]["field"] == "website_url"


def test_server_error_requires_two_consecutive_runs(tmp_path, tool_factory):
    import yaml

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool = tool_factory(name="A", website_url="https://flaky.example")
    (tools_dir / "a.yml").write_text(yaml.safe_dump(tool))

    state = {}
    with patch.object(linkcheck, "check_url", return_value="server_error"):
        dead, _ = linkcheck.check_all(tools_dir, state=state)
    assert dead == []  # first failure, not filed yet
    assert state["a.yml|website_url"]["consecutive_5xx"] == 1

    with patch.object(linkcheck, "check_url", return_value="server_error"):
        dead, _ = linkcheck.check_all(tools_dir, state=state)
    assert len(dead) == 1  # second consecutive failure, now filed
    assert "a.yml|website_url" not in state  # counter reset after filing


def test_server_error_recovery_resets_state(tmp_path, tool_factory):
    import yaml

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool = tool_factory(name="A", website_url="https://flaky.example")
    (tools_dir / "a.yml").write_text(yaml.safe_dump(tool))

    state = {"a.yml|website_url": {"consecutive_5xx": 1}}
    with patch.object(linkcheck, "check_url", return_value="ok"):
        dead, _ = linkcheck.check_all(tools_dir, state=state)
    assert dead == []
    assert "a.yml|website_url" not in state


def test_inconclusive_never_filed(tmp_path, tool_factory):
    import yaml

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool = tool_factory(name="A", website_url="https://real-but-auth-gated.example")
    (tools_dir / "a.yml").write_text(yaml.safe_dump(tool))

    with patch.object(linkcheck, "check_url", return_value="inconclusive"):
        dead, skipped = linkcheck.check_all(tools_dir, state={})
    assert dead == []
    assert len(skipped) == 1


def test_rate_limited_never_filed(tmp_path, tool_factory):
    import yaml

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool = tool_factory(name="A", website_url="https://ratelimited.example")
    (tools_dir / "a.yml").write_text(yaml.safe_dump(tool))

    with patch.object(linkcheck, "check_url", return_value="rate_limited"):
        dead, skipped = linkcheck.check_all(tools_dir, state={})
    assert dead == []
    assert len(skipped) == 1


def test_a_deliberately_broken_link_opens_exactly_one_issue(tmp_path, tool_factory):
    """Definition of done: a deliberately broken link opens exactly one
    issue, and re-running the check does not file a duplicate."""
    import yaml
    import github_issues

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    tool = tool_factory(name="A", website_url="https://dead.example")
    (tools_dir / "a.yml").write_text(yaml.safe_dump(tool))

    created_issues = []

    def fake_post(url, headers=None, json=None, timeout=None):
        created_issues.append(json["title"])
        return FakeResponse(201)

    with patch.object(linkcheck, "check_url", return_value="dead"):
        dead, _ = linkcheck.check_all(tools_dir, state={})

    existing_titles = set()
    with patch("github_issues.requests.post", side_effect=fake_post):
        filed = 0
        for link in dead:
            title = f"Dead link: {link['file']} ({link['field']})"
            if github_issues.create_issue_if_new(
                "owner/repo", title, "body", ["dead-link"], "token", existing_titles
            ):
                filed += 1

    assert filed == 1
    assert len(created_issues) == 1

    # Second run: same dead link found again, but the issue already exists.
    with patch.object(linkcheck, "check_url", return_value="dead"):
        dead2, _ = linkcheck.check_all(tools_dir, state={})

    with patch("github_issues.requests.post", side_effect=fake_post):
        filed_second_run = 0
        for link in dead2:
            title = f"Dead link: {link['file']} ({link['field']})"
            if github_issues.create_issue_if_new(
                "owner/repo", title, "body", ["dead-link"], "token", existing_titles
            ):
                filed_second_run += 1

    assert filed_second_run == 0
    assert len(created_issues) == 1
