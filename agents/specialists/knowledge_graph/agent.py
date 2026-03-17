"""
KnowledgeGraph specialist — code knowledge graphs and Graph RAG.

Wraps patterns from abhigyanpatwari/GitNexus (code entity extraction and
graph construction) and topoteretes/cognee (Graph RAG retrieval).  Given a
source artifact and a natural-language query, the specialist builds or
queries a structured knowledge graph and surfaces entity/relationship results
ready for downstream reasoning.

Typical pipeline:
    1. Extract graph parameters (source, graph_type, query) from the request.
    2. Build a knowledge graph from the source artifact.
    3. Query the graph using the natural-language query.
    4. Optionally find direct relationships between key entities.
    5. Return entities, relevance-ranked results, and relationship paths.
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from agents.specialists.knowledge_graph.tools import (
    build_graph,
    find_relationships,
    query_graph,
)
from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class KnowledgeGraphSpecialist(BaseSpecialist):
    """Code knowledge graphs and Graph RAG via GitNexus and cognee.

    Builds entity/relationship graphs from source repositories or code
    snippets and answers natural-language queries through graph traversal,
    returning ranked entity results and relationship paths.

    Attributes:
        name: Specialist identifier used for routing.
        description: Human-readable capability summary.
        source_repo: Upstream GitHub repository this specialist wraps.
        capabilities: List of string capability tags.
        output_formats: Supported output modes.
        tools: Tool descriptors made available to the agent runtime.
    """

    name: ClassVar[str] = "knowledge_graph"
    description: ClassVar[str] = (
        "Code knowledge graphs and Graph RAG: entity extraction, relationship mapping, "
        "and natural-language graph queries over source repositories"
    )
    source_repo: ClassVar[str] = "abhigyanpatwari/GitNexus"
    capabilities: ClassVar[list[str]] = [
        "knowledge_graph",
        "code_analysis",
        "entity_linking",
        "graph_rag",
    ]

    output_formats: ClassVar[list[OutputFormat]] = [
        OutputFormat.PYTHON_API,
        OutputFormat.CLI,
        OutputFormat.MCP_SERVER,
        OutputFormat.AGENT_SKILL,
        OutputFormat.REST_API,
    ]

    tools: ClassVar[list[Tool]] = [
        Tool(
            name="build_graph",
            description=(
                "Build a knowledge graph from a source artifact (repository URL, file path, "
                "or raw code). Returns graph_id, node_count, edge_count, and entity_types."
            ),
            parameters={
                "source": {
                    "type": "string",
                    "description": "Repository URL, local file path, or raw code/text to ingest",
                },
                "graph_type": {
                    "type": "string",
                    "description": "Entity extraction strategy: code | document | mixed",
                    "default": "code",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum traversal depth for cross-file relationships",
                    "default": 3,
                },
            },
        ),
        Tool(
            name="query_graph",
            description=(
                "Query a knowledge graph using natural language. Returns ranked entity "
                "results with relevance scores and the relationship paths connecting them."
            ),
            parameters={
                "query": {
                    "type": "string",
                    "description": "Natural-language question or keyword expression",
                },
                "graph_id": {
                    "type": "string",
                    "description": "UUID of the graph to query; defaults to latest",
                    "default": None,
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of entity results to return",
                    "default": 10,
                },
            },
        ),
        Tool(
            name="find_relationships",
            description=(
                "Find all relationship paths between two named entities in the graph. "
                "Returns paths, relationship_types, and a coupling strength score."
            ),
            parameters={
                "entity_a": {
                    "type": "string",
                    "description": "Name or entity ID of the source entity",
                },
                "entity_b": {
                    "type": "string",
                    "description": "Name or entity ID of the target entity",
                },
                "graph_id": {
                    "type": "string",
                    "description": "UUID of the graph to search; defaults to latest",
                    "default": None,
                },
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Build and query a knowledge graph for the incoming request.

        Extracts a source artifact and natural-language query from the
        request, constructs a knowledge graph, runs a graph RAG query, and
        optionally resolves direct entity relationships when ``entity_a`` and
        ``entity_b`` are provided in parameters.

        Args:
            request: The routed specialist request carrying an :class:`Intent`
                and a :class:`Query`.  Relevant ``intent.parameters`` keys:

                - ``source`` (str): Source artifact to ingest.  Falls back to
                  ``query.user_input`` when absent.
                - ``graph_type`` (str): ``"code"`` | ``"document"`` | ``"mixed"``.
                  Defaults to ``"code"``.
                - ``max_depth`` (int): Traversal depth limit.  Defaults to 3.
                - ``max_results`` (int): Result cap for graph queries.  Defaults to 10.
                - ``entity_a`` / ``entity_b`` (str): When both are supplied, an
                  additional :func:`find_relationships` call is made and included
                  in the response.

        Returns:
            A :class:`SpecialistResponse` with:
                - ``status``: ``"success"`` on a clean run.
                - ``result``: Dict containing ``graph``, ``query_results``, and
                  optionally ``relationships``.
                - ``metadata``: Graph configuration and timing details.
                - ``duration_ms``: Wall-clock time for the full pipeline in ms.
        """
        t_start = time.perf_counter()

        params: dict[str, Any] = request.intent.parameters or {}
        source: str = params.get("source") or request.query.user_input
        graph_type: str = str(params.get("graph_type", "code"))
        max_depth: int = int(params.get("max_depth", 3))
        max_results: int = int(params.get("max_results", 10))
        nl_query: str = params.get("query") or request.query.user_input
        entity_a: str | None = params.get("entity_a")
        entity_b: str | None = params.get("entity_b")

        # Step 1 — build the knowledge graph.
        graph = build_graph(source=source, graph_type=graph_type, max_depth=max_depth)
        graph_id: str = graph["graph_id"]

        # Step 2 — run a Graph RAG query against the new graph.
        query_results = query_graph(query=nl_query, graph_id=graph_id, max_results=max_results)

        # Step 3 — optionally find direct entity relationships.
        relationships: dict[str, Any] | None = None
        if entity_a and entity_b:
            relationships = find_relationships(
                entity_a=entity_a,
                entity_b=entity_b,
                graph_id=graph_id,
            )

        duration_ms = (time.perf_counter() - t_start) * 1000.0

        result: dict[str, Any] = {
            "graph": {
                "graph_id": graph_id,
                "node_count": graph["node_count"],
                "edge_count": graph["edge_count"],
                "entity_types": graph["entity_types"],
                "graph_type": graph["graph_type"],
            },
            "query_results": {
                "results": query_results["results"],
                "relevance_scores": query_results["relevance_scores"],
                "paths": query_results["paths"],
                "total_found": query_results["total_found"],
            },
        }
        if relationships is not None:
            result["relationships"] = {
                "paths": relationships["paths"],
                "relationship_types": relationships["relationship_types"],
                "strength": relationships["strength"],
                "path_count": relationships["path_count"],
            }

        metadata: dict[str, Any] = {
            "source_repo": self.source_repo,
            "graph_id": graph_id,
            "graph_type": graph_type,
            "max_depth": max_depth,
            "max_results": max_results,
            "entity_count": graph["node_count"],
            "relationship_search": relationships is not None,
        }

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result=result,
            metadata=metadata,
            duration_ms=round(duration_ms, 3),
        )
