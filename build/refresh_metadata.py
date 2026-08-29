#!/usr/bin/env python3
"""Refresh the machine-owned metadata block for entries with a source_code_url.

Never hand-edit stargazers_count / last_commit_at / archived / current_release
in data/tools/*.yml — this script is the only writer. Requires GITHUB_TOKEN
in the environment (repo secret in CI, never committed).
"""
import os
import pathlib
import re
import sys

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "data" / "tools"
GITHUB_API = "https://api.github.com"


def parse_owner_repo(source_code_url):
    match = re.match(
        r"https?://github\.com/([^/]+)/([^/]+?)/?$", source_code_url or ""
    )
    return match.groups() if match else None


def fetch_repo_metadata(owner, repo, token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    resp = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    release = None
    release_resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/releases/latest", headers=headers, timeout=30
    )
    if release_resp.status_code == 200:
        release = release_resp.json().get("tag_name")

    return {
        "stargazers_count": data["stargazers_count"],
        "last_commit_at": data["pushed_at"],
        "archived": data["archived"],
        "current_release": release,
    }


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set", file=sys.stderr)
        return 1

    updated = 0
    for path in sorted(TOOLS_DIR.glob("*.yml")):
        with open(path) as f:
            tool = yaml.safe_load(f)
        owner_repo = parse_owner_repo(tool.get("source_code_url"))
        if not owner_repo:
            continue
        try:
            tool.update(fetch_repo_metadata(*owner_repo, token))
        except requests.HTTPError as e:
            print(f"{path.name}: {e}", file=sys.stderr)
            continue
        with open(path, "w") as f:
            yaml.safe_dump(tool, f, sort_keys=False)
        updated += 1

    print(f"refreshed metadata for {updated} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
