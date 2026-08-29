# 1. Record architecture decisions

Date: 2026-08-29

## Status

Accepted

## Context

This repo will accumulate structural decisions over time — the data-file
architecture, the category-minimum rule, the license choice, how the build
pipeline is triggered — that aren't visible from reading the code alone and
that future contributors (human or agent) will otherwise re-litigate.

## Decision

We will use lightweight Architecture Decision Records, stored in
`docs/decisions/`, one file per decision, numbered sequentially. Use
[`0000-template.md`](0000-template.md) as the starting point for a new one.

## Consequences

Decisions and their reasoning are discoverable in the repo itself rather than
living only in PR discussions or a maintainer's memory.
