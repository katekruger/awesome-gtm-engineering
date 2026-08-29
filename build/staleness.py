#!/usr/bin/env python3
"""Flag entries with no commits in 12 months, or archived: true.

Only meaningful for entries with a source_code_url — that's the only field
this project has a machine-verified activity signal for (refresh_metadata.py
fills last_commit_at / archived). Commercial closed-source tools have no
such signal and are never flagged by this script.

Per contributing.md: removal is normal, not punitive. Opens one issue per
flagged entry, labeled staleness-review, stating a 14-day objection window
— deduplicated by exact issue title so a standing flag isn't re-filed every
week.
"""
import argparse
import pathlib
import sys
from datetime import datetime, timedelta, timezone

import yaml

import github_issues

ROOT = pathlib.Path(__file__).resolve().parent.parent
STALE_AFTER_DAYS = 365


def parse_timestamp(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def find_stale(tools_dir, as_of):
    """Returns a list of dicts: file, name, reason."""
    stale = []
    for path in sorted(pathlib.Path(tools_dir).glob("*.yml")):
        with open(path) as f:
            tool = yaml.safe_load(f)

        if not tool.get("source_code_url"):
            continue

        if tool.get("archived"):
            stale.append({"file": path.name, "name": tool["name"], "reason": "repository is archived"})
            continue

        last_commit = parse_timestamp(tool.get("last_commit_at"))
        if last_commit and (as_of - last_commit) > timedelta(days=STALE_AFTER_DAYS):
            days = (as_of - last_commit).days
            stale.append({
                "file": path.name,
                "name": tool["name"],
                "reason": f"no commits in {days} days (last commit {tool['last_commit_at']})",
            })

    return stale


def file_issues(stale_entries, repo, token):
    existing_titles = github_issues.list_open_issue_titles(repo, "staleness-review", token)
    filed = 0
    for entry in stale_entries:
        title = f"Staleness review: {entry['name']}"
        body = (
            f"**Entry**: `data/tools/{entry['file']}`\n"
            f"**Reason**: {entry['reason']}\n\n"
            "Per [contributing.md](../contributing.md), removal is normal "
            "and not punitive — a hand-maintained list going stale is the "
            "expected fate of good software that simply isn't being "
            "actively developed anymore, not a mark against the project.\n\n"
            "This issue stays open for **14 days** so the maintainer, "
            "vendor, or any interested contributor can object with evidence "
            "the project is still active. If nothing changes by then, the "
            "entry will be removed."
        )
        if github_issues.create_issue_if_new(repo, title, body, ["staleness-review"], token, existing_titles):
            filed += 1
    return filed


def main(argv=None):
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools-dir", default=str(ROOT / "data" / "tools"))
    args = parser.parse_args(argv)

    as_of = datetime.now(timezone.utc)
    stale_entries = find_stale(args.tools_dir, as_of)

    if not stale_entries:
        print("no stale entries found")
        return 0

    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if token and repo:
        filed = file_issues(stale_entries, repo, token)
        print(f"found {len(stale_entries)} stale entrie(s), filed {filed} new issue(s)")
    else:
        print(f"found {len(stale_entries)} stale entrie(s) (GITHUB_TOKEN/GITHUB_REPOSITORY not set, not filing issues)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
