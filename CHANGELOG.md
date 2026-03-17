# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-17

### Added

- **3-Tier Orchestration Architecture**
  - Tier 1 Conductor: NL intent classification via Claude SDK
  - Tier 2 Router: SKILL.md auto-discovery, parallel dispatch, result aggregation
  - Tier 3 Specialists: 10 plug-and-play capability wrappers

- **10 Specialists** wrapping proven open-source repos
  - `autoresearch` — hypothesis generation, experiment design (karpathy/autoresearch)
  - `swarm_predict` — multi-model swarm predictions (666ghj/MiroFish)
  - `deer_flow` — research pipelines, code generation (bytedance/deer-flow)
  - `browser_ai` — headless navigation, content extraction (lightpanda-io/browser)
  - `knowledge_graph` — graph construction, relationship queries (cognee/GitNexus)
  - `stock_analyst` — ticker analysis, technical indicators (virattt/ai-hedge-fund)
  - `opinion_analyst` — sentiment analysis, stance detection (666ghj/BettaFish)
  - `gui_agent` — element detection, UI interaction (alibaba/page-agent)
  - `sandbox` — safe code execution, multi-runtime (alibaba/OpenSandbox)
  - `repo_scanner` — meta-specialist for auto-scaffolding new specialists

- **Capability Scoring Engine** (15 weighted signals, 7 live sources)
  - Discovery signals: GitHub star velocity, trending position, HN frontpage, DevHunt, Rundown
  - Quality signals: README quality, test coverage, API clarity, license, maintenance
  - Durability signals: contributor diversity, OSSInsight growth, Trendshift momentum
  - Temporal index with trend detection (rising/peaked/declining)
  - Automatic action thresholds: auto-scaffold (80+), evaluate (60-79), watch (40-59), skip (<40)

- **5 Output Formats** generated for every specialist
  - Python API — direct import
  - CLI Tool — shell scripting
  - MCP Server — Claude Desktop, Cursor integration
  - Agent Skill — CrewAI, LangChain compatibility
  - REST API — language-agnostic HTTP

- **Session Memory** with keyword-based recall and optional JSON persistence

- **CI/CD Pipeline** with 4 jobs: lint, test, validate-specialists, generate-outputs
  - ruff linting + formatting
  - mypy strict type checking
  - pytest with 65% coverage threshold
  - SKILL.md schema validation
  - Specialist import verification

- **189 tests** covering orchestration, specialists, scoring, contracts, and memory

- **Beads task tracking** with Dolt backend integration

### Changed

- Test coverage threshold raised from 60% to 65%
- Added `--strict-markers` to pytest configuration

[1.0.0]: https://github.com/jeremylongshore/oss-agent-lab/releases/tag/v1.0.0
