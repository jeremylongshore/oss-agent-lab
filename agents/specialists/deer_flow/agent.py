"""
DeerFlow specialist — full-stack research and code generation pipeline.

Wraps bytedance/deer-flow patterns to provide a SuperAgent-style pipeline:
research a topic, generate code from findings, and package everything into a
versioned artifact. Each stage is independently accessible via the tool API.

Usage:
    specialist = DeerFlowSpecialist()
    response = await specialist.execute(request)
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse

from .tools import create_artifact, generate_code, research_topic


class DeerFlowSpecialist(BaseSpecialist):
    """Full-stack research and code generation pipeline inspired by bytedance/deer-flow.

    Executes the SuperAgent pattern in three stages:
    1. Research — gather findings and sources for the requested topic.
    2. Code generation — produce an implementation from the research summary.
    3. Artifact creation — package findings and code into a versioned deliverable.
    """

    name: ClassVar[str] = "deer_flow"
    description: ClassVar[str] = (
        "Full-stack research and code generation: research, code, create pipeline"
    )
    source_repo: ClassVar[str] = "bytedance/deer-flow"

    capabilities: ClassVar[list[str]] = [
        "research",
        "code_generation",
        "creation",
        "summarize",
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
            name="research_topic",
            description=(
                "Research a topic and return structured findings, sources, "
                "a summary, and a confidence score."
            ),
            parameters={
                "topic": "str",
                "depth": "Literal['shallow', 'standard', 'deep'] = 'standard'",
                "sources": "list[str] | None = None",
            },
        ),
        Tool(
            name="generate_code",
            description=(
                "Generate an implementation, tests, and explanation from a "
                "natural-language specification."
            ),
            parameters={
                "specification": "str",
                "language": "str = 'python'",
                "style": "Literal['clean', 'verbose', 'minimal'] = 'clean'",
            },
        ),
        Tool(
            name="create_artifact",
            description=(
                "Package pipeline outputs into a versioned artifact with a "
                "stable ID and creation metadata."
            ),
            parameters={
                "content": "dict[str, Any]",
                "artifact_type": "Literal['report', 'notebook', 'package', 'summary'] = 'report'",
                "format": "Literal['markdown', 'json', 'html'] = 'markdown'",
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Run the full deer-flow pipeline for the given request.

        Stages:
            1. Extract the task description from the request query.
            2. Research the topic via ``research_topic``.
            3. Generate code from the research summary via ``generate_code``.
            4. Package everything into a final artifact via ``create_artifact``.

        Args:
            request: Incoming specialist request with intent, query, and
                optional tool parameters.

        Returns:
            SpecialistResponse with status ``"success"`` and a ``result`` dict
            containing ``research``, ``code``, and ``artifact`` sub-sections,
            plus execution metadata.
        """
        start_ms = time.monotonic() * 1000
        params: dict[str, Any] = dict(request.intent.parameters)

        # Stage 1: extract task from the user query
        task: str = request.query.user_input.strip() or request.intent.action

        # Stage 2: research the topic
        depth: str = str(params.get("depth", "standard"))
        raw_sources = params.get("sources")
        sources: list[str] | None = list(raw_sources) if raw_sources else None
        research_result = research_topic(topic=task, depth=depth, sources=sources)

        # Stage 3: generate code if the intent or params signal it
        needs_code: bool = (
            "code" in request.intent.action.lower()
            or "code_generation" in request.intent.domain.lower()
            or bool(params.get("generate_code", True))
        )
        code_result: dict[str, Any] | None = None
        if needs_code:
            specification: str = str(params.get("specification", research_result["summary"]))
            language: str = str(params.get("language", "python"))
            style: str = str(params.get("style", "clean"))
            code_result = generate_code(
                specification=specification,
                language=language,
                style=style,
            )

        # Stage 4: create the final artifact
        artifact_content: dict[str, Any] = {"research": research_result}
        if code_result is not None:
            artifact_content["code"] = code_result

        artifact_type: str = str(params.get("artifact_type", "report"))
        artifact_format: str = str(params.get("format", "markdown"))
        artifact_result = create_artifact(
            content=artifact_content,
            artifact_type=artifact_type,
            format=artifact_format,
        )

        duration_ms = time.monotonic() * 1000 - start_ms

        result: dict[str, Any] = {
            "task": task,
            "research": research_result,
            "artifact": artifact_result,
        }
        if code_result is not None:
            result["code"] = code_result

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result=result,
            metadata={
                "depth": depth,
                "code_generated": code_result is not None,
                "artifact_id": artifact_result["artifact_id"],
                "confidence": research_result["confidence"],
            },
            duration_ms=round(duration_ms, 2),
        )
