# 006-RL-PROP: Bob's Brain to OSS Agent Lab -- Porting Decisions

**Category:** Research Log -- Proposal
**Status:** Final
**Date:** 2026-03-16
**Author:** Jeremy Longshore

---

## Purpose

This document records the architectural decisions made when porting concepts from Bob's Brain (a Google ADK-based IAM compliance agent system) to OSS Agent Lab (a Claude SDK-based trending-repo capability factory). Each row in the comparison table below gets a rationale section explaining what changed, why, and what the implications are.

---

## Comparison Matrix

| # | Bob's Brain (ADK) | OSS Agent Lab | Why |
|---|-------------------|---------------|-----|
| 1 | `google-adk` LlmAgent | `claude_agent_sdk` ClaudeSDKClient | User requirement: Claude SDK only |
| 2 | A2A protocol (JSONRPC) | Claude SDK subagent + MCP tools | Native Claude pattern, simpler |
| 3 | Vertex AI Agent Engine | Local execution + optional Cloud Run | No vendor lock-in |
| 4 | AgentCard (.well-known/) | SKILL.md + contracts/ | Consistent with ecosystem |
| 5 | Hard Mode R1-R8 | SDK-only, schema-validated, tested | Less rigid, more composable |
| 6 | 8 IAM specialists | 10 trending-repo specialists | Domain shift: compliance to capabilities |
| 7 | Dual Memory (Vertex) | cognee + local persistence | Open source, portable |

---

## 1. LLM Client: google-adk LlmAgent to claude_agent_sdk ClaudeSDKClient

Bob's Brain used `google-adk`'s `LlmAgent` class, which tied the orchestration layer to Google's Gemini models via Vertex AI. Every agent was instantiated through the ADK's agent lifecycle, which handled prompt injection, tool binding, and response parsing through Google's proprietary abstractions.

OSS Agent Lab replaces this with `claude_agent_sdk`'s `ClaudeSDKClient`. This is a hard user requirement -- the entire system must run on Claude. The practical impact is that prompt engineering, tool schemas, and response parsing all follow Anthropic's conventions rather than Google's. The `ClaudeSDKClient` provides native support for extended thinking, tool use with schema validation, and structured output, which eliminates the need for the custom parsing layers Bob's Brain had to build on top of ADK.

The trade-off is single-vendor LLM dependency at the orchestration level. To mitigate this, individual specialists can use LiteLLM as an adapter layer when a specific task benefits from a different model, but the conductor, router, and core orchestration remain Claude-only.

---

## 2. Inter-Agent Communication: A2A Protocol to Claude SDK Subagent + MCP Tools

Bob's Brain implemented Google's Agent-to-Agent (A2A) protocol, a JSONRPC-based communication standard where each agent exposed a `.well-known/agent.json` endpoint. Agents discovered each other via AgentCards and communicated through structured JSONRPC calls. This was architecturally clean but operationally heavy -- every agent needed its own HTTP server, its own discovery endpoint, and its own JSONRPC handler.

OSS Agent Lab drops A2A entirely in favor of Claude SDK's native subagent pattern combined with MCP tool exposure. The conductor spawns the router as a subagent. The router spawns specialists as subagents. Communication happens through Claude's built-in message passing rather than HTTP. For external consumers, specialists expose their capabilities as MCP tools, which is the standard the broader ecosystem has converged on (97M+ MCP downloads and growing).

This is simpler to develop, simpler to debug, and simpler to deploy. The cost is that agents are no longer independently addressable HTTP services. For a local-first capability factory, that cost is negligible.

---

## 3. Execution Environment: Vertex AI Agent Engine to Local Execution

Bob's Brain was designed to deploy on Vertex AI Agent Engine, Google's managed runtime for agent workloads. This provided automatic scaling, managed state, and integrated monitoring, but it also meant Google Cloud was a hard dependency. Running locally required emulating Vertex behaviors with stubs, which was fragile.

OSS Agent Lab inverts this. The primary execution target is a local machine -- `pip install -e .` and run. No cloud account required. For users who want persistent deployment, the same codebase runs on a self-hosted server or in a Docker container. Cloud Run is documented as an optional target for users who want managed scaling, but nothing in the codebase assumes cloud infrastructure.

This decision directly supports the local-first philosophy. It also makes development faster -- no deploy cycles, no cloud permissions, no billing surprises.

---

## 4. Agent Metadata: AgentCard (.well-known/) to SKILL.md + contracts/

Bob's Brain followed A2A's `AgentCard` specification. Each agent published a JSON document at `/.well-known/agent.json` containing its name, description, capabilities, and endpoint URL. This worked well for HTTP-based agent discovery but was disconnected from the agent's actual code.

OSS Agent Lab replaces AgentCard with `SKILL.md`, a YAML-frontmatter Markdown file co-located with the specialist's source code. The frontmatter contains machine-readable metadata (name, version, capabilities, allowed tools, tier). The body contains human-readable documentation. Because SKILL.md lives in the same directory as `agent.py` and `tools.py`, there is no drift between metadata and implementation -- CI validates that `capabilities` in SKILL.md match what `agent.py` actually implements, and `allowed_tools` match what `tools.py` exports.

The `contracts/` directory provides Pydantic schemas that formalize the data structures flowing between agents. This replaces the implicit contracts that A2A's JSONRPC messages carried.

---

## 5. Quality Enforcement: Hard Mode R1-R8 to SDK-Only, Schema-Validated, Tested

Bob's Brain defined "Hard Mode" as a set of 8 rigid rules (R1 through R8) that governed how agents were built: no mock LLM calls, real tool execution, validated outputs, etc. These rules were documented but enforced manually through code review.

OSS Agent Lab keeps the spirit but changes the mechanism. Instead of numbered rules, quality is enforced through three automated gates:

- **SDK-only**: All orchestration uses Claude SDK. No raw HTTP calls to LLM endpoints. This is enforced by linting rules.
- **Schema-validated**: All inter-agent data passes through Pydantic models from `contracts/schemas.py`. Invalid data fails fast with clear error messages.
- **Tested**: 80%+ test coverage per specialist, enforced by CI. No specialist merges without passing the coverage gate.

This is less rigid in form but more composable in practice. A specialist author does not need to memorize eight rules. They need to implement the template, pass the schemas, and hit coverage. The constraints are embedded in the tooling rather than in a manifesto.

---

## 6. Domain: 8 IAM Specialists to 10 Trending-Repo Specialists

Bob's Brain was a compliance system. Its 8 specialists covered IAM-specific tasks: policy analysis, permission auditing, role recommendation, compliance checking, and related operations. The domain was narrow and well-defined.

OSS Agent Lab is a capability factory. Its 10 specialists cover diverse domains: research automation (autoresearch, deer-flow), market intelligence (swarm-predict, stock-analyst, opinion-analyst), web interaction (browser-ai, gui-agent), knowledge management (knowledge-graph), safe execution (sandbox), and meta-operations (repo-scanner). The domain is broad and intentionally open-ended.

The architectural consequence is that Bob's Brain specialists could share domain-specific schemas and assumptions. OSS Agent Lab specialists cannot -- an autoresearch specialist and a stock-analyst specialist have almost nothing in common except the contract interface. This is why the contracts layer and SKILL.md specification are so important: they provide the only shared vocabulary across a heterogeneous specialist pool.

The 10th specialist (repo-scanner) is a meta-specialist that does not exist in Bob's Brain. It watches the Temporal Capability Index and proposes new specialist scaffolds when a repo crosses the auto-scaffold threshold. This makes the system self-extending.

---

## 7. Memory: Dual Memory (Vertex) to cognee + Local Persistence

Bob's Brain used Vertex AI's managed memory services for both short-term (session) and long-term (persistent) memory. Short-term memory lived in Vertex's session store. Long-term memory used Vertex's vector search for semantic retrieval. Both were fully managed, which was convenient but created a hard dependency on Google Cloud.

OSS Agent Lab replaces this with cognee, an open-source cognitive memory framework, backed by local file persistence. cognee provides semantic chunking, knowledge graph construction, and retrieval -- capabilities comparable to what Vertex offered, but running locally and portably. Memory state persists to disk in a configurable directory (`OSS_LAB_MEMORY_DIR`).

For users who want cloud-backed persistence, the memory layer is abstracted behind an interface that could be swapped for any backend. But the default is local, consistent with the local-first philosophy.

---

## What Was Kept

Three core patterns survived the port unchanged:

### 3-Tier Agent Hierarchy

Bob's Brain had Orchestrator, Router, and Specialists. OSS Agent Lab has Conductor, Router, and Specialists. The names changed but the pattern is identical: a top-level agent that decomposes intent, a middle layer that matches tasks to capabilities, and a bottom layer of specialized workers. This pattern proved robust in Bob's Brain and there was no reason to change it.

### Specialist Contracts

Both systems enforce a contract at the specialist boundary. In Bob's Brain, this was an implicit contract defined by the A2A message schema. In OSS Agent Lab, it is an explicit contract defined by Pydantic models in `contracts/schemas.py`. The principle is the same: specialists are black boxes that accept a defined input and produce a defined output. The orchestration layer never reaches into specialist internals.

### Registry Pattern

Bob's Brain had a registry that tracked available agents and their capabilities. OSS Agent Lab has the same pattern, extended with the SKILL.md frontmatter as the registration data source. The router queries the registry to find which specialists can handle a given task. The registry is populated at startup by scanning the `agents/specialists/` directory and parsing each specialist's SKILL.md frontmatter.

---

## What Is New

Three significant additions have no precedent in Bob's Brain:

### Temporal Capability Index

Bob's Brain had a fixed set of specialists. OSS Agent Lab has a dynamic discovery layer that continuously monitors 6+ sources (GitHub Trending, Hacker News, Papers With Code, Reddit, ArXiv, X/social) and scores every discovered repo on a composite 0-100 scale. This is the system's primary differentiator -- it makes the specialist pool self-updating rather than static.

### Multi-Format Output

Bob's Brain specialists produced a single output format (structured JSON via A2A). OSS Agent Lab specialists produce 5 formats simultaneously: Python API, CLI, MCP Server, Agent Skill, and REST API. This makes every specialist immediately consumable by any framework, any workflow, and any language.

### Scoring Engine

The Capability Score (0-100) is computed from three signal groups: Discovery (40%), Quality (35%), and Durability (25%). Each group aggregates multiple data sources into a normalized sub-score. The composite score drives automation: repos scoring 80+ get auto-scaffolded into new specialists, 60-79 get flagged for manual evaluation, and below 40 get skipped. This scoring engine has no equivalent in Bob's Brain, which had no concept of automated capability discovery.
