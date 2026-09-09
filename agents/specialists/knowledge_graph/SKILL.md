---
name: knowledge_graph
description: Generate synthetic graph counts, ranked artificial entities, and relationship paths from input strings. Use when testing the Knowledge Graph response contract, not when analyzing real source code. Trigger with simulate knowledge graph.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; inputs are hashed but never read, cloned, parsed, persisted, or queried through GitNexus or cognee.'
tags: [knowledge-graph, graph-rag, simulation, offline, prototype]
argument-hint: '[query] [--source STRING] [--graph-type code|document|mixed]'
model: inherit
effort: low
display_name: Knowledge Graph Specialist
source_repo: abhigyanpatwari/GitNexus
tier: core
capabilities:
  - knowledge_graph
  - code_analysis
  - entity_linking
  - graph_rag
allowed_tools:
  - build_graph
  - query_graph
  - find_relationships
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Knowledge Graph Specialist

## Overview

`knowledge_graph` wraps patterns from
[abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) for code
entity extraction and graph construction, and
[topoteretes/cognee](https://github.com/topoteretes/cognee) for Graph RAG retrieval.

Given any source string, the specialist hashes that string and constructs a synthetic graph-shaped
response. It returns artificial entity lists, relevance scores, and relationship paths for exercising
downstream contracts. It does not parse or cite the named artifact.

The specialist is stateless. Each `execute` call creates a new graph UUID and self-contained result;
there is no previously built graph to retrieve across calls.

Those descriptions are interface goals, not current data processing. The implementation hashes the
source string and generates artificial counts, entities, scores, and paths; it has no stored graph.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Pass only a source identifier or sample text; paths and URLs are not opened.
- Read [the runtime contract](references/runtime-contract.md) before using the response.

## Capabilities

- **knowledge_graph**: Generate graph-shaped counts and type labels from a source-string hash.
- **code_analysis**: Exercise a code-analysis response schema with artificial entities.
- **entity_linking**: Generate deterministic-style IDs and synthetic paths for contract tests.
- **graph_rag**: Exercise ranking and path fields without retrieval or generation.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `build_graph` | Derive synthetic graph metadata from a source string | None |
| `query_graph` | Generate artificial ranked entities and paths | None |
| `find_relationships` | Generate artificial paths, types, and strength | None |

## Parameters

### Request-level (`intent.parameters`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `source` | `str` | *(query.user_input)* | Repository URL, file path, or raw code to ingest |
| `graph_type` | `str` | `"code"` | Entity strategy: `code`, `document`, or `mixed` |
| `max_depth` | `int` | `3` | Maximum cross-file traversal depth |
| `query` | `str` | *(query.user_input)* | Natural-language question to run against the graph |
| `max_results` | `int` | `10` | Result cap for graph queries |
| `entity_a` | `str` | `None` | Source entity for relationship search (optional) |
| `entity_b` | `str` | `None` | Target entity for relationship search (optional) |

### Graph types

- **code** — labels output with `module`, `class`, `function`, `variable`, and `import` types.
- **document** — labels output with `concept`, `section`, `claim`, and `reference` types.
- **mixed** — returns a combined synthetic type list.

## Output

```python
{
    "graph": {
        "graph_id": str,          # stable UUID for this graph instance
        "node_count": int,        # total entity nodes
        "edge_count": int,        # total directed relationship edges
        "entity_types": list[str],# entity labels present in the graph
        "graph_type": str,        # echo of requested graph_type
    },
    "query_results": {
        "results": list[dict],    # ranked entity hits
        "relevance_scores": list[float],  # parallel relevance values 0-1
        "paths": list[dict],      # connecting relationship paths
        "total_found": int,       # total matches before max_results cap
    },
    # only present when entity_a and entity_b are supplied:
    "relationships": {
        "paths": list[dict],      # all paths from entity_a to entity_b
        "relationship_types": list[str],  # deduplicated edge labels
        "strength": float,        # coupling strength 0-1
        "path_count": int,
    },
}
```

## Instructions

1. Supply a non-empty source string and query plus a supported graph type and bounded positive limits.
2. Run the specialist through the Python API or CLI.
3. Treat graph IDs as per-call identifiers and every entity/path as artificial fixture data.
4. Use a real parser or graph store when the task requires claims about source code.

## Examples

### Python API

```python
import asyncio
from agents.specialists.knowledge_graph.agent import KnowledgeGraphSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = KnowledgeGraphSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="knowledge_graph",
        domain="code_analysis",
        confidence=0.9,
        parameters={
            "source": "https://github.com/abhigyanpatwari/GitNexus",
            "graph_type": "code",
            "max_depth": 3,
        },
    ),
    query=Query(user_input="Which functions call the authentication module?"),
    specialist_name="knowledge_graph",
)

response = asyncio.run(specialist.execute(request))
print(response.result["graph"]["node_count"])
print(response.result["query_results"]["results"][0])
```

### CLI

```bash
oss-lab run knowledge_graph "Which functions call the authentication module?"
```

### With relationship search

```python
request = SpecialistRequest(
    intent=Intent(
        action="knowledge_graph",
        domain="code_analysis",
        confidence=0.9,
        parameters={
            "source": "./src/",
            "entity_a": "UserService",
            "entity_b": "DatabaseAdapter",
        },
    ),
    query=Query(user_input="How does UserService depend on DatabaseAdapter?"),
    specialist_name="knowledge_graph",
)
```

### CLI with parameters

```bash
oss-lab run knowledge_graph "dependency chain for PaymentProcessor" \
  --param source=https://github.com/owner/repo \
  --param graph_type=code \
  --param max_depth=5 \
  --param entity_a=PaymentProcessor \
  --param entity_b=DatabaseClient
```

## Error Handling

- Reject empty source or query values, unknown graph types, and non-positive depth/result limits.
- Do not claim that a path or URL was read merely because the result contains a graph ID.
- Do not cite synthetic entities or relationships as evidence about a repository.

## Resources

Wraps [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) and
[topoteretes/cognee](https://github.com/topoteretes/cognee).

The current local implementation is interface-only. See
[the runtime contract](references/runtime-contract.md).
