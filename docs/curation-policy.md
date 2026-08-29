# Curation policy

This is the policy referenced from [`contributing.md`](../contributing.md),
kept as its own document so it can be linked from issue templates and PR
reviews without duplicating text.

1. **Self-submissions are welcome and must be disclosed** via
   `submitted_by_vendor: true`. Not disqualifying — undisclosed is.
2. **No category may be more than 50% one vendor's properties.**
   `build/validate.py` enforces this at PR time.
3. **Entries must be usable without a sales call** — public docs, public
   pricing or a real free tier, or a public repository.
4. **No listing-for-backlink.**
5. **Every entry must earn its place.** Curation means the best, not
   everything.
6. **Removal is normal, not punitive.** Archived, sunset,
   acquired-and-folded, or 12 months with no development activity gets
   removed via a maintainer- or bot-opened issue, with a 14-day window to
   object.
7. **Every category needs a minimum of 3 entries.** The build fails below
   that — no one-entry stub sections.

This policy exists because both prior lists using this name drifted without
one: one accumulated vendor self-submissions in most of its open PRs, the
other ended up with a category where every entry was one vendor's own
properties. A written, enforced policy is cheap; drift is expensive to
unwind later.
