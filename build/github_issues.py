"""Shared helper for opening deduplicated GitHub issues from automation scripts.

Both linkcheck.py and staleness.py file one issue per (entry, reason) and
must never re-file the same one on every subsequent run — a weekly workflow
that reopens the same complaint every week is worse than useless. Dedup is
by exact issue title: before creating an issue, list open issues with the
target label and skip creation if one already has the same title.

Deliberately keyed on OPEN issues only — a maintainer who closes a
removal/dead-link/staleness issue without acting on it (rather than fixing
the underlying entry) will see it re-filed on the next run. That is the one
path to a duplicate, and it is treated as correct: "closed" means "handled",
and re-filing on an unhandled-but-closed issue is the failure mode automation
should have (silently forgetting is worse).

Rate limiting: every call here that hits the GitHub API can be rate limited
(403-with-remaining-zero for the primary limit, 429 for secondary limits),
and every caller (refresh_metadata.py, linkcheck.py, staleness.py) must stop
cleanly rather than let it surface as an uncaught requests.HTTPError.
RateLimited is raised here, once, so every caller catches the same
exception instead of each reimplementing the 403/429 check.
"""
import requests

GITHUB_API = "https://api.github.com"


class RateLimited(Exception):
    pass


def _raise_if_rate_limited(resp):
    """GitHub returns 403-with-remaining-zero for the primary rate limit and
    429 for secondary rate limits. Both must stop the caller immediately."""
    is_primary = resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0"
    is_secondary = resp.status_code == 429
    if is_primary or is_secondary:
        reset = resp.headers.get("Retry-After") or resp.headers.get("X-RateLimit-Reset")
        raise RateLimited(reset)


def list_open_issue_titles(repo, label, token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    titles = set()
    page = 1
    while True:
        resp = requests.get(
            f"{GITHUB_API}/repos/{repo}/issues",
            headers=headers,
            params={"state": "open", "labels": label, "per_page": 100, "page": page},
            timeout=30,
        )
        _raise_if_rate_limited(resp)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        titles.update(issue["title"] for issue in batch)
        if len(batch) < 100:
            break
        page += 1
    return titles


def create_issue_if_new(repo, title, body, labels, token, existing_titles):
    """Returns True if a new issue was created, False if one with this exact
    title was already open (existing_titles is the set from
    list_open_issue_titles, fetched once per run — not re-fetched per issue,
    to keep this to one list call regardless of how many issues get filed)."""
    if title in existing_titles:
        return False

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    resp = requests.post(
        f"{GITHUB_API}/repos/{repo}/issues",
        headers=headers,
        json={"title": title, "body": body, "labels": labels},
        timeout=30,
    )
    _raise_if_rate_limited(resp)
    resp.raise_for_status()
    existing_titles.add(title)
    return True
