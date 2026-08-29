# Going-public checklist

This repo is private during the build. Flip it to public once every item
below is true — see `BUILD-PLAN.md` §0 and §9 for the reasoning.

- [ ] All 14 categories in `data/categories.yml` have at least 3 entries
- [ ] `python build/build.py` regenerates `README.md` deterministically
      (running it twice produces no diff)
- [ ] `python build/validate.py` passes with zero errors
- [ ] `npx awesome-lint` passes with zero errors
- [ ] `license`, `contributing.md`, `code-of-conduct.md` all present at repo root
- [ ] Repo topics include `awesome` and `awesome-list`
- [ ] Default branch is `main`
- [ ] `lint.yml` and `build.yml` are green on the latest commit to `main`
- [ ] No category is more than 50% one vendor's properties

Once public, the 30-day `sindresorhus/awesome` age clock starts running from
this date. Submission itself stays blocked until intake reopens
(tracked in `BUILD-PLAN.md` §0 item 2) — going public does not mean
submitting immediately.
