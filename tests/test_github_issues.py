import sys
import pathlib
from unittest.mock import patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import github_issues  # noqa: E402


class FakeResp:
    def __init__(self, status_code, headers=None, json_data=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._json = json_data or []

    def json(self):
        return self._json

    def raise_for_status(self):
        pass


def test_list_open_issue_titles_429_raises_rate_limited():
    with patch.object(github_issues.requests, "get", return_value=FakeResp(429)):
        with pytest.raises(github_issues.RateLimited):
            github_issues.list_open_issue_titles("owner/repo", "label", "token")


def test_list_open_issue_titles_403_remaining_zero_raises_rate_limited():
    resp = FakeResp(403, headers={"X-RateLimit-Remaining": "0"})
    with patch.object(github_issues.requests, "get", return_value=resp):
        with pytest.raises(github_issues.RateLimited):
            github_issues.list_open_issue_titles("owner/repo", "label", "token")


def test_create_issue_if_new_429_raises_rate_limited():
    with patch.object(github_issues.requests, "post", return_value=FakeResp(429)):
        with pytest.raises(github_issues.RateLimited):
            github_issues.create_issue_if_new(
                "owner/repo", "title", "body", ["label"], "token", set()
            )


def test_429_honours_retry_after():
    with patch.object(github_issues.requests, "get", return_value=FakeResp(429, {"Retry-After": "30"})):
        with pytest.raises(github_issues.RateLimited) as exc_info:
            github_issues.list_open_issue_titles("owner/repo", "label", "token")
    assert exc_info.value.args[0] == "30"
