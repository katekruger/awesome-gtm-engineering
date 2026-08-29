# Agent instructions for this repo

- `readme.md` is **generated**. Never hand-edit it — edit `data/tools/*.yml`
  and `data/categories.yml` instead, then run `python build/build.py`.
- Curation is a **human decision**. Automation refreshes metadata
  (`build/refresh_metadata.py`) and enforces structural rules
  (`build/validate.py`); it never decides what belongs on the list.
- Every category in `data/categories.yml` needs a minimum of 3 entries.
  `build/validate.py` fails the build below that — no one-entry stub
  sections.
- Never add a CI badge to the README. Run CI; don't badge it.
- No license name, license text, or "License" section anywhere in
  `readme.md` — the license lives only in the `license` file.
- Entry format in the generated README is exactly
  `- [Name](url) - Description.` — hyphen separator, uppercase first
  character, ends in a period.
- See [`contributing.md`](contributing.md) for the full inclusion policy and
  [`docs/data-format.md`](docs/data-format.md) for the entry schema.
