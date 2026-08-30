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

## [Unreleased]
