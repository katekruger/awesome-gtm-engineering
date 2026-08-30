# Security policy

This repository is a curated list — a set of YAML data files rendered
into a static `readme.md` and a static `data/index.json` dataset by the
scripts in `build/`. There is no runtime service, no user data, and no
authentication to compromise. The realistic security surface is narrow:

- The build and automation scripts (`build/*.py`) and the GitHub Actions
  workflows that run them (`.github/workflows/*.yml`).
- Supply-chain integrity of the pinned dependencies in
  `build/requirements.txt` / `build/requirements-dev.txt` and the pinned
  action SHAs in the workflow files.
- The published `data/index.json` dataset, which downstream consumers
  fetch and parse.

## Reporting a vulnerability

If you find a security issue — a workflow that could be tricked into
exfiltrating the `METADATA_REFRESH_TOKEN` secret, a command-injection
path in the build scripts, a malicious dependency, or anything similar —
please report it privately rather than opening a public issue:

1. Use [GitHub's private vulnerability reporting](https://github.com/katekruger/awesome-gtm-engineering/security/advisories/new)
   for this repository, or
2. If that is unavailable, open a regular issue asking a maintainer to
   set up a private channel, without describing the vulnerability
   publicly.

Please include steps to reproduce and the potential impact. We'll
acknowledge reports within a few days and aim to have a fix or mitigation
merged within 30 days for a confirmed issue, sooner for anything actively
exploitable.

## Supported versions

Only the latest state of the `main` branch is supported. There are no
long-lived release branches to backport fixes to.

## Out of scope

- Vulnerabilities in a third-party tool that happens to be *listed* on
  this list. Report those to the tool's own maintainers — see
  [`contributing.md`](contributing.md) if you also think the entry
  should be reconsidered or removed as a result.
- Findings that require compromising a maintainer's GitHub account or
  local machine rather than the repository's own code or workflows.
