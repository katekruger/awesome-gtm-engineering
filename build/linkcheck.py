#!/usr/bin/env python3
"""Check every URL field in data/tools/*.yml and file an issue per dead link.

Fields checked: website_url, source_code_url, api_docs_url, mcp_server_url.

This workflow never fails on a broken third-party site — a dead link is
something to report, not a CI failure. It always exits 0; failures are
reported as GitHub issues instead.

Handling, per field failure mode:
  - 429 (rate limited by the target site)  -> retried with exponential
                                               backoff; if still 429 after
                                               retries, skipped for this run
                                               rather than filed as dead —
                                               a rate limit is not evidence
                                               the link is broken.
  - host on the hostile-to-bots allowlist  -> skipped entirely and noted.
                                               These sites (LinkedIn,
                                               Crunchbase, Reddit, ...) 403
                                               anything that isn't a
                                               logged-in browser, so a 403
                                               from them is not a dead-link
                                               signal.
  - 5xx (server error)                     -> requires two CONSECUTIVE runs
                                               of failure before an issue is
                                               filed — a one-off 500 is
                                               normal internet noise, not a
                                               dead link. Consecutive-failure
                                               counts persist across runs in
                                               a small state file.
  - any other 4xx (401, 403, 405, 406, ...) -> skipped and noted, never
                                               filed. A live API or MCP
                                               endpoint routinely answers
                                               with one of these to a bare
                                               unauthenticated request —
                                               that's evidence the server is
                                               up, not that the link is dead.
                                               Confirmed empirically: real
                                               endpoints for HubSpot, Clay,
                                               and Common Room all 401 a
                                               plain GET.
  - 404 or 410                             -> filed immediately, the one
                                               unambiguous "this doesn't
                                               exist" signal, along with a
                                               connection error/timeout/DNS
                                               failure.

One issue per (entry, field), deduplicated by exact title so a standing
dead link doesn't get re-filed every week until someone acts on it.
"""
import argparse
import json
import pathlib
import sys
import time

import requests
import yaml

import github_issues

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE_FILE = pathlib.Path(__file__).resolve().parent / ".linkcheck-state.json"

URL_FIELDS = ["website_url", "source_code_url", "api_docs_url", "mcp_server_url"]

# Sites whose bot/WAF protection reliably 403s anything without a real
# browser session. A 403 from these is not evidence the link is dead.
HOSTILE_HOSTS = {
    "linkedin.com",
    "www.linkedin.com",
    "crunchbase.com",
    "www.crunchbase.com",
    "reddit.com",
    "www.reddit.com",
}

USER_AGENT = "awesome-gtm-engineering-linkcheck/1.0 (+https://github.com/katekruger/awesome-gtm-engineering)"


def hostname(url):
    from urllib.parse import urlparse

    return urlparse(url).hostname or ""


def load_state(state_file):
    state_file = pathlib.Path(state_file)
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {}


def save_state(state_file, state):
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


# Status codes that unambiguously mean "this resource does not exist" for a
# bare, unauthenticated HEAD/GET. Deliberately narrow: a live API or MCP
# endpoint routinely answers 401/403/405/406 to a request with no auth
# header or wrong Accept/method — that's evidence the server is up and
# enforcing its own protocol, not evidence the link is dead. Treating those
# as "dead" produces exactly the false-positive flood this project can't
# afford (verified empirically: real, working MCP endpoints for HubSpot,
# Clay, and Common Room all 401 a plain GET). Only 404/410 are conclusive.
DEAD_STATUS_CODES = {404, 410}


def check_url(url, session, sleep=time.sleep, max_retries=3):
    """Returns one of: 'ok', 'rate_limited', 'dead', 'server_error', 'inconclusive'.

    Uses GET, not HEAD: verified empirically that some real doc sites (e.g.
    Salesforce's developer docs) return a bare 404 to HEAD while GET works
    fine — HEAD support is inconsistent enough across the wild diversity of
    hosts this list points to that it isn't a safe primary probe.

    Streams the response and never reads the body — status_code is
    available as soon as headers arrive, so this doesn't download full
    pages, and critically it doesn't hang on an SSE/streaming MCP endpoint
    that holds the connection open (confirmed: a plain GET without
    stream=True times out completely against smartlead's SSE MCP URL,
    which would misclassify a live streaming endpoint as dead)."""
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(max_retries + 1):
        try:
            resp = session.get(url, headers=headers, timeout=15, allow_redirects=True, stream=True)
            resp.close()
        except requests.RequestException:
            return "dead"

        if resp.status_code == 429:
            if attempt < max_retries:
                sleep(2**attempt)
                continue
            return "rate_limited"

        if 200 <= resp.status_code < 400:
            return "ok"

        if resp.status_code >= 500:
            return "server_error"

        if resp.status_code in DEAD_STATUS_CODES:
            return "dead"

        # Any other 4xx (401, 403, 405, 406, ...): the server responded, it
        # just didn't like an unauthenticated bare request — not evidence
        # of a dead link.
        return "inconclusive"

    return "rate_limited"


def check_all(tools_dir, state, session=None, sleep=time.sleep):
    """Returns (dead_links, skipped_notes). dead_links is a list of dicts
    with keys: file, field, url, reason ('dead' or 'server_error-confirmed')
    — only entries that should actually get an issue filed."""
    session = session or requests.Session()
    dead_links = []
    skipped = []

    for path in sorted(pathlib.Path(tools_dir).glob("*.yml")):
        with open(path) as f:
            tool = yaml.safe_load(f)

        for field in URL_FIELDS:
            url = tool.get(field)
            if not url:
                continue

            host = hostname(url)
            if host in HOSTILE_HOSTS:
                skipped.append(f"{path.name}:{field} — {host} is on the bot-hostile allowlist, skipped")
                continue

            state_key = f"{path.name}|{field}"
            result = check_url(url, session, sleep=sleep)

            if result == "ok":
                state.pop(state_key, None)
                continue

            if result == "rate_limited":
                skipped.append(f"{path.name}:{field} — still 429 after retries, skipped this run")
                continue

            if result == "inconclusive":
                state.pop(state_key, None)
                skipped.append(f"{path.name}:{field} — server responded but rejected an unauthenticated request, not filed as dead")
                continue

            if result == "server_error":
                count = state.get(state_key, {}).get("consecutive_5xx", 0) + 1
                if count >= 2:
                    dead_links.append({"file": path.name, "field": field, "url": url, "reason": "server error (2 consecutive runs)"})
                    state.pop(state_key, None)
                else:
                    state[state_key] = {"consecutive_5xx": count}
                continue

            # result == "dead": unambiguous, file immediately.
            state.pop(state_key, None)
            dead_links.append({"file": path.name, "field": field, "url": url, "reason": "unreachable"})

    return dead_links, skipped


def file_issues(dead_links, repo, token):
    existing_titles = github_issues.list_open_issue_titles(repo, "dead-link", token)
    filed = 0
    for link in dead_links:
        title = f"Dead link: {link['file']} ({link['field']})"
        body = (
            f"**Entry**: `data/tools/{link['file']}`\n"
            f"**Field**: `{link['field']}`\n"
            f"**URL**: {link['url']}\n"
            f"**Reason**: {link['reason']}\n\n"
            "Found by the weekly link-check workflow. If this is a false "
            "positive (temporary outage, bot-blocking that should be "
            "allowlisted), close this issue — otherwise please update or "
            "remove the entry."
        )
        if github_issues.create_issue_if_new(repo, title, body, ["dead-link"], token, existing_titles):
            filed += 1
    return filed


def main(argv=None):
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools-dir", default=str(ROOT / "data" / "tools"))
    parser.add_argument("--state-file", default=str(STATE_FILE))
    args = parser.parse_args(argv)

    state = load_state(args.state_file)
    dead_links, skipped = check_all(args.tools_dir, state)
    save_state(args.state_file, state)

    for note in skipped:
        print(f"  - {note}")

    if dead_links:
        token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get("GITHUB_REPOSITORY")
        if token and repo:
            try:
                filed = file_issues(dead_links, repo, token)
            except github_issues.RateLimited as e:
                # A 429 from the GitHub issues API itself, not the target
                # link — the dead-link scan above already completed and its
                # state file is already saved, so this only stops issue
                # filing, cleanly, instead of surfacing as an uncaught
                # requests.HTTPError.
                print(f"rate limited, stopping (resets at {e.args[0]})")
                return 1
            print(f"found {len(dead_links)} dead link(s), filed {filed} new issue(s)")
        else:
            print(f"found {len(dead_links)} dead link(s) (GITHUB_TOKEN/GITHUB_REPOSITORY not set, not filing issues)")
    else:
        print("no dead links found")

    return 0


if __name__ == "__main__":
    sys.exit(main())
