"""
Tools for the KnowledgeGraph specialist.

Implements code knowledge graph construction and Graph RAG query patterns
inspired by abhigyanpatwari/GitNexus and topoteretes/cognee.

Each function is a pure transformation — no I/O side effects in v1.
Real backends (graph databases, embedding stores, code parsers) would be
injected via a context or registry rather than hard-coded here.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any


def build_graph(
    source: str,
    graph_type: str = "code",
    max_depth: int = 3,
) -> dict[str, Any]:
    """Build a knowledge graph from a source artifact.

    Parses the source (repository URL, file path, or raw code snippet) and
    constructs a directed knowledge graph up to ``max_depth`` traversal hops.
    Entity types extracted depend on ``graph_type``:

    - ``"code"``: modules, classes, functions, variables, imports.
    - ``"document"``: concepts, sections, claims, references.
    - ``"mixed"``: union of code and document entity types.

    Args:
        source: Repository URL, local file path, or raw code/text to ingest.
            Examples: ``"https://github.com/owner/repo"``, ``"./src/"``,
            ``"def foo(): ..."``.
        graph_type: The entity extraction strategy.  One of ``"code"``,
            ``"document"``, or ``"mixed"``.  Defaults to ``"code"``.
        max_depth: Maximum traversal depth when resolving cross-file or
            cross-module relationships.  Must be >= 1.  Defaults to 3.

    Returns:
        A dict with:
            - ``graph_id``: Stable UUID identifying this graph instance.
            - ``node_count``: Total number of entity nodes extracted.
            - ``edge_count``: Total number of directed relationship edges.
            - ``entity_types``: List of entity type labels present in the graph.
            - ``graph_type``: Echo of the requested graph type.
            - ``max_depth``: Echo of the depth limit used.
            - ``source_hash``: SHA-256 prefix of the source string for
              deduplication / cache keying.

    Raises:
        ValueError: If ``graph_type`` is not one of the supported values, or
            if ``max_depth`` < 1.
    """
    valid_graph_types = {"code", "document", "mixed"}
    if graph_type not in valid_graph_types:
        raise ValueError(
            f"graph_type must be one of {sorted(valid_graph_types)}, got {graph_type!r}"
        )
    if max_depth < 1:
        raise ValueError(f"max_depth must be >= 1, got {max_depth}")

    entity_type_map: dict[str, list[str]] = {
        "code": ["module", "class", "function", "variable", "import"],
        "document": ["concept", "section", "claim", "reference"],
        "mixed": ["module", "class", "function", "variable", "import", "concept", "claim"],
    }
    entity_types = entity_type_map[graph_type]

    # Derive a stable seed from source content for reproducible simulated counts.
    source_hash = hashlib.sha256(source.encode()).hexdigest()[:12]
    seed = int(source_hash, 16) % (2**32)

    # Simulated node/edge counts that scale with depth and source complexity.
    base_nodes = 20 + (seed % 80)
    node_count = base_nodes * max_depth
    edge_count = int(node_count * 1.8)

    return {
        "graph_id": str(uuid.uuid4()),
        "node_count": node_count,
        "edge_count": edge_count,
        "entity_types": entity_types,
        "graph_type": graph_type,
        "max_depth": max_depth,
        "source_hash": source_hash,
    }


def query_graph(
    query: str,
    graph_id: str | None = None,
    max_results: int = 10,
) -> dict[str, Any]:
    """Query a knowledge graph using natural language.

    Translates a free-text query into a graph traversal and returns the most
    relevant entity nodes with relevance scores and the paths that connect
    them.  When ``graph_id`` is ``None`` the most recently built graph in
    the current session is used.

    Args:
        query: Natural-language question or keyword expression to search for.
            Examples: ``"Who calls authenticate()"``,
            ``"dependencies of UserService"``.
        graph_id: UUID returned by :func:`build_graph` that identifies the
            target graph.  Defaults to ``None`` (implicit latest graph).
        max_results: Maximum number of entity results to return.  Must be
            >= 1.  Defaults to 10.

    Returns:
        A dict with:
            - ``results``: List of up to ``max_results`` entity dicts, each
              with ``entity_id``, ``label``, ``type``, and ``snippet``.
            - ``relevance_scores``: Parallel list of float scores in [0, 1]
              for each result entry.
            - ``paths``: List of path dicts, each with ``from``, ``to``,
              ``relationship``, and ``hops``.
            - ``graph_id``: The graph that was queried (echoed or inferred).
            - ``query``: Echo of the input query.
            - ``total_found``: Total matching entities before limiting.

    Raises:
        ValueError: If ``max_results`` < 1.
    """
    if max_results < 1:
        raise ValueError(f"max_results must be >= 1, got {max_results}")

    resolved_graph_id = graph_id or str(uuid.uuid4())

    # Derive a deterministic seed from query + graph_id for reproducibility.
    seed = sum(ord(c) for c in query + resolved_graph_id) % 997
    total_found = 10 + (seed % 40)
    count = min(max_results, total_found)

    entity_types_cycle = ["function", "class", "module", "variable", "import"]
    results: list[dict[str, Any]] = []
    relevance_scores: list[float] = []

    for i in range(count):
        etype = entity_types_cycle[i % len(entity_types_cycle)]
        label = f"{etype}_{query.split()[0].lower()}_{i}"
        results.append(
            {
                "entity_id": f"e_{seed}_{i:03d}",
                "label": label,
                "type": etype,
                "snippet": f"# {label} — matched query term '{query.split()[0]}'",
            }
        )
        # Relevance decays from ~0.95 with small variation.
        score = round(max(0.30, 0.95 - i * 0.06 + (((seed + i * 7) % 11) - 5) * 0.01), 4)
        relevance_scores.append(score)

    # Synthesise a handful of relationship paths.
    paths: list[dict[str, Any]] = []
    for i in range(min(3, count - 1)):
        paths.append(
            {
                "from": results[i]["entity_id"],
                "to": results[i + 1]["entity_id"],
                "relationship": ["calls", "imports", "inherits", "references"][i % 4],
                "hops": i + 1,
            }
        )

    return {
        "results": results,
        "relevance_scores": relevance_scores,
        "paths": paths,
        "graph_id": resolved_graph_id,
        "query": query,
        "total_found": total_found,
    }


def find_relationships(
    entity_a: str,
    entity_b: str,
    graph_id: str | None = None,
) -> dict[str, Any]:
    """Find all relationship paths between two named entities in the graph.

    Performs a bidirectional graph search between ``entity_a`` and
    ``entity_b``, returning every discovered path, the relationship types
    found along those paths, and a strength score indicating how tightly the
    entities are coupled.

    Args:
        entity_a: Name or entity ID of the source entity.
        entity_b: Name or entity ID of the target entity.
        graph_id: UUID of the graph to search.  Defaults to ``None``
            (implicit latest graph).

    Returns:
        A dict with:
            - ``paths``: List of path dicts, each with ``steps`` (ordered
              list of entity labels traversed), ``relationship_sequence``
              (edge labels along the path), and ``length`` (hop count).
            - ``relationship_types``: Deduplicated list of edge label strings
              seen across all paths.
            - ``strength``: Float in [0, 1] estimating coupling strength.
              Higher values indicate shorter, more direct paths.
            - ``entity_a``: Echo of the source entity name.
            - ``entity_b``: Echo of the target entity name.
            - ``graph_id``: The graph that was searched (echoed or inferred).
            - ``path_count``: Number of distinct paths found.
    """
    resolved_graph_id = graph_id or str(uuid.uuid4())

    # Stable seed from both entity names and graph.
    seed = sum(ord(c) for c in entity_a + entity_b + resolved_graph_id) % 997

    relationship_labels = ["calls", "imports", "inherits", "references", "instantiates"]
    path_count = 1 + (seed % 4)  # 1-4 paths

    paths: list[dict[str, Any]] = []
    all_relationship_types: set[str] = set()

    for i in range(path_count):
        hops = 1 + (seed + i) % 3  # 1-3 hops
        # Build intermediate entity labels for multi-hop paths.
        intermediates = [f"intermediate_{(seed + i * 3 + j) % 99}" for j in range(hops - 1)]
        steps = [entity_a, *intermediates, entity_b]
        rel_sequence = [
            relationship_labels[(seed + i + j) % len(relationship_labels)]
            for j in range(len(steps) - 1)
        ]
        all_relationship_types.update(rel_sequence)
        paths.append(
            {
                "steps": steps,
                "relationship_sequence": rel_sequence,
                "length": hops,
            }
        )

    # Strength inversely proportional to average path length, with a seed nudge.
    avg_length = sum(p["length"] for p in paths) / len(paths)
    strength = round(max(0.1, min(1.0, 1.0 - (avg_length - 1) * 0.3 + (seed % 11) * 0.01)), 4)

    return {
        "paths": paths,
        "relationship_types": sorted(all_relationship_types),
        "strength": strength,
        "entity_a": entity_a,
        "entity_b": entity_b,
        "graph_id": resolved_graph_id,
        "path_count": path_count,
    }
