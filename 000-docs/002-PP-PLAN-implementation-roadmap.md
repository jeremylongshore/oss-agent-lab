# 002-PP-PLAN: Implementation Roadmap

**Project:** OSS Agent Lab
**Version:** 1.0
**Date:** 2026-03-16
**Author:** Jeremy Longshore
**Status:** Draft

---

## Overview

This roadmap defines the phased implementation plan for OSS Agent Lab v1. Each phase (epic) has clear deliverables, dependencies, and estimated complexity. The critical path runs E0 through E6, with the scoring engine (E5) developed in parallel after E2.

---

## Dependency Chain

```
E0 ──→ E1 ──→ E2 ──→ E3 ──→ E4 ──→ E6
                │                      ▲
                └──→ E5 ──────────────┘
```

- E3 and E5 can proceed in parallel after E2 completes.
- E4 depends on E3 (pattern established by first 3 specialists).
- E6 depends on both E4 (all specialists) and E5 (scoring engine).

---

## Phase 0 — Foundation (E0)

**Complexity:** S (Small)
**Duration:** 1 session
**Depends on:** Nothing

| # | Deliverable | Description |
|---|------------|-------------|
| 0.1 | GitHub repository | Create `oss-agent-lab` repo, MIT license, .gitignore |
| 0.2 | Local project directory | `/home/jeremy/000-projects/oss-agent-lab/` |
| 0.3 | Beads initialization | `bd init`, create initial tasks for E1-E6 |
| 0.4 | Ecosystem registration | Add to `000-ecosystem/CLAUDE.md` cross-reference |

**Exit criteria:** Repo exists, beads tracking active, ecosystem linked.

---

## Phase 1 — Scaffold (E1)

**Complexity:** S (Small)
**Duration:** 1 session
**Depends on:** E0

| # | Deliverable | Description |
|---|------------|-------------|
| 1.1 | CLAUDE.md | Project-level agent instructions with architecture summary |
| 1.2 | README.md | Full project README with architecture diagram, specialist matrix, quickstart |
| 1.3 | pyproject.toml | Python packaging with dependencies (anthropic, pydantic, httpx, click, rich, litellm) |
| 1.4 | Directory structure | `src/`, `agents/`, `scoring/`, `tests/`, `000-docs/`, `output/`, `scripts/`, `service/` |
| 1.5 | Specialist template | `agents/specialists/_template/` with agent.py, tools.py, SKILL.md, README.md |
| 1.6 | Phase 1 docs | 000-docs populated with PRD, roadmap, architecture, inventory, landscape research |
| 1.7 | Initial push | All scaffold files committed and pushed to remote |

**Exit criteria:** `pip install -e .` succeeds, directory structure matches CLAUDE.md architecture, docs complete.

---

## Phase 2 — Core Orchestration (E2)

**Complexity:** XL (Extra Large)
**Duration:** 3-5 sessions
**Depends on:** E1

| # | Deliverable | Description |
|---|------------|-------------|
| 2.1 | Contract schemas | `agents/contracts/schemas.py` — Query, Intent, SpecialistRequest, SpecialistResponse, SessionContext as Pydantic models |
| 2.2 | Registry | `agents/router/registry.py` — Auto-discovers specialists by scanning `agents/specialists/` directory, loads SKILL.md manifests, builds capability index |
| 2.3 | Conductor agent | `agents/conductor/agent.py` — NL input, intent classification, task decomposition using Claude Agent SDK |
| 2.4 | Router agent | `agents/router/agent.py` — Capability matching against registry, parallel dispatch, result aggregation |
| 2.5 | Memory layer | `agents/memory/` — cognee-based knowledge graph for cross-session context and conversation history |
| 2.6 | E2E test harness | `tests/test_e2e.py` — Full pipeline test: NL input -> conductor -> router -> mock specialist -> response |
| 2.7 | CLI entry point | `src/oss_agent_lab/cli.py` — Click-based CLI wiring conductor as the entry point |

**Exit criteria:** E2E test passes with mock specialists, conductor classifies intents correctly, router dispatches and aggregates, registry auto-discovers.

---

## Phase 3 — First 3 Specialists (E3)

**Complexity:** L (Large)
**Duration:** 2-3 sessions
**Depends on:** E2

| # | Deliverable | Description |
|---|------------|-------------|
| 3.1 | autoresearch specialist | Wraps karpathy/autoresearch — hypothesis_generation, experiment_design, result_analysis |
| 3.2 | swarm_predict specialist | Wraps 666ghj/MiroFish — multi_model_voting, swarm_consensus, prediction |
| 3.3 | deer_flow specialist | Wraps bytedance/deer-flow — research, code_generation, creation_pipeline |
| 3.4 | Specialist test suite | 80%+ coverage per specialist, integration tests with real router dispatch |
| 3.5 | Output format generation | Verify all 3 specialists produce Python API, CLI, MCP, Skill, REST |
| 3.6 | Pattern documentation | Document the specialist implementation pattern based on lessons from first 3 |

**Exit criteria:** 3 specialists pass all tests, generate all 5 formats, integrate with conductor-router pipeline end-to-end.

**Why these 3 first:** They cover three distinct patterns — research loops (autoresearch), multi-model orchestration (swarm_predict), and full-stack pipelines (deer_flow). Proving the pattern across these three ensures the template works for the remaining seven.

---

## Phase 4 — Full Team (E4)

**Complexity:** XL (Extra Large)
**Duration:** 3-5 sessions
**Depends on:** E3

| # | Deliverable | Description |
|---|------------|-------------|
| 4.1 | browser_ai specialist | Wraps lightpanda-io/browser — navigate, click, extract, screenshot |
| 4.2 | knowledge_graph specialist | Wraps GitNexus + cognee — entity_linking, relationship_inference, graph_rag |
| 4.3 | stock_analyst specialist | Wraps ai-hedge-fund + daily_stock — ohlcv_analysis, technical_analysis, news_signals |
| 4.4 | opinion_analyst specialist | Wraps 666ghj/BettaFish — sentiment_analysis, stance_detection, bias_measurement |
| 4.5 | gui_agent specialist | Wraps alibaba/page-agent — element_detection, locator_generation, nl_interaction |
| 4.6 | sandbox specialist | Wraps alibaba/OpenSandbox — isolated_execution, timeout_management, output_capture |
| 4.7 | Full integration test | All 9 specialists (excluding repo_scanner) pass E2E with conductor-router |

**Exit criteria:** All 9 specialists meet the bar (80% coverage, 5 formats, contract compliance), full integration suite green.

---

## Phase 5 — Scoring Engine (E5)

**Complexity:** L (Large)
**Duration:** 2-3 sessions
**Depends on:** E2 (can run in parallel with E3/E4)

| # | Deliverable | Description |
|---|------------|-------------|
| 5.1 | GitHub Trending scraper | `scoring/sources/github_trending.py` — Star velocity, fork rate, new repo detection |
| 5.2 | Hacker News scraper | `scoring/sources/hackernews.py` — Points, comment count, front-page duration |
| 5.3 | Papers With Code scraper | `scoring/sources/papers_with_code.py` — Paper-repo links, benchmark results |
| 5.4 | Reddit scraper | `scoring/sources/reddit.py` — r/MachineLearning upvotes, cross-posts |
| 5.5 | ArXiv scraper | `scoring/sources/arxiv.py` — CS.AI listings, citation velocity |
| 5.6 | Social signals scraper | `scoring/sources/social.py` — X mentions, engagement rate |
| 5.7 | Weighted scorer | `scoring/scorer.py` — Composite 0-100 score (Discovery 40%, Quality 35%, Durability 25%) |
| 5.8 | Temporal index | `scoring/temporal.py` — Track score changes over time, detect velocity spikes |
| 5.9 | Threshold automation | Score-based actions: 80+ auto-scaffold, 60-79 flag, 40-59 watch, <40 skip |

**Exit criteria:** All 6 scrapers return structured data, scorer produces consistent 0-100 scores, temporal index tracks history, thresholds trigger correct actions.

---

## Phase 6 — Meta-Agent + Launch (E6)

**Complexity:** L (Large)
**Duration:** 2-3 sessions
**Depends on:** E4 + E5

| # | Deliverable | Description |
|---|------------|-------------|
| 6.1 | repo_scanner specialist | META specialist (#10) — analyzes repos, generates specialist scaffolds, opens PRs |
| 6.2 | Multi-format output pipeline | Automated generation of all 5 output formats from specialist definition |
| 6.3 | CI/CD pipeline | GitHub Actions: lint (ruff), type check (mypy), test (pytest-cov), format generation validation |
| 6.4 | CHANGELOG.md | Complete changelog following Keep a Changelog format |
| 6.5 | Contributing guide | Specialist contribution workflow, PR template, quality bar documentation |
| 6.6 | Launch README | Final README polish with live examples, badges, GIFs |
| 6.7 | v0.1.0 release | Tagged release, PyPI-ready (optional), GitHub Release with notes |

**Exit criteria:** All 10 specialists operational, CI green, repo_scanner can generate a scaffold from a GitHub URL, README tells the full story.

---

## Summary

| Phase | Name | Complexity | Depends On | Key Deliverables |
|-------|------|-----------|------------|-----------------|
| E0 | Foundation | S | -- | Repo, beads, ecosystem link |
| E1 | Scaffold | S | E0 | CLAUDE.md, README, pyproject, template, docs |
| E2 | Core Orchestration | XL | E1 | Conductor, Router, Registry, Contracts, Memory |
| E3 | First 3 Specialists | L | E2 | autoresearch, swarm_predict, deer_flow |
| E4 | Full Team | XL | E3 | browser_ai through sandbox (6 more) |
| E5 | Scoring Engine | L | E2 | 6 scrapers, weighted scorer, temporal index |
| E6 | Meta-Agent + Launch | L | E4, E5 | repo_scanner, CI/CD, multi-format pipeline, release |

**Total estimated effort:** 14-20 sessions across all phases.
