"""Shared helper for opening deduplicated GitHub issues from automation scripts.

Both linkcheck.py and staleness.py file one issue per (entry, reason) and
must never re-file the same one on every subsequent run — a weekly workflow
that reopens the same complaint every week is worse than useless. Dedup is
by exact issue title: before creating an issue, list open issues with the
target label and skip creation if one already has the same title.
"""
import requests

GITHUB_API = "https://api.github.com"


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
    resp.raise_for_status()
    existing_titles.add(title)
    return True
