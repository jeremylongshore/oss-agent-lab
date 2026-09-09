---
name: deer_flow
description: Exercise an offline prototype that returns synthetic research findings, code stubs, and packaged artifact dictionaries. Use when testing a Deer Flow-shaped pipeline contract. Trigger with prototype research and code.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; no web research or model-backed code generation occurs, and artifacts are returned in memory rather than written.'
tags: [research, code-generation, simulation, artifacts, prototype]
argument-hint: '[task] [--depth shallow|standard|deep]'
model: inherit
effort: low
display_name: Deer Flow Specialist
source_repo: bytedance/deer-flow
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

1. **Research fixture** — formats numbered findings and caller-supplied or synthetic source labels.
2. **Code stub** — translates a specification into a TODO implementation and test skeleton.
3. **Artifact envelope** — packages the dictionaries with a hash-derived ID and format label.

Each stage is also independently callable as a tool, making the specialist useful for
partial workflows (research-only, code-only, wrap-existing-content-in-artifact).

The present tools are offline contract stubs. Research findings are formatted fixtures, generated
code is a `NotImplementedError` skeleton, and artifacts are in-memory dictionaries rather than files.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Do not treat source labels, confidence, code, or artifacts as externally generated evidence.
- Read [the runtime contract](references/runtime-contract.md) for supported values and defaults.

## Authentication

None. The current implementation is local and makes no external request. Do not provide API keys or
tokens; a future network-backed implementation must document its own credential boundary.

## Capabilities

- **research**: Generate findings, labels, a summary, and a fixture confidence score for a topic.
  Supports `shallow`, `standard`, and `deep` depth settings.
- **code_generation**: Generate an implementation stub, test skeleton, and explanation from a
  natural-language specification. Supports Python and other languages.
- **creation**: Package any content dict into an in-memory envelope with a stable ID and
  creation metadata.
- **summarize**: The research stage always produces a concise summary suitable for direct
  use or downstream prompting.

## Tools

| Tool | Description | Parameters | Side Effects |
|------|-------------|------------|--------------|
| `research_topic` | Generate fixture findings, labels, summary, and confidence | `topic`, `depth`, `sources` | None |
| `generate_code` | Generate code and test stubs from a specification | `specification`, `language`, `style` | None |
| `create_artifact` | Package content into an in-memory envelope | `content`, `artifact_type`, `format` | None |

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

## Instructions

1. Provide a non-empty task and choose a supported depth, style, artifact type, and format.
2. Disable code generation explicitly when only the synthetic research shape is needed.
3. Run the local Python API or CLI and inspect the structured result.
4. Label every result as prototype output; never present it as live research or completed code.

## Examples

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

## Output

The response includes synthetic `research`, optional code and tests stubs, and an `artifact` dictionary
with a hash-derived ID and timestamp. It does not write the declared Markdown, JSON, or HTML format.

## Error Handling

- Reject unsupported depth, style, artifact type, or format values.
- Reject an empty code specification or empty artifact content.
- Treat generated TODOs and `NotImplementedError` as deliberate stubs requiring implementation.

## Resources

Wraps [bytedance/deer-flow](https://github.com/bytedance/deer-flow) — a full-stack
multi-agent research framework featuring deep research, report generation, and
podcast/presentation creation pipelines built on top of LangGraph.

The local specialist only mirrors a response shape. See
[the runtime contract](references/runtime-contract.md).
