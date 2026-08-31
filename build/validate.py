#!/usr/bin/env python3
"""Validate data/tools/*.yml against schema.json and enforce structural rules.

Run in CI on every pull request. Exits non-zero on any failure.

Checks, beyond JSON Schema:
  - category minimum of 3 entries, and no category may have a single vendor
    at 50% or more of its entries (a category that is precisely half one
    vendor is the monoculture this rule exists to catch, not a pass)
  - duplicate entries by website_url and by name (awesome-lint's
    double-link rule only catches URL collisions in the rendered README;
    two entries with different URLs but the same name still need to be
    caught here)
  - description starts uppercase, ends in a period, and uses a plain
    hyphen rather than an en dash or em dash anywhere in the entry text
"""
import argparse
import json
import pathlib
import sys
from urllib.parse import urlparse

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_FILE = pathlib.Path(__file__).resolve().parent / "schema.json"

DASH_CHARS = {"–": "en dash (–)", "—": "em dash (—)"}

# Code-hosting roots where the owner appears as the first path segment
# (github.com/owner/repo, gitlab.com/owner/repo, ...). Treated identically:
# resolving only github.com meant a GitLab/Bitbucket/Codeberg/sr.ht-hosted
# monoculture was invisible to this rule.
CODE_HOSTS = {
    "github.com", "www.github.com",
    "gitlab.com", "www.gitlab.com",
    "bitbucket.org", "www.bitbucket.org",
    "codeberg.org", "www.codeberg.org",
    "sr.ht", "git.sr.ht",
}

# Hosts that indicate "this is documentation," not "this is the vendor" —
# a project's docs living on readthedocs is not a vendor-identity signal at
# all, and treating it as one collapses unrelated readthedocs-hosted
# projects into a single fictional vendor.
DOC_HOST_SUFFIXES = ("readthedocs.io", "readthedocs.org")

# A small, checked-in list of second-level public-suffix patterns, so that
# e.g. 'acme.co.uk' resolves to the full registrable domain rather than the
# meaningless label 'co'. Deliberately not a full public-suffix-list
# dependency (this repo has none, and determinism argues against fetching
# one at runtime) — just enough of the common ccTLD compounds to stop the
# obviously wrong cases.
MULTI_PART_SUFFIXES = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "net.uk",
    "com.au", "net.au", "org.au",
    "co.nz", "co.jp", "co.kr", "co.in", "co.il", "co.za",
    "com.br", "com.mx", "com.sg",
}


def _is_doc_host(host):
    return any(host == suffix or host.endswith("." + suffix) for suffix in DOC_HOST_SUFFIXES)


def _path_owner(url):
    """First non-empty path segment, e.g. 'acme' from '/acme/repo'. sr.ht
    usernames are conventionally written '~acme' — strip the tilde so an
    sr.ht entry can still match the same vendor's identity elsewhere."""
    owner = next((p for p in urlparse(url).path.split("/") if p), None)
    if owner and owner.startswith("~"):
        owner = owner[1:]
    return owner


def _domain_key(host):
    """Best-effort registrable-domain extraction from a hostname (e.g.
    'acme' from 'www.acme.com'). Not a real eTLD+1 parser — this repo has
    no public suffix list dependency — but it is enough to match a
    vendor's website against their code-host owner login, which is all
    this rule needs.

    A hostname ending in one of MULTI_PART_SUFFIXES (e.g. 'acme.co.uk')
    returns the full three-label string instead of just 'acme': collapsing
    to the bare label would make 'acme.co.uk' and 'acme.com.au' — or any
    other pair of otherwise-unrelated companies that happen to share a
    generic name under different ccTLDs — read as the same vendor, which is
    a worse failure than not matching them to a same-vendor github owner at
    all."""
    labels = [label for label in host.split(".") if label]
    if labels and labels[0] == "www":
        labels = labels[1:]
    if not labels:
        return None
    if len(labels) == 1:
        return labels[0]
    if len(labels) >= 3 and ".".join(labels[-2:]) in MULTI_PART_SUFFIXES:
        return ".".join(labels[-3:])
    return labels[-2]


def vendor_key(tool, sentinel):
    """Best-effort owner of an entry's properties.

    Not the submitter. The policy in docs/curation-policy.md is about who
    OWNS the tools in a category, which self-reporting cannot establish:
    a curator adding four of one vendor's packages produces exactly the
    monoculture the policy forbids, with submitted_by_vendor false on all
    four.

    An explicit `vendor:` field always wins when present — a curator-set
    escape hatch for the cases the URL heuristic below gets wrong (e.g. a
    GitHub org name that doesn't match the marketing domain: 'integromat'
    vs. 'make.com'). An ever-cleverer heuristic doesn't scale past a
    handful of such cases; a field a curator sets once does.

    Otherwise: derived from the registrable domain of source_code_url,
    falling back to website_url. A recognized code-hosting URL
    (CODE_HOSTS, or a *.github.io URL) yields the owner/org login instead
    of the host itself, since e.g. github.com is the registrable domain for
    every GitHub-hosted entry and would otherwise collapse the whole list
    into one vendor. A documentation host (DOC_HOST_SUFFIXES) contributes
    no signal at all and falls through to the next URL, rather than being
    treated as if it were the vendor's own domain. An entry with no
    resolvable signal gets a sentinel unique to it, so it never accidentally
    clusters with another such entry.
    """
    explicit = tool.get("vendor")
    if explicit:
        return explicit.strip().casefold()

    for url in (tool.get("source_code_url"), tool.get("website_url")):
        if not url:
            continue
        try:
            host = urlparse(url).netloc.lower()
        except ValueError:
            host = ""
        if not host:
            continue
        if _is_doc_host(host):
            continue
        if host in CODE_HOSTS:
            owner = _path_owner(url)
            if owner:
                return owner.casefold()
            continue
        if host.endswith(".github.io"):
            owner = host[: -len(".github.io")]
            if owner:
                return owner.casefold()
            continue
        domain = _domain_key(host)
        if domain:
            return domain
    return f"__no-vendor-url__:{sentinel}"


def load_schema(schema_file):
    with open(schema_file) as f:
        return json.load(f)


def load_categories(categories_file):
    with open(categories_file) as f:
        return yaml.safe_load(f)


def load_tools(tools_dir):
    tools = []
    for path in sorted(pathlib.Path(tools_dir).glob("*.yml")):
        with open(path) as f:
            tools.append((path, yaml.safe_load(f)))
    return tools


def check_dashes(tool, path, errors):
    for char, label in DASH_CHARS.items():
        if char in tool.get("name", "") or char in tool.get("description", ""):
            errors.append(f"{path.name}: contains a {label} — use a plain hyphen")


def check_description_format(tool, path, errors):
    description = tool.get("description", "")
    if description and not description[0].isupper():
        errors.append(f"{path.name}: description must start with an uppercase character")
    if description and not description.endswith("."):
        errors.append(f"{path.name}: description must end with a period")


def validate(categories_file, tools_dir, schema_file=SCHEMA_FILE):
    errors = []
    schema = load_schema(schema_file)
    categories = load_categories(categories_file)
    category_names = {c["name"] for c in categories}

    counts = {c["name"]: 0 for c in categories}
    vendor_counts = {c["name"]: {} for c in categories}

    seen_urls = {}
    seen_names = {}
    seen_source_urls = {}

    tool_files = load_tools(tools_dir)
    for path, tool in tool_files:
        try:
            jsonschema.validate(tool, schema)
        except jsonschema.ValidationError as e:
            errors.append(f"{path.name}: {e.message}")
            continue

        check_dashes(tool, path, errors)
        check_description_format(tool, path, errors)

        url = tool["website_url"].rstrip("/").lower()
        if url in seen_urls:
            errors.append(
                f"{path.name}: duplicate website_url, already used by {seen_urls[url]}"
            )
        else:
            seen_urls[url] = path.name

        name_key = tool["name"].strip().casefold()
        if name_key in seen_names:
            errors.append(
                f"{path.name}: duplicate name, already used by {seen_names[name_key]}"
            )
        else:
            seen_names[name_key] = path.name

        # Two entries pointing at the same repo isn't just a data-quality
        # smell: build/refresh_metadata.py's removal-issue title is keyed on
        # the entry's name, not the repo, so two differently-named entries
        # sharing a source_code_url would each independently file their own
        # "Remove: <name>" issue the day that repo 404s — two issues for one
        # dead link. Catching the duplicate here removes the cause instead
        # of teaching the issue-filer to dedup titles across entries.
        source_url = (tool.get("source_code_url") or "").rstrip("/").lower()
        if source_url:
            if source_url in seen_source_urls:
                errors.append(
                    f"{path.name}: duplicate source_code_url, already used by {seen_source_urls[source_url]}"
                )
            else:
                seen_source_urls[source_url] = path.name

        key = vendor_key(tool, sentinel=path.name)
        for cat_name in tool["categories"]:
            if cat_name not in category_names:
                errors.append(f"{path.name}: unknown category {cat_name!r}")
                continue
            counts[cat_name] += 1
            vendor_counts[cat_name][key] = vendor_counts[cat_name].get(key, 0) + 1

    for cat in categories:
        name, minimum = cat["name"], cat["min_entries"]
        # Independent checks, not if/elif: a category below its minimum
        # used to skip the vendor-concentration check entirely (it lived in
        # this branch's `else`), so a contributor who fixed the count would
        # only then discover a second, previously-invisible error. Running
        # both means every problem surfaces in one pass.
        if counts[name] < minimum:
            errors.append(
                f"category {name!r} has {counts[name]} entries, "
                f"needs at least {minimum}"
            )
        if counts[name] > 0:
            top_vendor, top_count = max(
                vendor_counts[name].items(), key=lambda kv: kv[1], default=(None, 0)
            )
            # >=, not >: a category that is EXACTLY half one vendor is the
            # monoculture docs/curation-policy.md #2 exists to catch, not a
            # pass. With an even category size, `>` can never fire on the
            # one distribution the rule was written for.
            if top_count * 2 >= counts[name]:
                errors.append(
                    f"category {name!r} has a vendor at 50% or more of its "
                    f"entries ({top_vendor}: {top_count}/{counts[name]})"
                )

    return errors, len(tool_files), len(categories)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--categories-file", default=str(ROOT / "data" / "categories.yml"))
    parser.add_argument("--tools-dir", default=str(ROOT / "data" / "tools"))
    args = parser.parse_args(argv)

    errors, tool_count, category_count = validate(args.categories_file, args.tools_dir)

    if errors:
        print(f"{len(errors)} validation error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"{tool_count} entries valid across {category_count} categories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
