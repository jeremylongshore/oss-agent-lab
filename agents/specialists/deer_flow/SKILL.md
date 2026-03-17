---
name: deer_flow
display_name: Deer Flow Specialist
description: Full-stack research and code generation pipeline - research, code, and create
version: 0.1.0
source_repo: bytedance/deer-flow
license: MIT
tier: core
capabilities:
  - research
  - code_generation
  - creation
  - summarize
allowed_tools:
  - research_topic
  - generate_code
  - create_artifact
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Deer Flow Specialist

## Overview

The Deer Flow specialist wraps the [bytedance/deer-flow](https://github.com/bytedance/deer-flow)
SuperAgent pattern into a composable OSS Agent Lab specialist. It chains three stages into a
single pipeline:

1. **Research** — gathers structured findings and source attribution for any topic.
2. **Code Generation** — translates research summaries or explicit specifications into
   working implementations with matching test skeletons.
3. **Artifact Creation** — packages the pipeline outputs into a versioned, hash-identified
   deliverable in markdown, JSON, or HTML.

Each stage is also independently callable as a tool, making the specialist useful for
partial workflows (research-only, code-only, wrap-existing-content-in-artifact).

## Capabilities

- **research**: Gather findings, sources, a summary, and a confidence score for any topic.
  Supports `shallow`, `standard`, and `deep` depth settings.
- **code_generation**: Generate an implementation, test skeleton, and explanation from a
  natural-language specification. Supports Python and other languages.
- **creation**: Package any content dict into a versioned artifact with stable ID and
  creation metadata.
- **summarize**: The research stage always produces a concise summary suitable for direct
  use or downstream prompting.

## Tools

| Tool | Description | Parameters | Side Effects |
|------|-------------|------------|--------------|
| `research_topic` | Research a topic and return findings, sources, summary, confidence | `topic`, `depth`, `sources` | None |
| `generate_code` | Generate code, tests, and explanation from a specification | `specification`, `language`, `style` | None |
| `create_artifact` | Package content into a versioned artifact with metadata | `content`, `artifact_type`, `format` | None |

### Tool Parameter Reference

**`research_topic`**
- `topic: str` — subject to research (required)
- `depth: str` — `"shallow"` | `"standard"` | `"deep"` (default: `"standard"`)
- `sources: list[str] | None` — explicit source list; auto-selected when `None`

**`generate_code`**
- `specification: str` — natural-language description of the code to produce (required)
- `language: str` — target language, e.g. `"python"`, `"typescript"` (default: `"python"`)
- `style: str` — `"clean"` | `"verbose"` | `"minimal"` (default: `"clean"`)

**`create_artifact`**
- `content: dict[str, Any]` — pipeline outputs to embed (required)
- `artifact_type: str` — `"report"` | `"notebook"` | `"package"` | `"summary"` (default: `"report"`)
- `format: str` — `"markdown"` | `"json"` | `"html"` (default: `"markdown"`)

## Pipeline Flow

```
SpecialistRequest
       │
       ▼
  research_topic(topic, depth, sources)
       │
       ▼  (if code generation needed)
  generate_code(specification, language, style)
       │
       ▼
  create_artifact(content, artifact_type, format)
       │
       ▼
  SpecialistResponse(result={research, code?, artifact})
```

Code generation is triggered when:
- The intent action contains `"code"`
- The intent domain contains `"code_generation"`
- The request parameter `generate_code` is truthy (default: `True`)

## Usage

### Python API

```python
from agents.specialists.deer_flow.agent import DeerFlowSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = DeerFlowSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="research_and_build",
        domain="code_generation",
        confidence=0.95,
        parameters={"depth": "deep", "language": "python"},
    ),
    query=Query(user_input="async rate limiter with token bucket algorithm"),
    specialist_name="deer_flow",
)

response = await specialist.execute(request)
print(response.result["artifact"]["artifact_id"])
print(response.result["code"]["code"])
```

### CLI

```bash
oss-lab run deer_flow "async rate limiter with token bucket algorithm"
```

### Research-only (tool call)

```python
from agents.specialists.deer_flow.tools import research_topic

findings = research_topic(
    topic="transformer attention mechanisms",
    depth="deep",
    sources=["arxiv", "github"],
)
print(findings["summary"])
print(f"Confidence: {findings['confidence']}")
```

### Code generation standalone

```python
from agents.specialists.deer_flow.tools import generate_code

result = generate_code(
    specification="LRU cache with O(1) get and put operations",
    language="python",
    style="clean",
)
print(result["code"])
print(result["tests"])
```

## Source

Wraps [bytedance/deer-flow](https://github.com/bytedance/deer-flow) — a full-stack
multi-agent research framework featuring deep research, report generation, and
podcast/presentation creation pipelines built on top of LangGraph.
