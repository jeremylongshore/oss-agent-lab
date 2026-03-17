# 001-PP-PROD: Product Requirements Document

**Project:** OSS Agent Lab
**Version:** 1.0
**Date:** 2026-03-16
**Author:** Jeremy Longshore
**Status:** Draft

---

## 1. Problem Statement

500+ AI repositories trend on GitHub every week. There are now 4.3 million AI-tagged repos on GitHub, growing at 178% year-over-year. Each repo ships its own API, its own setup ritual, and its own multi-day learning curve. None of them interoperate -- a research agent cannot call a browser agent, which cannot query a knowledge graph.

MCP standardized the protocol layer (97M+ cumulative downloads). Skills marketplaces launched (500K+ packages across ecosystems). Frameworks like CrewAI, LangChain, and Claude Agent SDK handle orchestration. But a critical gap remains: **nothing auto-discovers trending repositories and makes them instantly usable as agent capabilities.**

That void is what OSS Agent Lab fills. It is a capability factory that continuously watches the open-source ecosystem, scores repositories on a composite 0-100 scale, and wraps top scorers into five output formats (Python API, CLI, MCP Server, Agent Skill, REST API) -- ready for any framework, any workflow, any stack.

---

## 2. Target Users

### Persona 1: Frontier Builders

**Profile:** Independent developers and researchers who track the bleeding edge of AI tooling. They read GitHub Trending daily and want last week's breakthroughs pre-wrapped and ready to use.

**Pain:** Manually cloning, reading docs, writing wrappers, and maintaining compatibility for repos that may be obsolete in two weeks. The discovery-to-productivity gap is measured in days, not minutes.

**Need:** Instant access to trending repo capabilities without manual integration work.

### Persona 2: Agent Developers

**Profile:** Engineers building agent systems on CrewAI, LangChain, AutoGen, or Claude Agent SDK. They need new capabilities (web browsing, research, financial analysis) without writing custom tool wrappers for each upstream repo.

**Pain:** Every new capability requires reading a repo's source, writing a wrapper, defining tool schemas, and maintaining it as the upstream changes. This consumes 40-60% of agent development time.

**Need:** Drop-in specialist modules that expose upstream repos as framework-compatible tools with stable contracts.

### Persona 3: AI Product Teams

**Profile:** Product engineers at startups and enterprises building AI-powered products. They need domain expertise -- stock analysis, sentiment detection, code research -- without building each capability from scratch.

**Pain:** Building domain-specific AI pipelines requires deep expertise in each domain plus ongoing maintenance. Hiring specialists for every vertical is not scalable.

**Need:** Production-ready, tested specialist modules with clear APIs that can be composed into product workflows.

### Persona 4: OSS Contributors

**Profile:** Open-source developers who have built a trending repo and want it to reach a wider audience. They want their repo usable as an agent capability without writing framework-specific integrations themselves.

**Pain:** Adoption plateaus after the initial star surge because users cannot easily integrate the repo into their existing agent workflows. Framework lock-in fragments the user base.

**Need:** A standardized path from "trending repo" to "usable capability" that generates all major integration formats automatically.

---

## 3. User Stories

### Frontier Builders

- As a frontier builder, I want to see this week's highest-scoring AI repos ranked by capability score, so that I can focus on the breakthroughs that matter most.
- As a frontier builder, I want to run a trending repo's capabilities with a single CLI command, so that I can evaluate it in minutes instead of days.
- As a frontier builder, I want specialists to auto-update when upstream repos ship breaking changes, so that my workflows do not silently break.

### Agent Developers

- As an agent developer, I want to import a specialist as a CrewAI tool with one line of code, so that I can add new capabilities to my agent without writing wrapper code.
- As an agent developer, I want all specialists to use the same Pydantic contract schemas, so that I can compose them without type conversion overhead.
- As an agent developer, I want the router to automatically dispatch my query to the right specialist(s), so that I do not need to manually select which tool to call.
- As an agent developer, I want each specialist to expose an MCP server, so that I can use it from Claude Desktop, Cursor, or any MCP-compatible client.

### AI Product Teams

- As a product engineer, I want a financial analysis specialist that combines OHLCV data with news signals, so that I can build investment research features without hiring a quant team.
- As a product engineer, I want sentiment analysis across social platforms via a REST API, so that I can integrate opinion intelligence into my product's backend.
- As a product engineer, I want 80%+ test coverage on every specialist, so that I can trust these modules in production.
- As a product engineer, I want isolated sandbox execution for untrusted code, so that specialists running user-provided code cannot compromise my infrastructure.

### OSS Contributors

- As an OSS contributor, I want a specialist scaffold generator that reads my repo and produces a working wrapper, so that I do not have to learn the OSS Agent Lab internals.
- As an OSS contributor, I want my repo's capabilities to be discoverable through the Temporal Capability Index, so that agent developers find and use my work.
- As an OSS contributor, I want a clear PR template and contributing guide, so that I can submit a specialist wrapper without back-and-forth.

---

## 4. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Specialists at v1 launch | 10 | Count of specialists passing all acceptance criteria |
| Test coverage per specialist | 80%+ | pytest-cov report per specialist module |
| End-to-end query latency | < 3 seconds | Time from NL input to aggregated response (local, warm cache) |
| Community PRs within 30 days of launch | 3+ | GitHub PR count from non-maintainer contributors |
| Output formats per specialist | 5/5 | Automated CI check: Python API, CLI, MCP, Skill, REST |
| Scoring engine source coverage | 6+ sources | Count of active scrapers in scoring/sources/ |
| Registry auto-discovery | 100% | All specialists in agents/specialists/ detected without manual config |

---

## 5. Scope (v1)

### In Scope

- **10 Specialists:** autoresearch, swarm_predict, deer_flow, browser_ai, knowledge_graph, stock_analyst, opinion_analyst, gui_agent, sandbox, repo_scanner
- **Scoring Engine:** 6 source scrapers (GitHub Trending, Hacker News, Papers With Code, Reddit r/MachineLearning, ArXiv CS.AI, X/Social Signals) feeding a weighted composite scorer (Discovery 40%, Quality 35%, Durability 25%)
- **Multi-Format Output:** Every specialist generates Python API, CLI tool, MCP server, Agent Skill, and REST API
- **Core Orchestration:** Conductor (NL interface + intent classification + task decomposition), Router (capability matching + parallel dispatch + result aggregation), Registry (auto-discovery from specialists/ directory)
- **Contract System:** Pydantic schemas for Query, Intent, SpecialistRequest, SpecialistResponse, SessionContext
- **Memory Layer:** cognee-based knowledge graph for cross-session context
- **QMD Integration:** BM25 + vector + LLM re-ranking for knowledge retrieval

### Non-Goals (v1)

| Non-Goal | Rationale |
|----------|-----------|
| SaaS / managed hosting | v1 is local-first and self-hosted. Cloud deployment is post-v1. |
| Proprietary specialists | All specialists must wrap MIT-compatible open-source repos. |
| Slack / Discord integration | Messaging integrations are post-v1. CLI, MCP, and REST cover v1 use cases. |
| Mobile application | Desktop and server workflows are the v1 target. |
| Paid tiers or licensing | v1 is fully open-source under MIT. Monetization decisions come later. |
| GUI dashboard | CLI and programmatic access only at v1. A web UI is post-v1. |

---

## 6. Acceptance Criteria

### Epic: Core Orchestration (E2)

- [ ] Conductor accepts natural language input and returns classified intent with confidence score
- [ ] Conductor decomposes multi-part queries into independent sub-tasks
- [ ] Router matches sub-tasks to specialists using capability index with >90% accuracy on test suite
- [ ] Router dispatches to multiple specialists in parallel and aggregates results
- [ ] Registry auto-discovers all specialists in agents/specialists/ without manual registration
- [ ] End-to-end flow (NL input -> classified intent -> routed dispatch -> aggregated response) completes in <3s

### Epic: First 3 Specialists (E3)

- [ ] autoresearch specialist wraps karpathy/autoresearch with hypothesis_generation, experiment_design, result_analysis capabilities
- [ ] swarm_predict specialist wraps 666ghj/MiroFish with multi_model_voting, swarm_consensus, prediction capabilities
- [ ] deer_flow specialist wraps bytedance/deer-flow with research, code_generation, creation_pipeline capabilities
- [ ] Each specialist passes 80%+ test coverage
- [ ] Each specialist generates all 5 output formats
- [ ] Each specialist conforms to contract schemas from agents/contracts/schemas.py

### Epic: Full Team (E4)

- [ ] Remaining 6 specialists (browser_ai, knowledge_graph, stock_analyst, opinion_analyst, gui_agent, sandbox) implemented
- [ ] All 6 meet the same bar: 80% coverage, 5 formats, contract compliance
- [ ] repo_scanner (specialist #10) can analyze a GitHub repo and generate a specialist scaffold

### Epic: Scoring Engine (E5)

- [ ] 6 source scrapers operational (GitHub Trending, HN, PwC, Reddit, ArXiv, X)
- [ ] Weighted composite scorer produces 0-100 scores with Discovery/Quality/Durability breakdown
- [ ] Temporal index tracks score changes over time
- [ ] Score thresholds trigger correct actions (80+ auto-scaffold, 60-79 flag, 40-59 watch, <40 skip)

### Epic: Meta-Agent + Launch (E6)

- [ ] repo_scanner auto-generates specialist scaffolds from high-scoring repos
- [ ] Multi-format output generation pipeline produces all 5 formats from specialist definition
- [ ] CI/CD pipeline validates coverage, linting, format generation on every PR
- [ ] README, CHANGELOG, and contributing guide are complete and accurate

---

## 7. Dependencies

| Dependency | Role | Risk |
|-----------|------|------|
| [Claude Agent SDK](https://github.com/anthropics/anthropic-sdk-python) | Foundation for conductor, router, and specialist agent implementations | Low -- stable, well-documented |
| [cognee](https://github.com/topoteretes/cognee) | Knowledge graph and memory layer | Medium -- active development, API may shift |
| [Lightpanda](https://github.com/nicepkg/gpt-runner) | Headless browser engine for browser_ai specialist | Medium -- newer project, monitoring stability |
| [OpenSandbox](https://github.com/anthropics/anthropic-quickstarts) | Isolated execution environment for sandbox specialist | Medium -- depends on container runtime availability |
| [LiteLLM](https://github.com/BerriAI/litellm) | Multi-provider LLM gateway for specialists needing model access | Low -- widely adopted, stable API |
| [qmd](https://github.com/tobi/qmd) | Local search engine with MCP integration for knowledge layer | Low -- simple CLI tool, minimal coupling |

---

## Appendix A: Naming Convention

This document follows **doc-filing v4.3** (NNN-CC-ABCD-description.md):

- **NNN:** Sequential number (001)
- **CC:** Category code (PP = Project Planning)
- **ABCD:** Subcategory (PROD = Product Requirements)
- **description:** Kebab-case human-readable name
