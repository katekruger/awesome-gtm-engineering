# Going-public checklist

This repo is private during the build. Flip it to public once every item
below is true — see `BUILD-PLAN.md` §0 and §9 for the reasoning.

- [x] All 14 categories in `data/categories.yml` have at least 3 entries
- [x] `python build/build.py` regenerates `README.md` deterministically
      (running it twice produces no diff)
- [x] `python build/validate.py` passes with zero errors
- [x] `npx awesome-lint` passes with zero errors
- [x] `license`, `contributing.md`, `code-of-conduct.md` all present at repo root
- [x] Repo topics include `awesome` and `awesome-list`
- [x] Default branch is `main`
- [x] `lint.yml` and `build.yml` are green on the latest commit to `main`
- [x] No category is more than 50% one vendor's properties

## Clock start

**Repo flipped to public on 2026-08-29.** The `sindresorhus/awesome` 30-day
age rule measures from first real commit or open-sourcing, whichever is
later — private time before this date does not count. First real commit
was also 2026-08-29 (same day as going public), so the clock starts today.

**Earliest possible submission date: 2026-09-28** — assuming
`sindresorhus/awesome` intake has reopened by then, which it may not have
(see `BUILD-PLAN.md` §0 item 2 and the submission requirements below).
Going public does not mean submitting immediately; submission is gated on
both the 30-day clock AND intake reopening.

## Submission requirements, for when intake reopens

Captured here so a future session doesn't have to re-derive them from
`sindresorhus/awesome`'s `pull_request_template.md` and `create-list.md`:

- Review **at least 4** other open PRs on `sindresorhus/awesome`,
  substantively — a comment that only says "looks good" does not count.
- PR title exactly: `Add GTM Engineering` — no "Awesome" in the title.
- The index entry (the line added to `sindresorhus/awesome`'s own README)
  describes the **subject**, not the list. Uppercase first character, ends
  in a period. Same style as every entry in this list's own README.
- The URL in that index entry ends in `#readme` and is title-cased.
- The entry is added at the **bottom** of its category in
  `sindresorhus/awesome`'s README — not alphabetically, not at the top.
- Comment the single word `unicorn` on the PR. This is the buried
  proof-you-actually-read-the-contributing-guidelines check reviewers use
  to filter low-effort submissions — do not skip it, and do not explain it
  in the PR itself.
