# Entry data format

One YAML file per entry in `data/tools/`, named after the tool
(`clay.yml`, `apollo-io.yml`). Validated against
[`build/schema.json`](../build/schema.json) — run `python build/validate.py`
before opening a PR.

```yaml
# data/tools/clay.yml
name: Clay
website_url: https://clay.com
description: Enrichment waterfalls and list building with a spreadsheet interface.
categories: [Enrichment & Data]
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

# --- disclosure ---
submitted_by_vendor: false

# --- optional override for the vendor-concentration check; see notes below ---
# vendor: acme

# --- machine-refreshed by build/refresh_metadata.py; never hand-edit ---
stargazers_count: null
last_commit_at: null
archived: null
current_release: null
```

## Field notes

- `categories` must match a `name` in [`data/categories.yml`](../data/categories.yml)
  exactly. An entry may belong to more than one category.
- `description` must start with an uppercase character and end in a period —
  this mirrors the `sindresorhus/awesome` entry format so the generated
  README passes `awesome-lint` unmodified.
- `source_code_url` is the GitHub repo URL if the tool is open source, or
  `null` for closed-source commercial tools. Only entries with a
  `source_code_url` get the machine-refreshed metadata block filled in.
- The machine-refreshed block (`stargazers_count`, `last_commit_at`,
  `archived`, `current_release`) is written only by
  `build/refresh_metadata.py`. A PR that hand-edits these fields will be
  overwritten on the next daily refresh — don't bother setting them yourself.
- `vendor` (optional) overrides `build/validate.py`'s vendor-concentration
  check for this one entry. Set it when the automatic heuristic (the code
  host's owner login, falling back to the website's registrable domain)
  would resolve to something that isn't the entry's real owner — e.g. a
  GitHub org that predates a product rename, or a repo hosted under an
  acquirer's org rather than the product's own brand. Most entries never
  need it.
