# Contributing

Thanks for wanting to add to this list. Read this before opening a PR — most
rejected PRs fail on one of the points below, not on taste.

## The data file is the source of truth

`readme.md` is **generated**. Never hand-edit it — your changes will be
overwritten the next time `build/build.py` runs. Contributors edit
`data/tools/*.yml`, one file per entry. Add or update the YAML file for your
entry; a GitHub Action regenerates `readme.md` on merge.

Curation — whether an entry belongs, which category it sits in, whether the
description is accurate — is a **human decision**, made by a maintainer
reviewing your PR. Automation in this repo only refreshes metadata
(stars, last commit, archived status, latest release) and enforces the
structural rules below. It never decides what belongs on the list.

## How to add a tool

1. Copy an existing file in `data/tools/` as a starting point.
2. Fill in the fields described in [`docs/data-format.md`](docs/data-format.md).
3. Run `python build/validate.py` locally and fix anything it flags.
4. Open a PR. Fill out the PR template checklist.

## Inclusion policy

1. **Self-submissions are welcome and must be disclosed.** If you work for
   the company whose product you're adding, set `submitted_by_vendor: true`
   in the YAML. That is not disqualifying — an undisclosed self-submission is.
2. **No category may have a single vendor at 50% or more of its entries.** A
   single vendor holding half or more of one category crowds out independent
   options and reads as a content-marketing placement, not a curated list.
   `build/validate.py` enforces this at PR time, including the exact-50%
   case.
3. **Entries must be usable without a sales call.** Public docs, public
   pricing or a real free tier, or a public repository. "Contact us for a
   demo" is not enough on its own.
4. **No listing-for-backlink.** If the primary reason to add an entry is the
   link back to your site rather than the tool itself being useful to a GTM
   engineer, it doesn't belong here.
5. **Every entry must earn its place.** This is a curation of the best tools
   in each category, not an exhaustive directory. A maintainer may decline an
   entry that is redundant with better-established options, even if it
   technically qualifies.
6. **Removal is normal, not punitive.** Archived, sunset, acquired-and-folded,
   or 12 months with no development activity gets removed via the
   [remove-tool issue template](.github/ISSUE_TEMPLATE/remove-tool.yml),
   opened by a maintainer or a bot. There is a 14-day window to object before
   the entry is removed.

## Category minimums

Every category needs at least 3 entries. `build/validate.py` fails the build
if any category drops below that — a category is either populated properly
or it doesn't exist as a section.

## What we will not accept

- Fully AI-generated pull requests. Automation and scaffolding in this repo
  are fine; the entry description and the judgment that a tool belongs need
  to be yours.
- Entries for products that no longer exist, are archived, or have been
  folded into another product without a redirect.
- Duplicate entries — search `data/tools/` before adding.
