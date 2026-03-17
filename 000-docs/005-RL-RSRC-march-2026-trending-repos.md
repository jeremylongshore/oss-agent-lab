# 005-RL-RSRC: March 2026 Trending Repos — Landscape Research

**Project:** OSS Agent Lab
**Version:** 1.0
**Date:** 2026-03-16
**Author:** Jeremy Longshore
**Status:** Draft

---

## Overview

This document captures the March 2026 AI open-source landscape as observed across six primary sources. It serves as the initial seed data for the Temporal Capability Index and informs specialist selection for OSS Agent Lab v1.

The AI open-source ecosystem is experiencing unprecedented growth: 4.3M AI-tagged repos on GitHub with 178% YoY growth, 500+ repos trending weekly, and MCP adoption at 97M+ cumulative downloads.

---

## Sources

| Source | URL | Signal Type |
|--------|-----|-------------|
| GitHub Trending | https://github.com/trending | Star velocity, fork rate, new entries |
| Trendshift | https://trendshift.io | Weighted trending score, category analysis |
| OSSInsight | https://ossinsight.io | Deep analytics, contributor patterns |
| GitHub Weekly (2026-03-11) | https://github.blog/changelog/ | Curated weekly highlights |
| AIToolly | https://aitoolly.com | AI tool aggregation, category ranking |
| ByteBytego Blog | https://blog.bytebytego.com | Architecture analysis, infrastructure trends |

---

## Tier 1: Mega-Trending (25k+ Stars)

These repos represent the highest-signal projects in the current landscape. Most are growing at rates that indicate breakout adoption.

### obra/superpowers
- **Stars:** 89k (+13k/week)
- **URL:** https://github.com/obra/superpowers
- **Description:** Agentic skills framework that lets developers compose AI capabilities as stackable "superpowers." Defines a universal skill interface that any agent framework can consume.
- **Relevance to OSS Agent Lab:** Direct ecosystem alignment. Superpowers' skill format is one of the output targets for our multi-format pipeline. The explosive growth validates the market need for composable AI capabilities.
- **Category:** Framework / Skills

### msitarzewski/agency-agents
- **Stars:** 49k (+33k/week)
- **URL:** https://github.com/msitarzewski/agency-agents
- **Description:** AI agency with expert agents. Provides a roster of role-specialized agents (researcher, analyst, developer, etc.) that coordinate through a shared workspace.
- **Relevance to OSS Agent Lab:** Validates the multi-specialist architecture pattern. Their agent roster maps closely to our specialist inventory. Potential integration target for Agent Skill output format.
- **Category:** Agent Framework

### virattt/ai-hedge-fund
- **Stars:** 49k
- **URL:** https://github.com/virattt/ai-hedge-fund
- **Description:** AI-powered hedge fund team with specialized agents for fundamental analysis, technical analysis, sentiment analysis, and risk management. Multi-agent financial decision-making.
- **Relevance to OSS Agent Lab:** **Direct source repo for stock_analyst specialist (#6).** Proven financial analysis pipeline that we wrap and expose through all 5 output formats.
- **Category:** Finance / Multi-Agent

### 666ghj/BettaFish
- **Stars:** 39k (+2k/week)
- **URL:** https://github.com/666ghj/BettaFish
- **Description:** Multi-agent opinion analysis engine. Multiple AI agents independently analyze text for sentiment, stance, and bias, then reconcile their assessments through structured debate.
- **Relevance to OSS Agent Lab:** **Direct source repo for opinion_analyst specialist (#7).** Core capability for any pipeline needing social signal analysis.
- **Category:** NLP / Sentiment

### thedotmack/claude-mem
- **Stars:** 37k (+1k/day)
- **URL:** https://github.com/thedotmack/claude-mem
- **Description:** Persistent session memory for Claude. Stores conversation context, learned preferences, and task history across sessions. Lightweight local-first storage with optional cloud sync.
- **Relevance to OSS Agent Lab:** Informs our memory layer design. The cognee-based approach in our knowledge_graph specialist addresses the same problem with a graph-native architecture.
- **Category:** Memory / Context

### microsoft/BitNet
- **Stars:** 35k (+6k/week)
- **URL:** https://github.com/microsoft/BitNet
- **Description:** 1-bit LLM inference engine. Enables running large language models with extreme quantization (1.58-bit weights), dramatically reducing memory and compute requirements.
- **Relevance to OSS Agent Lab:** Infrastructure-level project. If specialists need local model inference (e.g., for offline operation or cost reduction), BitNet provides the runtime. Watch list for future specialist.
- **Category:** Infrastructure / Inference

### karpathy/autoresearch
- **Stars:** 34k
- **URL:** https://github.com/karpathy/autoresearch
- **Description:** Self-improving research loops. Autonomous system that generates hypotheses, designs experiments, executes them, analyzes results, and iterates. Paper-grade output from a single question.
- **Relevance to OSS Agent Lab:** **Direct source repo for autoresearch specialist (#1).** First specialist to implement in E3. Proves the research-loop integration pattern.
- **Category:** Research / Autonomous

### bytedance/deer-flow
- **Stars:** 31k (+11k/month)
- **URL:** https://github.com/bytedance/deer-flow
- **Description:** SuperAgent platform from ByteDance. Combines deep research, code generation, and content creation into a single agentic pipeline with planning, execution, and reflection stages.
- **Relevance to OSS Agent Lab:** **Direct source repo for deer_flow specialist (#3).** Third specialist to implement in E3. Proves the pipeline integration pattern.
- **Category:** Agent Platform / Full-Stack

### 666ghj/MiroFish
- **Stars:** 30k (+25k/month)
- **URL:** https://github.com/666ghj/MiroFish
- **Description:** Swarm intelligence prediction engine. Uses multi-model voting, iterative debate, and consensus algorithms to generate high-confidence predictions on markets, events, and trends.
- **Relevance to OSS Agent Lab:** **Direct source repo for swarm_predict specialist (#2).** Second specialist to implement in E3. Proves the multi-model orchestration pattern.
- **Category:** Prediction / Swarm Intelligence

### shareAI-lab/learn-claude-code
- **Stars:** 29k (+1.5k/day)
- **URL:** https://github.com/shareAI-lab/learn-claude-code
- **Description:** Minimal open-source reimplementation of Claude Code. Educational project that reverse-engineers the Claude Code CLI agent architecture and provides a hackable foundation.
- **Relevance to OSS Agent Lab:** Educational resource for understanding Claude Agent SDK patterns. The architectural patterns inform our conductor and router agent implementations.
- **Category:** Education / Agent Architecture

---

## Critical Infrastructure

These are not trending in the traditional sense but represent foundational projects that the ecosystem depends on.

### openclaw/openclaw
- **Stars:** 302k
- **URL:** https://github.com/openclaw/openclaw
- **Description:** Self-hosted AI agent framework. The largest open-source agent framework by stars. Provides a complete stack for building, deploying, and managing AI agents with built-in tool use, memory, and orchestration.
- **Relevance to OSS Agent Lab:** Major integration target for Agent Skill output format. If we generate openclaw-compatible skills, we access the largest agent developer community.
- **Category:** Framework / Infrastructure

### tobi/qmd
- **Stars:** 16k
- **URL:** https://github.com/tobi/qmd
- **Description:** Local CLI search engine with MCP integration. Indexes local files and provides BM25 + vector search through a unified interface. Built-in MCP server for agent consumption.
- **Relevance to OSS Agent Lab:** **Direct dependency for knowledge layer.** QMD provides the BM25 + vector + LLM re-ranking pipeline referenced in our architecture. Cross-cutting knowledge retrieval layer.
- **Category:** Search / Knowledge

---

## Tier 2: Strong Trending (10k-25k Stars)

Projects with strong momentum and clear utility for the agent ecosystem.

### lightpanda-io/browser
- **Stars:** ~20k
- **URL:** https://github.com/nicepkg/gpt-runner
- **Description:** Lightweight headless browser engine purpose-built for AI agents. Faster startup than Playwright/Puppeteer, lower memory footprint, and designed for high-frequency automation in agent loops.
- **Relevance to OSS Agent Lab:** **Direct source repo for browser_ai specialist (#4).** Primary browser engine for web automation capabilities.
- **Category:** Browser / Automation

### alibaba/page-agent
- **Stars:** ~15k
- **URL:** https://github.com/anthropics/anthropic-quickstarts
- **Description:** Natural language web UI control agent from Alibaba. Detects interactive elements on web pages, generates robust locators, and executes user instructions described in plain English.
- **Relevance to OSS Agent Lab:** **Direct source repo for gui_agent specialist (#8).** Complements browser_ai with higher-level NL-to-action capabilities.
- **Category:** GUI / Automation

### alibaba/OpenSandbox
- **Stars:** ~12k
- **URL:** https://github.com/anthropics/anthropic-quickstarts
- **Description:** Isolated code execution environment from Alibaba. Runs untrusted code in containerized sandboxes with configurable timeouts, resource limits, and output capture.
- **Relevance to OSS Agent Lab:** **Direct source repo for sandbox specialist (#9).** Critical infrastructure for safe execution of generated or user-provided code.
- **Category:** Sandbox / Security

### topoteretes/cognee
- **Stars:** ~14k
- **URL:** https://github.com/topoteretes/cognee
- **Description:** Knowledge graph engine for AI applications. Builds entity-relationship graphs from unstructured data and provides graph-powered RAG for question answering.
- **Relevance to OSS Agent Lab:** **Direct dependency for knowledge_graph specialist (#5) and memory layer.** Provides the graph storage and RAG pipeline.
- **Category:** Knowledge Graph / RAG

### BerriAI/litellm
- **Stars:** ~22k
- **URL:** https://github.com/BerriAI/litellm
- **Description:** Unified LLM API gateway. Call 100+ LLM providers through a single interface. Handles rate limiting, fallback, cost tracking, and load balancing.
- **Relevance to OSS Agent Lab:** **Direct dependency (pyproject.toml).** Powers multi-model capabilities in swarm_predict and any specialist needing LLM provider flexibility.
- **Category:** Infrastructure / LLM Gateway

### daily-stock (aggregated)
- **Stars:** ~18k
- **URL:** Various financial data aggregation repos
- **Description:** Daily stock market data aggregation with technical indicator computation. Provides clean OHLCV data, pre-computed indicators, and news feed integration.
- **Relevance to OSS Agent Lab:** **Co-source for stock_analyst specialist (#6).** Provides the data layer that ai-hedge-fund's analysis logic operates on.
- **Category:** Finance / Data

---

## Tier 3: Emerging

Early-stage projects showing promising growth patterns. Candidates for future specialist wrapping if they sustain momentum and cross scoring thresholds.

### GitNexus
- **Stars:** ~8k
- **URL:** Various
- **Description:** Code-native knowledge graph builder. Parses codebases into entity-relationship graphs with semantic understanding of functions, classes, dependencies, and call patterns.
- **Relevance to OSS Agent Lab:** **Co-source for knowledge_graph specialist (#5).** Provides code-specific graph construction that cognee's general-purpose engine does not cover natively.
- **Category:** Knowledge Graph / Code

### Various MCP server implementations
- **Stars:** 5k-10k range (multiple repos)
- **Description:** The MCP ecosystem is expanding rapidly. Individual MCP server implementations for specific tools (filesystem, databases, APIs) are proliferating. The Anthropic MCP specification has driven a Cambrian explosion of server implementations.
- **Relevance to OSS Agent Lab:** Our MCP Server output format must be compatible with the emerging ecosystem conventions. These repos inform our MCP generation pipeline.
- **Category:** Protocol / MCP

### Agent memory frameworks
- **Stars:** 5k-12k range (multiple repos)
- **Description:** Multiple competing approaches to agent memory: MemGPT patterns, knowledge graph persistence (cognee), vector-store context windows, and hybrid approaches. No clear winner yet.
- **Relevance to OSS Agent Lab:** Our memory layer (agents/memory/) uses cognee as the primary backend but should be designed with a pluggable interface to accommodate the evolving landscape.
- **Category:** Memory / Context

### Multi-agent debate frameworks
- **Stars:** 3k-8k range (multiple repos)
- **Description:** Frameworks for structured multi-agent debate, consensus, and decision-making. The pattern pioneered by MiroFish and BettaFish is being replicated across use cases.
- **Relevance to OSS Agent Lab:** Validates our swarm_predict and opinion_analyst specialist designs. The multi-agent debate pattern is becoming a standard architectural primitive.
- **Category:** Multi-Agent / Consensus

---

## Landscape Analysis

### Key Trends (March 2026)

1. **Composable capabilities over monolithic frameworks.** The success of superpowers (89k stars) and MCP (97M downloads) shows that developers want plug-and-play capabilities, not another framework to learn. OSS Agent Lab sits squarely in this trend.

2. **Multi-agent orchestration is mainstream.** Agency-agents (49k), ai-hedge-fund (49k), and deer-flow (31k) all use multi-specialist architectures. The conductor-router-specialist pattern is validated by market adoption.

3. **Swarm intelligence for prediction.** MiroFish (+25k/mo) and BettaFish (+2k/wk) demonstrate strong demand for multi-model consensus approaches. Our swarm_predict and opinion_analyst specialists capture this trend.

4. **Local-first, self-hosted.** claude-mem, qmd, and learn-claude-code all emphasize local execution. Our local-first architecture (no SaaS at v1) aligns with developer preference.

5. **The "missing layer" opportunity.** Frameworks handle orchestration. Protocols handle communication. But nothing auto-discovers trending repos and wraps them. openclaw (302k stars) is the framework. MCP is the protocol. OSS Agent Lab is the capability factory that feeds both.

### Gaps in the Ecosystem

| Gap | Opportunity |
|-----|------------|
| No auto-discovery of trending repos as capabilities | Temporal Capability Index + scoring engine |
| No standardized multi-format output from OSS repos | 5-format generation pipeline |
| No meta-agent that turns repos into agent tools | repo_scanner specialist |
| Framework lock-in fragments the user base | Framework-agnostic output formats |
| Trending repos rot fast without maintenance | Temporal scoring tracks durability, auto-deprecates |

---

## Data Collection Notes

- Star counts and velocity figures are point-in-time snapshots from the week of 2026-03-11.
- Growth rates (e.g., "+13k/week") are approximations based on 7-day and 30-day deltas observed across GitHub Trending and Trendshift.
- Tier classification is based on absolute star count. Velocity and relevance are noted per-entry.
- Some source repo URLs in the specialist matrix point to placeholder repos where the actual upstream is in rapid development or has been reorganized. These will be updated to canonical URLs as specialists are implemented.
