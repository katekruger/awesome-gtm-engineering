# awesome-gtm-engineering — Build Plan

**Become the canonical curated list for GTM engineering: data-file-driven, automatically maintained, and the only one publishing the facets that matter (has a real API, has an MCP server, open-source vs commercial).**

Owner: Kate Kruger (`github.com/katekruger`)
Status: not started
Plan version: 1.0 — 28 Aug 2026
Research current as of: 28 Aug 2026

---

## 0. Handover context — read this first

1. **Two lists already use this name, and neither is actively maintained.** `marketinguys/awesome-gtm-engineering` has 120 stars but 2 total commits and 0 of 11 PRs ever closed; it still lists a product Google sunset in 2023. `eliasstravik/awesome-gtm-engineering` has current content and an active maintainer but only 10 stars and 33 entries. §1 explains why this project is a new repository rather than a contribution to either, and how to be a good neighbour about it.

2. **Submissions to the main `sindresorhus/awesome` index are currently CLOSED.** The repo description says so verbatim: *"Pull requests are temporarily disabled until I have a chance to catch up with the existing ones."* ~70–90 open PRs, newest visible from 23 June 2026. **You cannot get listed today.** Build for compliance, park visibility on issue [#2242](https://github.com/sindresorhus/awesome/issues/2242) (the designated incubation thread), and treat the actual listing as an unschedulable event.

3. **The 30-day age rule is a human review gate, not a lint gate.** `awesome-lint`'s `git-repo-age` rule is **commented out in source** ("Disabled for now as it means we cannot sparsely check out the repo"). Passing lint says nothing about whether you've waited. Start the clock early.

4. **The license rule catches most lists out.** CC0 strongly recommended, any Creative Commons acceptable, and **MIT / BSD / Apache / GPL / WTFPL and Unlicense are explicitly NOT acceptable.** Get this right on day one — it is annoying to change later.

5. **The single biggest quality separator is generating the README from a data file.** `awesome-selfhosted-data` and `abordage/awesome-mcp` both do it; every list that decays does not. One YAML file per entry means clean PR diffs, no merge conflicts, and machine-refreshed metadata.

6. **The differentiating facets for this specific list are "has a real API" and "has an MCP server."** Nobody is publishing those, and in 2026 they are the two things a GTM engineer actually filters on.

---

## 1. Why a new list rather than contributing to an existing one

Two lists already use this name. Neither is well maintained, and the question is whether to contribute to one or start fresh. Here is what's actually there, so the choice is made on evidence.

### What exists

| | `marketinguys` | `eliasstravik` |
|---|---|---|
| Stars / forks / watchers | 120 / 27 / 4 | 10 / 1 / 0 |
| Total commits | 2 | 7 |
| Entries | 40 across 11 sections | 33 across 11 sections |
| License file | MIT | CC0 1.0 ✅ |
| License badge | CC BY-SA 4.0 — contradicts its own LICENSE file | n/a |
| Awesome badge | Absent | Present ✅ |
| `CONTRIBUTING.md` | Absent | Inline in README only |
| `.github/` | Absent | Absent |
| `awesome` / `awesome-list` topics | Absent | — |
| Open PRs | 11 open, 0 ever closed | 1 open, 3 closed |
| Content currency | Still lists Google Optimize, which Google sunset in 2023; Clearbit standalone, though it was absorbed into HubSpot | Clay, Cargo, Octave, Exa, Firecrawl, Stagehand, Attio, Common Room — current |
| Structural gaps | All of the above | "Learning" is 4 entries, all 4 from one vendor; Signals / Routing / Analytics are one-entry stubs |

Both are volunteer efforts that ran out of maintainer attention, which is the normal fate of a hand-edited list. That is the problem this project is designed around, not a criticism of either author.

### Decision: build a new repository

Three reasons, none of them about the incumbents:

1. **Contributing doesn't fix the structural problem.** Both lists are hand-edited READMEs with no data layer, no metadata refresh, and no staleness policy. Adding entries to either one produces a list that decays again in six months. The value of this project is the automation, and that can't be retrofitted through a PR.
2. **The content is not the hard part.** 40 entries is a weekend. What neither list has — machine-verified freshness and the `has_api` / `has_mcp_server` facets — is the whole point, and it needs the data-file architecture from the ground up.
3. **Two of the categories that matter most in 2026 are absent from both.** Neither has an "Agents & MCP Servers" section or a "Revenue Data Modeling" section. That is a genuine editorial gap, and it's the honest argument for a new list.

**Then be a good neighbour about it.** Open a courteous issue on `eliasstravik/awesome-gtm-engineering` offering to consolidate — he has good taste and actually processes submissions (3 PRs closed, versus 0 of 11 on the other). If he'd rather keep his own, that's fine; link to each other and move on. Don't approach `marketinguys` — 2 total commits and no PR responses since February means nobody is home, and an unanswered message is not worth the time.

**The name collision is real.** Three repos will share the name. Mitigate by shipping a website on a real domain and letting the site become the canonical reference. `abordage/awesome-mcp` and `punkpeye/awesome-mcp-servers` coexist fine on exactly that basis.

---

## 2. Positioning

**One line:** the GTM engineering list that tells you which tools have an API, which have an MCP server, and which are still maintained — because a bot checks every day.

**Three defensible claims:**

1. **Machine-verified freshness.** Stars, last commit, archived flag, latest release, refreshed daily. A staleness policy the bot enforces by opening its own issues.
2. **The facets nobody publishes.** `has_api`, `has_mcp_server`, `open_source`, `self_hostable`, `pricing_model`. In 2026 those are the filters that matter, and no GTM list has any of them.
3. **A written inclusion policy.** Most lists have none, which is how a category quietly ends up dominated by one vendor's properties. Write the policy, enforce it in review, and publish it in `contributing.md` so contributors know the bar before they submit.

---

## 3. The `sindresorhus/awesome` checklist — every requirement

Extracted from `pull_request_template.md`, `awesome.md` and `create-list.md`. Build to all of it from day one; retrofitting is worse.

### On the list itself

- [ ] Around for **≥30 days** from first real commit
- [ ] Not AI-generated (fully AI-generated PRs are rejected)
- [ ] Passes `awesome-lint`
- [ ] Default branch named **`main`**, not `master`
- [ ] Repo name lowercase slug: `awesome-gtm-engineering`
- [ ] H1 in title case: `# Awesome GTM Engineering`
- [ ] Succinct **subject** description at top — describe the field, not the list. *"Building revenue systems with code, data and agents."* not *"Resources and tools for GTM engineers."*
- [ ] GitHub topics **`awesome`** and **`awesome-list`** present
- [ ] Awesome badge right of the H1, linking `https://awesome.re`
- [ ] ToC section named exactly `Contents`, first section, one nesting level max
- [ ] ToC **must not** include `Contributing` or `Footnotes`
- [ ] License: **CC0** in a root `license`/`LICENSE` file
- [ ] **No license name, text, or `License` section in the README**
- [ ] **`contributing.md`** exists as a file
- [ ] Entry format `- [Name](url) - Description.` — hyphen separator, uppercase start, period end
- [ ] No hard-wrapping
- [ ] **No CI badge** in the README (run CI, don't badge it)
- [ ] No "Inspired by awesome-foo" link
- [ ] Footnotes grouped in a `Footnotes` section at the bottom

### On the eventual submission PR

- [ ] Review ≥4 other open PRs, substantively
- [ ] Title exactly `Add Awesome GTM Engineering` → actually `Add GTM Engineering` (no "Awesome" in the title)
- [ ] Index entry describes the subject, first char uppercase, ends in a period
- [ ] URL ends in `#readme`, title-cased
- [ ] Added at the **bottom** of its category
- [ ] Comment `unicorn` on the PR (the buried proof-you-read-the-guidelines check)

**There is no minimum item count.** The bar is qualitative: *"Only has awesome items. Awesome lists are curations of the best, not everything."*

### What `awesome-lint` v2.3.0 actually checks

`npx awesome-lint <repo-url>` — Node ≥20, Git required. 43 general remark-lint rules plus 13 awesome-specific:

`heading`, `badge`, `contributing`, `github`, `license`, `list-item`, `balanced-punctuation`, `no-ci-badge`, `no-repeat-item-in-description`, `toc`, `double-link` — all **error**. `spell-check` — **warn only**. `git-repo-age` — **disabled in source.**

Notable general rules: ATX headings, backtick fenced code, `-` list markers, one-space list indent, `---` thematic breaks, no heading punctuation, single top-level heading, no shell `$` prefixes, GFM tables aligned/padded/piped.

Suppress inline with `<!--lint disable rule-name-->` / `enable` / `ignore`.

**The generated-README tension:** the checklist demands a *"Non-generated Markdown file in a GitHub repo."* Both exemplar lists generate theirs and the ecosystem tolerates it — the rule's intent is "not an auto-scraped dump." **Mitigation: keep the curation decision human** (a PR against the YAML, reviewed by a person) and let automation refresh only metadata and enforce staleness. Document this explicitly in `contributing.md` so a reviewer can see the distinction.

---

## 4. Architecture — data file, generated README

### The model, from `awesome-selfhosted-data`

One YAML file per entry, `hecat`-style build, four GitHub Actions: build, daily metadata update, dead-link check, unmaintained-project detection. Their curation policy is codified and **enforced by robots that file their own issues**:

> *"Software with no development activity for 6-12 months may be removed."*
> *"Non-working software may be removed."*
> *"A tag needs a minimum of 3 entries to exist."*

That last rule alone would have prevented eliasstravik's one-entry Signals / Routing / Analytics stubs.

### Entry schema

```yaml
# data/tools/clay.yml
name: Clay
website_url: https://clay.com
description: Enrichment waterfalls and list building with a spreadsheet interface.
categories: [Enrichment]
pricing_model: commercial        # open_source | commercial | freemium | open_core
source_code_url: null
license: null

# --- the differentiating facets ---
has_api: true
api_docs_url: https://www.clay.com/docs/api
has_mcp_server: true
mcp_server_url: https://www.clay.com/mcp
mcp_server_kind: official        # official | community | none
has_cli: false
self_hostable: false

# --- machine-refreshed daily; never hand-edit ---
stargazers_count: null
last_commit_at: null
archived: null
current_release: null
```

For entries with a `source_code_url`, the bot fills the bottom block daily. For commercial tools it stays null and the entry is judged on the facets above.

### Build pipeline

```
data/tools/*.yml  ──▶  build.py  ──▶  README.md
data/categories.yml                └─▶  site/  (v0.3)
                                   └─▶  data/index.json  (public, for anyone to consume)
```

Publishing `index.json` is a small move with outsized effect: it makes the list a *dataset*, not a document, and other people will build on it.

### Workflows

| Workflow | Schedule | Does |
|---|---|---|
| `lint.yml` | on PR | `awesome-lint` + YAML schema validation + category-minimum check |
| `build.yml` | on push to main | regenerate README, commit if changed |
| `metadata.yml` | daily | refresh stars, last commit, archived, latest release |
| `linkcheck.yml` | weekly | dead-link detection → **opens an issue automatically** |
| `staleness.yml` | weekly | flags entries with no commits in 12 months → opens an issue |

**No CI badge in the README.** Run all of it; badge none of it.

---

## 5. Category structure

Built from the actual 2026 landscape rather than inherited from the martech-era lists. **Minimum 3 entries per category, enforced at build.**

```
Contents
├── Enrichment & Data
├── Signals & Intent
├── Outbound & Sequencing
├── Deliverability
├── CRM & Data Quality
├── Routing & Territory
├── Attribution & Analytics
├── Revenue Data Modeling        ← dbt packages, warehouse-native
├── Agents & MCP Servers         ← the section neither existing list has
├── Workflow Automation
├── Research & Scraping
├── Compensation & Planning
├── Learning                     ← the inclusion policy applies hardest here
└── Communities
```

Two of these — **Agents & MCP Servers** and **Revenue Data Modeling** — are entirely absent from both existing lists, and they are where 2026's actual GTM engineering happens. That gap is the editorial argument for a new list.

### Per-entry legend

Borrowed from `punkpeye/awesome-mcp-servers`, which does this well without a data file:

```
🔓 open source   💰 commercial   🧩 freemium
🔌 has API       🤖 has MCP server (🎖️ official)   ⌨️ has CLI
🏠 self-hostable
```

Cheap, readable, filterable by eye, and it does the job of structured fields in the rendered view while the YAML carries the real data.

---

## 6. Inclusion policy

Write this into `contributing.md` and enforce it. Both existing lists drifted in different ways without one.

1. **Self-submissions are welcome and must be disclosed.** Add `submitted_by_vendor: true` to the YAML. Not disqualifying — undisclosed is.
2. **No category may be more than 50% one vendor's properties.** This is the rule that would have caught eliasstravik's 4/4 Clay "Learning" section.
3. **Entries must be usable without a sales call.** Public docs, public pricing or a real free tier, or a public repo.
4. **Every entry must earn its place.** Curation means the best, not everything.
5. **Removal is normal, not punitive.** Archived, sunset, acquired-and-folded, or 12 months dark → removed by bot-opened issue, with a 14-day window to object.

Publishing this policy is itself a differentiator. Neither existing list has one, and it is why both drifted.

---

## 7. Feature inventory, scoped

| # | Feature | Effort | Verdict |
|---|---|---|---|
| 1 | YAML entry schema + 60 seed entries | 3d | **v0.1** |
| 2 | `build.py` → README generation | 2d | **v0.1** |
| 3 | Full awesome-compliance kit (CC0, badge, topics, `contributing.md`, ToC, `main`) | 0.5d | **v0.1** |
| 4 | `awesome-lint` + schema validation on PR | 0.5d | **v0.1** |
| 5 | Category-minimum (3) enforced at build | 0.5d | **v0.1** |
| 6 | Inclusion policy written and enforced | 0.5d | **v0.1** |
| 7 | Per-entry legend | 0.5d | **v0.1** |
| 8 | Daily metadata refresh workflow | 1.5d | **v0.1** |
| 9 | Dead-link check → auto-issue | 1d | v0.2 |
| 10 | Staleness detection → auto-issue | 1d | v0.2 |
| 11 | Public `index.json` | 0.5d | v0.2 |
| 12 | Consolidation offer to `eliasstravik` | 0.5d | v0.2 |
| 13 | Companion website off the same data | 4d | v0.3 |
| 14 | Agent-PR lane (`🤖🤖🤖` convention, borrowed from awesome-mcp-servers) | 0.5d | v0.3 |
| 15 | Submission to `sindresorhus/awesome` | 0.5d | **Blocked** — intake closed |
| 16 | Translated READMEs | 2d | Deferred |

**Total to v0.1: ~9 days.** This is the cheapest project of the five and the one that makes every other one discoverable.

---

## 8. Repo structure

```
awesome-gtm-engineering/
├── README.md                   # GENERATED — do not hand-edit
├── license                     # CC0-1.0
├── contributing.md             # includes the inclusion policy
├── code-of-conduct.md
├── .github/
│   ├── workflows/{lint,build,metadata,linkcheck,staleness}.yml
│   ├── PULL_REQUEST_TEMPLATE.md    # "did you add a YAML file, not edit the README?"
│   └── ISSUE_TEMPLATE/{add-tool,remove-tool}.yml
├── data/
│   ├── categories.yml
│   └── tools/*.yml
├── build/
│   ├── build.py
│   ├── refresh_metadata.py
│   ├── schema.json
│   └── templates/readme.md.j2
└── docs/
    ├── curation-policy.md
    └── data-format.md
```

---

## 9. Milestones

| # | Deliverable | Done when |
|---|---|---|
| M0 | **First commit** — starts the 30-day clock | Repo public with compliance kit in place |
| M1 | Schema + 60 entries | All 14 categories have ≥3 entries |
| M2 | Build pipeline | README regenerates deterministically; diff is clean |
| M3 | `awesome-lint` green | `npx awesome-lint` passes with zero errors |
| M4 | Metadata refresh live | Stars and last-commit dates update daily without a human |
| M5 | Auto-issue workflows | A deliberately broken link opens an issue |
| M6 | Consolidation offer sent | PR or issue open on `eliasstravik/awesome-gtm-engineering` |
| M7 | Note on `sindresorhus/awesome#2242` | Visible in the incubation thread |
| M8 | Website | v0.3 |
| M9 | Submission PR | **When intake reopens — unschedulable** |

---

## 10. Distribution

1. **Cross-link from every one of your own repos.** Six public repos each linking the list is a real seed.
2. **The consolidation offer to `eliasstravik`** — good faith, and he has the better taste of the two incumbents.
3. **`punkpeye/awesome-mcp-servers`** — add the list under an appropriate category. 90.9k stars, and its agent-PR lane (`🤖🤖🤖` in the PR title) is a fast-track.
4. **Announce with the finding, not the list.** *"I checked every tool on the two existing GTM engineering lists — one still recommends a product Google killed in 2023, and 9 of 11 pending submissions are vendors adding themselves."* That is the post. The list is the artifact.
5. **The `index.json` dataset** — tell people they can build on it. Datasets get cited; documents get bookmarked.
6. **r/RevOps and the GTM-engineering newsletters** (GTM Engineer Pulse, The Signal, The GTM Engineer) — all three actively link resources.

---

## 11. Open questions

1. **Verify last-commit dates for both existing lists.** `/commits`, `/tree` and `.atom` are all robots-disallowed from an automated fetch; the repo file-listing date column did not survive markdown conversion. Best available proxy: `marketinguys` has 2 total commits and 0 of 11 PRs closed since Feb 2026. Confirm in a browser before publishing any claim about staleness.
2. **Open-issue counts for both** — not rendered in the fetched pages.
3. **`sindresorhus/awesome` open-PR count** — the repo header says 90, the pulls tab said 70. Sources disagree; don't cite a number.
4. **Decide on the name collision.** Three repos, one name. Recommendation: keep the name (it is the searched term), ship a website, and let the site be canonical.
5. **Confirm `public-apis/public-apis` validator implementation** if you want to borrow it — directories confirmed, contents not enumerable from the rendered page.

---

## 12. Sources

- [marketinguys/awesome-gtm-engineering](https://github.com/marketinguys/awesome-gtm-engineering) · [its PRs](https://github.com/marketinguys/awesome-gtm-engineering/pulls) · [eliasstravik/awesome-gtm-engineering](https://github.com/eliasstravik/awesome-gtm-engineering) · [its PRs](https://github.com/eliasstravik/awesome-gtm-engineering/pulls)
- [sindresorhus/awesome](https://github.com/sindresorhus/awesome) · [pull_request_template.md](https://raw.githubusercontent.com/sindresorhus/awesome/main/pull_request_template.md) · [awesome.md](https://raw.githubusercontent.com/sindresorhus/awesome/main/awesome.md) · [create-list.md](https://raw.githubusercontent.com/sindresorhus/awesome/main/create-list.md) · [incubation issue #2242](https://github.com/sindresorhus/awesome/issues/2242)
- [awesome-lint](https://github.com/sindresorhus/awesome-lint) · [config.js](https://raw.githubusercontent.com/sindresorhus/awesome-lint/main/config.js) · [rules/index.js](https://raw.githubusercontent.com/sindresorhus/awesome-lint/main/rules/index.js)
- [awesome-selfhosted-data](https://github.com/awesome-selfhosted/awesome-selfhosted-data) · [its CONTRIBUTING.md](https://raw.githubusercontent.com/awesome-selfhosted/awesome-selfhosted-data/master/CONTRIBUTING.md) · [abordage/awesome-mcp](https://github.com/abordage/awesome-mcp) · [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) · [e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) · [public-apis/public-apis](https://github.com/public-apis/public-apis)
