---
name: knowledge_graph
display_name: Knowledge Graph Specialist
description: Code knowledge graphs and Graph RAG — entity extraction, relationship mapping, and natural-language queries over source repositories
version: 0.1.0
source_repo: abhigyanpatwari/GitNexus
license: MIT
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

Given a source artifact — repository URL, file path, or raw code — the specialist
builds a directed knowledge graph of entities and relationships, then answers
natural-language questions through graph traversal.  Results are returned as ranked
entity lists, relevance scores, and explicit relationship paths, ready for downstream
reasoning or citation.

The specialist is stateless.  Each :meth:`execute` call builds a fresh graph and
returns a self-contained result dict.  Graph IDs can be passed across calls to query
a previously built graph without rebuilding.

## Capabilities

- **knowledge_graph**: Build a structured entity/relationship graph from code or
  documents, scoped by traversal depth and entity type.
- **code_analysis**: Extract modules, classes, functions, variables, and imports from
  source repositories, surfacing dependency and call-graph structure.
- **entity_linking**: Resolve named entities across files and modules into a unified
  graph, deduplicating references by stable entity ID.
- **graph_rag**: Answer natural-language queries via graph traversal and relevance
  ranking — Graph Retrieval-Augmented Generation over structured code knowledge.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `build_graph` | Build a knowledge graph from a source artifact | None (v1 local; future: network/disk) |
| `query_graph` | Query the graph with natural language; returns ranked entities and paths | None |
| `find_relationships` | Find all paths between two named entities; returns types and strength | None |

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

- **code** — extracts `module`, `class`, `function`, `variable`, `import` entities.
  Best for source repository analysis and call-graph reasoning.
- **document** — extracts `concept`, `section`, `claim`, `reference` entities.
  Suited for technical documentation or research papers.
- **mixed** — union of code and document types.  Use when the source combines
  runnable code with rich inline documentation.

## Response shape

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

## Usage

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

## Source

Wraps [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) and
[topoteretes/cognee](https://github.com/topoteretes/cognee).
