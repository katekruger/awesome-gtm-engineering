# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not use semantic versioning for its content (adding or
removing an entry is not a breaking change) — version tags mark milestones
in the build and tooling, not the dataset.

## [1.0.0] - 2026-08-30

Going-public release. First tagged version.

### Added

- Data-file-driven build: one YAML file per entry in `data/tools/`,
  validated against `build/schema.json` and rendered into `readme.md` and
  the public `data/index.json` dataset by `build/build.py`.
- 66 curated entries across all 14 categories, each at or above the
  3-entry minimum.
- Daily metadata refresh (`build/refresh_metadata.py`), weekly link
  checking (`build/linkcheck.py`) and staleness review
  (`build/staleness.py`), all filing deduplicated GitHub issues via the
  shared `build/github_issues.py` helper.
- `build/validate.py` structural checks: category minimums, no category
  more than 50% one vendor's properties (derived from the registrable
  domain or GitHub owner of each entry, not self-disclosure), duplicate
  detection, and entry-format rules.
- CC0 1.0 license, `contributing.md`, `code-of-conduct.md`, and the full
  `sindresorhus/awesome` compliance kit.

### Fixed

- The vendor-capture rule previously counted `submitted_by_vendor`
  self-disclosure instead of actual ownership, so it never once
  evaluated true and missed a real violation (Revenue Data Modeling was
  4/4 Fivetran-owned dbt packages). Corrected to derive ownership from
  each entry's URL, and the underlying violation resolved by researching
  and adding independent alternatives.
- The daily metadata refresh filed a new "repo not found" issue on every
  run instead of deduplicating like the other automation scripts,
  producing up to 365 duplicate issues a year for one dead repository.
- The metadata refresh did not stop on GitHub's 429 secondary rate limit
  (only 403), risking a partial refresh getting committed.

## [1.0.1] - 2026-08-31

**`v1.0.0` shipped with the vendor-concentration rule unenforceable.** It was
tagged at the same commit that introduced `top_count * 2 > counts[name]`
(strictly greater than), which cannot fire on an even-sized category at
exactly 50% — and Revenue Data Modeling sat at precisely 4/8 Fivetran
entries, the one distribution the rule exists to catch. A small honest
correction beats quietly re-tagging.

### Fixed

- The 50% vendor-concentration check is now `>=`, so the exact-50% case
  actually fails, matching what `docs/curation-policy.md` and
  `contributing.md` have always said the rule does. Added MetricFlow (dbt
  Labs) as a researched, non-Fivetran fifth entry so Revenue Data Modeling
  passes at 4/9.
- `vendor_key` had three latent failure modes, none previously covered by a
  test that could catch them: a single vendor could resolve to two
  different identities depending on which URL an entry carried (fixed with
  an optional `vendor:` schema field, seeded on the seven live entries
  where this occurred); only `github.com` was treated as a code host,
  so entries on GitLab, Bitbucket, Codeberg, or sr.ht were invisible to the
  check (fixed by treating those hosts the same way); and a documentation
  host like `readthedocs.io` was treated as if it were the vendor's own
  domain, which could collapse unrelated readthedocs-hosted projects into
  one fictional vendor (fixed by giving doc hosts no vendor signal).
- The vendor-concentration check was skipped entirely for any category
  below its minimum entry count (it lived in that check's `else` branch).
  Both checks now run independently, so both problems surface in the same
  run.
- `list_open_issue_titles` and `create_issue_if_new` (`build/github_issues.py`)
  had no rate-limit handling of their own, so a 429/403 from GitHub's
  issues API — as opposed to the repo-metadata API, which was already
  handled — surfaced as an uncaught `requests.HTTPError` instead of the
  clean "rate limited, stopping" path. All three callers
  (`build/refresh_metadata.py`, `build/linkcheck.py`, `build/staleness.py`)
  now stop cleanly on it.
- `build/validate.py` now rejects two entries sharing a `source_code_url`.
  Previously two differently-named entries pointing at the same repo could
  each independently file their own "Remove: `<name>`" removal issue for
  one dead link, since `open_removal_issue`'s title is keyed on the entry
  name, not the repo.

## [Unreleased]
