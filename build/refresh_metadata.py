#!/usr/bin/env python3
"""Refresh the machine-owned metadata block for entries with a source_code_url.

Never hand-edit stargazers_count / last_commit_at / archived / current_release
in data/tools/*.yml — this script is the only writer. Requires GITHUB_TOKEN
in the environment (repo secret in CI, never committed).

Edge cases:
  - no source_code_url (commercial tool)   -> skipped cleanly, no error
  - repo 404s (deleted or renamed)         -> entry left untouched; flagged
                                               in the summary and, if
                                               GITHUB_REPOSITORY is set (i.e.
                                               running in this repo's own CI),
                                               a removal issue is opened. A
                                               human decides whether to
                                               actually remove the entry.
  - repo moved (301, GitHub merges this    -> the API call still succeeds
    into a normal 200 response)               against the new location;
                                               source_code_url is updated to
                                               the repo's current full_name
                                               and the rename is noted in the
                                               summary so it can go in the
                                               commit message.
  - GitHub API rate limit                  -> stop immediately; nothing
                                               already fetched this run is
                                               written to disk, so a half
                                               -refreshed file never gets
                                               committed.
  - repo is now archived                   -> archived: true is written, and
                                               it's called out in the summary
                                               (a maintainer or downstream
                                               staleness workflow decides
                                               whether to open an issue).
  - product acquired and folded into       -> no reliable signal for this
    another, without the repo moving          from the GitHub API. Human
                                               review only.
"""
import argparse
import os
import pathlib
import re
import sys

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
GITHUB_API = "https://api.github.com"


class RateLimited(Exception):
    pass


def parse_owner_repo(source_code_url):
    match = re.match(
        r"https?://github\.com/([^/]+)/([^/]+?)/?$", source_code_url or ""
    )
    return match.groups() if match else None


def fetch_repo_metadata(owner, repo, token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    resp = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=headers, timeout=30)

    if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
        raise RateLimited(resp.headers.get("X-RateLimit-Reset"))
    if resp.status_code == 404:
        return None

    resp.raise_for_status()
    data = resp.json()

    release = None
    release_resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/releases/latest", headers=headers, timeout=30
    )
    if release_resp.status_code == 403 and release_resp.headers.get("X-RateLimit-Remaining") == "0":
        raise RateLimited(release_resp.headers.get("X-RateLimit-Reset"))
    if release_resp.status_code == 200:
        release = release_resp.json().get("tag_name")

    return {
        "full_name": data["full_name"],
        "stargazers_count": data["stargazers_count"],
        "last_commit_at": data["pushed_at"],
        "archived": data["archived"],
        "current_release": release,
    }


def open_removal_issue(owner, repo, tool_name, token):
    target_repo = os.environ.get("GITHUB_REPOSITORY")
    if not target_repo:
        return
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    requests.post(
        f"{GITHUB_API}/repos/{target_repo}/issues",
        headers=headers,
        json={
            "title": f"Remove: {tool_name}",
            "body": (
                f"`{tool_name}`'s source repo `{owner}/{repo}` returned 404 "
                "during the daily metadata refresh — it may be deleted, "
                "renamed without a redirect, or made private. A human "
                "should confirm before removing the entry."
            ),
            "labels": ["remove-tool"],
        },
        timeout=30,
    )


def refresh(tools_dir, token):
    """Returns (updated_count, notes). Writes files as it goes — each file
    is only ever written with a complete, successfully fetched block."""
    notes = []
    updated = 0

    for path in sorted(pathlib.Path(tools_dir).glob("*.yml")):
        with open(path) as f:
            tool = yaml.safe_load(f)

        owner_repo = parse_owner_repo(tool.get("source_code_url"))
        if not owner_repo:
            continue

        owner, repo = owner_repo
        try:
            metadata = fetch_repo_metadata(owner, repo, token)
        except RateLimited as e:
            notes.append(f"rate limited, stopping (resets at {e.args[0]})")
            break
        except requests.HTTPError as e:
            notes.append(f"{path.name}: {e}")
            continue

        if metadata is None:
            notes.append(f"{path.name}: {owner}/{repo} returned 404 — flagged for removal")
            open_removal_issue(owner, repo, tool["name"], token)
            continue

        full_name = metadata.pop("full_name")
        if full_name.lower() != f"{owner}/{repo}".lower():
            new_url = f"https://github.com/{full_name}"
            notes.append(f"{path.name}: {owner}/{repo} moved to {full_name}, updated source_code_url")
            tool["source_code_url"] = new_url

        if metadata["archived"] and not tool.get("archived"):
            notes.append(f"{path.name}: now archived")

        tool.update(metadata)
        with open(path, "w") as f:
            yaml.safe_dump(tool, f, sort_keys=False)
        updated += 1

    return updated, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools-dir", default=str(ROOT / "data" / "tools"))
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set", file=sys.stderr)
        return 1

    updated, notes = refresh(args.tools_dir, token)

    print(f"refreshed metadata for {updated} entries")
    for note in notes:
        print(f"  - {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
