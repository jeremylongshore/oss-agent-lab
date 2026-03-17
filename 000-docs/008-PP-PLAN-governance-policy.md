# 008-PP-PLAN: Governance Policy

**Category:** Project Plan -- Policy
**Status:** Final
**Date:** 2026-03-16
**Author:** Jeremy Longshore

---

## Purpose

This document defines the governance model for OSS Agent Lab: who maintains it, how contributions work, how versions are managed, and what quality standards specialists must meet. It is the authoritative reference for all contribution and lifecycle decisions.

---

## Maintainer

**Jeremy Longshore** ([@jeremylongshore](https://github.com/jeremylongshore)) is the sole maintainer for v1.x. All merge decisions, release decisions, and tier promotions go through Jeremy. This is intentional for v1 -- a single maintainer ensures consistent quality and architectural coherence during the foundational phase.

Additional maintainers may be added after v1.0.0 stabilizes, at the sole discretion of the current maintainer.

---

## Contribution Model

OSS Agent Lab uses an open PR model. Anyone can contribute. The primary contribution path is **new specialists** -- each new specialist is submitted as a single pull request.

### PR Requirements for New Specialists

Every specialist PR must include:

| File | Location | Purpose |
|------|----------|---------|
| `agent.py` | `agents/specialists/<name>/agent.py` | Specialist class extending BaseSpecialist |
| `tools.py` | `agents/specialists/<name>/tools.py` | Tool implementations (pure functions preferred) |
| `SKILL.md` | `agents/specialists/<name>/SKILL.md` | Metadata and documentation per 007-DR-STND |
| `README.md` | `agents/specialists/<name>/README.md` | Human-readable specialist documentation |
| Unit tests | `tests/specialists/<name>/` | Test files covering the specialist |

### PR Checklist

Before a specialist PR can be merged, it must satisfy all of the following:

- [ ] `agent.py` extends `BaseSpecialist` from `agents/contracts/`
- [ ] `tools.py` exports functions matching SKILL.md `allowed_tools`
- [ ] `SKILL.md` passes all validation rules (see 007-DR-STND)
- [ ] `README.md` documents setup, usage, and upstream repo attribution
- [ ] Unit test coverage at 80% or above for the specialist directory
- [ ] All inter-agent data uses Pydantic schemas from `agents/contracts/schemas.py`
- [ ] Source repo attribution with link to upstream repository
- [ ] Upstream repo has an MIT-compatible license (MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, Unlicense, 0BSD)
- [ ] No undocumented network calls (all external calls declared in SKILL.md `allowed_tools`)
- [ ] All 5 output formats generated (python_api, cli, mcp_server, agent_skill, rest_api)
- [ ] CI pipeline passes (linting, type checking, tests, coverage, SKILL.md validation)

### Other Contribution Types

Non-specialist contributions (bug fixes, scoring source additions, tooling improvements, documentation) follow standard open-source PR conventions: fork, branch, PR, review, merge. These do not require the specialist-specific checklist above but must pass CI.

---

## Versioning

OSS Agent Lab follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (semver).

| Version Component | When to Increment | Examples |
|-------------------|-------------------|---------|
| **PATCH** (0.1.x) | Bug fixes, documentation corrections, test improvements | Fix scoring calculation, correct SKILL.md typo |
| **MINOR** (0.x.0) | New specialists, new scoring sources, new tooling, additive contract fields | Add `stock-analyst` specialist, add Reddit scoring source |
| **MAJOR** (x.0.0) | Breaking changes to conductor/router/registry contracts, removal of output formats, schema incompatibilities | Change SpecialistRequest schema, remove MCP output format |

### Pre-1.0 Convention

While the project is below v1.0.0, MINOR versions may include breaking changes. After v1.0.0, the breaking change policy (below) applies strictly.

---

## Changelog

Every release must include a [CHANGELOG.md](../CHANGELOG.md) entry following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

Each entry uses one or more of these sections:

| Section | When to Use |
|---------|-------------|
| **Added** | New features, new specialists, new scoring sources |
| **Changed** | Modifications to existing behavior |
| **Deprecated** | Features that will be removed in a future release |
| **Removed** | Features removed in this release |
| **Fixed** | Bug fixes |
| **Security** | Vulnerability patches, dependency updates for security |

### Changelog Entry Example

```markdown
## [0.2.0] - 2026-04-01

### Added
- `autoresearch` specialist wrapping karpathy/autoresearch
- Reddit r/MachineLearning as scoring source

### Fixed
- Scoring engine correctly normalizes star velocity across time zones
```

---

## Specialist Quality Tiers

Every specialist is assigned a quality tier. Tiers control visibility, trust level, and maintenance expectations.

### Tier Definitions

| Tier | Badge | Criteria | Maintenance |
|------|-------|----------|-------------|
| **Core** | `[core]` | Ships with v1.0.0. Maintained by Jeremy. Covers the 10 foundational specialists. | Maintained by project maintainer. Guaranteed to work with every release. |
| **Verified** | `[verified]` | PR reviewed and merged. 80%+ test coverage. 30 days of active maintenance after merge. No unresolved issues. | Maintained by contributor with maintainer oversight. Expected to work with every release. |
| **Community** | `[community]` | PR merged. Self-maintained by the contributor. Meets baseline quality (CI passes, SKILL.md valid). | Maintained by contributor. Best-effort compatibility with releases. |
| **Experimental** | `[experimental]` | Work in progress. May not pass all CI checks. Not recommended for production use. | No maintenance guarantees. May be removed if abandoned. |

### Tier Promotion Path

```
experimental --> community --> verified --> core
```

- **experimental to community**: PR passes CI, SKILL.md validates, tests pass at 80%+, maintainer approves merge.
- **community to verified**: 30 days of active maintenance post-merge. Contributor responds to issues within 7 days. No open bugs older than 14 days. Maintainer approves promotion.
- **verified to core**: Maintainer decision only. Reserved for specialists that are essential to the project's value proposition.

### Tier Demotion

- A **verified** specialist with no maintenance activity for 60 days is demoted to **community**.
- A **community** specialist with no maintenance activity for 90 days is flagged for removal.
- Removal requires a deprecation notice in CHANGELOG.md one MINOR version before actual removal.

---

## Breaking Change Policy

After v1.0.0, the following contracts are **frozen**:

- **Conductor contract**: The interface between natural language input and task decomposition.
- **Router contract**: The interface between task dispatch and specialist invocation.
- **Registry contract**: The interface for specialist discovery and capability matching.
- **SpecialistRequest / SpecialistResponse schemas**: The Pydantic models in `agents/contracts/schemas.py`.

Frozen contracts may only receive **additive** changes:

- New optional fields: allowed.
- New enum values: allowed.
- Removing fields: **not allowed** (major version required).
- Changing field types: **not allowed** (major version required).
- Renaming fields: **not allowed** (major version required).

A specialist PR that requires a contract change is **rejected by CI**. Contract changes require a separate PR with a major version bump justification reviewed by the maintainer.

---

## Security Policy

### Network Call Transparency

All specialists must declare every external network call in their SKILL.md `allowed_tools` field with a `Network` side-effect annotation in the Tools table. Any network call not declared in SKILL.md is a policy violation.

### CI Security Scanning

The CI pipeline includes a scan for undocumented outbound network calls. The scanner:

1. Parses SKILL.md `allowed_tools` and the Tools table side-effects column.
2. Static-analyzes `agent.py` and `tools.py` for HTTP client usage (`httpx`, `requests`, `urllib`, `aiohttp`, socket operations).
3. Flags any network-capable code path not covered by a declared `Network` side-effect tool.

Flagged specialists fail CI and cannot merge until the undocumented call is either declared in SKILL.md or removed.

### Dependency Security

- All dependencies must be pinned to minimum versions (not exact pins, to allow security patches).
- `pip-audit` runs in CI to catch known vulnerabilities.
- Dependencies with critical CVEs block merging until updated or replaced.

### Secrets

- No API keys, tokens, or credentials in source code. Ever.
- All secrets are passed via environment variables.
- `.env` files are in `.gitignore` and must never be committed.

---

## License

OSS Agent Lab is licensed under the [MIT License](../LICENSE). Copyright (c) 2026 intentsolutions.io.

### Specialist License Requirements

All specialists must wrap upstream repos with MIT-compatible licenses. The accepted SPDX identifiers are:

- MIT
- Apache-2.0
- BSD-2-Clause
- BSD-3-Clause
- ISC
- Unlicense
- 0BSD

Specialists wrapping proprietary or GPL-licensed repos are out of scope and will not be merged. The `license` field in SKILL.md is validated against this allowlist in CI.

---

## Specialist Lifecycle

The full lifecycle of a specialist from idea to retirement:

```
1. Idea
   A trending repo crosses the scoring threshold, or a contributor
   identifies a valuable capability gap.

2. Scaffold
   Contributor copies agents/specialists/_template/ to a new directory.
   Fills in SKILL.md, implements agent.py and tools.py.

3. PR Submission
   Contributor opens a PR with all required files. CI runs automatically.

4. CI Validation
   Automated checks: SKILL.md validation, linting, type checking,
   test coverage, security scan, output format generation.

5. Code Review
   Maintainer reviews code quality, architectural fit, upstream repo
   health, and license compliance.

6. Merge as [community]
   PR is merged. Specialist enters the registry at community tier.
   Contributor is responsible for ongoing maintenance.

7. Promotion to [verified]
   After 30 days of active maintenance, contributor requests promotion.
   Maintainer reviews maintenance history and approves.

8. Deprecation (if needed)
   If a specialist becomes unmaintained or the upstream repo is archived,
   a deprecation notice is added to CHANGELOG.md.

9. Removal
   One MINOR version after deprecation notice, the specialist is removed
   from the repository.
```

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-16 | Sole maintainer model for v1 | Ensures architectural coherence during foundation phase |
| 2026-03-16 | 80% test coverage requirement | Balances quality with contributor friction |
| 2026-03-16 | MIT-compatible license only | Simplifies legal review, prevents license contamination |
| 2026-03-16 | 30-day active maintenance for verified tier | Proves commitment beyond initial contribution |
| 2026-03-16 | Frozen contracts after v1.0.0 | Protects the ecosystem from breaking changes |
