# 004-AT-DSGN: Specialist Inventory

**Project:** OSS Agent Lab
**Version:** 1.0
**Date:** 2026-03-16
**Author:** Jeremy Longshore
**Status:** Draft

---

## Overview

OSS Agent Lab v1 ships with 10 specialists. Each specialist wraps one or more proven open-source repositories, exposing their capabilities through a standardized contract interface and generating all 5 output formats (Python API, CLI, MCP Server, Agent Skill, REST API).

This document is the authoritative inventory of all v1 specialists, their source repos, capabilities, dependencies, and implementation status.

---

## Specialist Matrix

| # | Name | Source Repo | Capabilities | Tier | Status |
|---|------|-------------|-------------|------|--------|
| 1 | autoresearch | karpathy/autoresearch | hypothesis_generation, experiment_design, result_analysis | core | planned |
| 2 | swarm_predict | 666ghj/MiroFish | multi_model_voting, swarm_consensus, prediction | core | planned |
| 3 | deer_flow | bytedance/deer-flow | research, code_generation, creation_pipeline | core | planned |
| 4 | browser_ai | lightpanda-io/browser | navigate, click, extract, screenshot | core | planned |
| 5 | knowledge_graph | GitNexus + cognee | entity_linking, relationship_inference, graph_rag | core | planned |
| 6 | stock_analyst | ai-hedge-fund + daily_stock | ohlcv_analysis, technical_analysis, news_signals | core | planned |
| 7 | opinion_analyst | 666ghj/BettaFish | sentiment_analysis, stance_detection, bias_measurement | core | planned |
| 8 | gui_agent | alibaba/page-agent | element_detection, locator_generation, nl_interaction | core | planned |
| 9 | sandbox | alibaba/OpenSandbox | isolated_execution, timeout_management, output_capture | core | planned |
| 10 | repo_scanner | META (internal) | repo_analysis, specialist_scaffolding, pr_generation | core | planned |

---

## Specialist Details

### 1. autoresearch

**Description:** Self-improving research loops. Feed a question, get a paper-grade answer through iterative hypothesis generation, experiment design, and result analysis. The specialist orchestrates multi-step research workflows that progressively refine their own methodology.

**Source Repo:** [karpathy/autoresearch](https://github.com/karpathy/autoresearch) (34k stars)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `generate_hypothesis` | Generate testable hypotheses from a research question | None |
| `design_experiment` | Design experimental methodology for a hypothesis | None |
| `analyze_results` | Analyze experimental outputs and synthesize conclusions | None |
| `run_research_loop` | Full autonomous research loop (compose all three steps) | Network (API calls to LLM provider) |

**Dependencies:** anthropic, httpx

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E3

---

### 2. swarm_predict

**Description:** Swarm intelligence prediction engine. Uses multi-model voting and consensus algorithms to generate predictions across markets, events, and trends. Multiple LLMs debate, vote, and converge on high-confidence predictions.

**Source Repo:** [666ghj/MiroFish](https://github.com/666ghj/MiroFish) (30k stars)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `multi_model_vote` | Run a prediction question through multiple models and aggregate votes | Network (multi-provider LLM calls) |
| `swarm_consensus` | Iterative debate rounds until convergence threshold is met | Network (multi-provider LLM calls) |
| `predict` | Single-shot prediction with confidence interval | Network |

**Dependencies:** litellm, anthropic, pydantic

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E3

---

### 3. deer_flow

**Description:** Full-stack research and code generation pipeline. Combines deep research capabilities with code generation and creation workflows. Acts as a SuperAgent that can research a topic, generate implementation code, and produce complete deliverables.

**Source Repo:** [bytedance/deer-flow](https://github.com/bytedance/deer-flow) (31k stars)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `research` | Deep research on a topic with source citation | Network |
| `generate_code` | Generate implementation code from research findings | Filesystem (writes code files) |
| `creation_pipeline` | End-to-end pipeline: research -> design -> implement -> test | Filesystem, Network |

**Dependencies:** anthropic, httpx

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E3

---

### 4. browser_ai

**Description:** Headless web automation for data extraction and interaction. Provides programmatic browser control through natural language commands -- navigate to URLs, click elements, extract structured data, and capture screenshots.

**Source Repo:** [lightpanda-io/browser](https://github.com/nicepkg/gpt-runner)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `navigate` | Navigate to a URL and wait for page load | Network |
| `click` | Click an element identified by selector or description | Network, DOM mutation |
| `extract` | Extract structured data from current page | None (read-only) |
| `screenshot` | Capture screenshot of current viewport or element | Filesystem (writes image) |

**Dependencies:** lightpanda (or playwright fallback), httpx

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E4

---

### 5. knowledge_graph

**Description:** Code knowledge graphs with RAG-powered querying. Builds entity-relationship graphs from codebases and documentation, then answers questions using a hybrid retrieval pipeline (BM25 + vector + LLM re-ranking).

**Source Repo:** GitNexus + [cognee](https://github.com/topoteretes/cognee)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `entity_linking` | Extract and link entities from text or code to the knowledge graph | Database (graph writes) |
| `relationship_inference` | Infer relationships between entities using graph patterns and LLM | Network |
| `graph_rag` | Answer questions using hybrid retrieval over the knowledge graph | Network, Database (reads) |

**Dependencies:** cognee, pydantic

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E4

---

### 6. stock_analyst

**Description:** Multi-signal financial analysis combining OHLCV price data with technical indicators and news sentiment. Provides institutional-grade analysis without requiring quant expertise.

**Source Repo:** [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) (49k stars) + daily_stock

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `ohlcv_analysis` | Fetch and analyze OHLCV price data for a ticker | Network (market data API) |
| `technical_analysis` | Run technical indicators (RSI, MACD, Bollinger, etc.) on price data | None |
| `news_signals` | Aggregate and score news sentiment for a ticker or sector | Network |

**Dependencies:** httpx, pandas (optional)

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E4

---

### 7. opinion_analyst

**Description:** Sentiment analysis at scale across social platforms. Detects sentiment, stance, and bias in text corpora using multi-agent opinion analysis pipelines.

**Source Repo:** [666ghj/BettaFish](https://github.com/666ghj/BettaFish) (39k stars)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `sentiment_analysis` | Classify sentiment (positive/negative/neutral) with confidence scores | None |
| `stance_detection` | Detect stance toward a target topic or entity | None |
| `bias_measurement` | Identify and quantify bias dimensions in text | None |

**Dependencies:** litellm, anthropic

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E4

---

### 8. gui_agent

**Description:** Natural language control of web UIs. Detects page elements, generates robust locators, and executes interactions described in plain English. Turns "click the login button" into reliable automated actions.

**Source Repo:** [alibaba/page-agent](https://github.com/anthropics/anthropic-quickstarts)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `element_detection` | Detect and catalog interactive elements on a page | Network |
| `locator_generation` | Generate robust CSS/XPath locators for detected elements | None |
| `nl_interaction` | Execute a natural language instruction on the current page | Network, DOM mutation |

**Dependencies:** playwright (or lightpanda), anthropic

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E4

---

### 9. sandbox

**Description:** Safe, isolated code execution environments. Runs untrusted code in containerized sandboxes with configurable timeouts, resource limits, and output capture. Essential for specialists that execute user-provided or generated code.

**Source Repo:** [alibaba/OpenSandbox](https://github.com/anthropics/anthropic-quickstarts)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `isolated_execution` | Execute code in an isolated container with resource limits | Container lifecycle |
| `timeout_management` | Configure and enforce execution timeouts | None |
| `output_capture` | Capture stdout, stderr, exit code, and generated files from execution | Filesystem (read from container) |

**Dependencies:** docker (or podman), httpx

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E4

---

### 10. repo_scanner

**Description:** The meta-specialist. Watches the Temporal Capability Index and auto-generates new specialist scaffolds when a repo crosses the auto-scaffold threshold (score 80+). Analyzes repo structure, infers capabilities, generates the four required files (agent.py, tools.py, SKILL.md, README.md), and opens a PR.

**Source Repo:** META (internal -- built from scratch within OSS Agent Lab)

**Key Tools:**

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `repo_analysis` | Clone and analyze a GitHub repo to infer capabilities, API surface, and dependencies | Network, Filesystem |
| `specialist_scaffolding` | Generate agent.py, tools.py, SKILL.md, README.md from analysis results | Filesystem (writes specialist files) |
| `pr_generation` | Create a branch, commit scaffold files, and open a GitHub PR | Git operations, Network |

**Dependencies:** anthropic, httpx, gitpython

**Output Formats:** Python API, CLI, MCP Server, Agent Skill, REST API

**Implementation Phase:** E6

---

## Implementation Order

```
Phase E3 (pattern proof):    autoresearch → swarm_predict → deer_flow
Phase E4 (full team):        browser_ai → knowledge_graph → stock_analyst → opinion_analyst → gui_agent → sandbox
Phase E6 (meta-agent):       repo_scanner
```

The first three specialists in E3 are chosen to prove three distinct integration patterns:
1. **autoresearch** -- research loop pattern (iterative, self-refining)
2. **swarm_predict** -- multi-model orchestration pattern (fan-out, consensus)
3. **deer_flow** -- pipeline pattern (sequential stages with artifacts)

Lessons from E3 inform the template refinements applied in E4.

---

## Quality Bar (All Specialists)

Every specialist must meet the following criteria before merging:

- [ ] 80%+ test coverage (pytest-cov)
- [ ] All 5 output formats generated and tested
- [ ] Pydantic contract schemas from `agents/contracts/schemas.py`
- [ ] SKILL.md manifest with accurate capability declarations
- [ ] README.md with usage examples for all output formats
- [ ] MIT-compatible license on upstream source repo
- [ ] Integration test with conductor-router pipeline
