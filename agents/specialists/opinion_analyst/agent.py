"""
OpinionAnalyst specialist — public opinion analysis and sentiment at scale.

Wraps 666ghj/BettaFish to provide sentiment analysis, stance detection, and
bias measurement across arbitrary text inputs.
"""

import time
from typing import Any, ClassVar

from agents.specialists.opinion_analyst.tools import (
    analyze_sentiment,
    detect_stance,
    measure_bias,
)
from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class OpinionAnalystSpecialist(BaseSpecialist):
    """Analyse public opinion, sentiment, stance, and bias in text at scale.

    Wraps the 666ghj/BettaFish repository which provides efficient NLP
    pipelines for opinion mining over large corpora.
    """

    name: ClassVar[str] = "opinion_analyst"
    description: ClassVar[str] = (
        "Public opinion analysis and sentiment at scale — sentiment scoring,"
        " stance detection, and multi-dimensional bias measurement."
    )
    source_repo: ClassVar[str] = "666ghj/BettaFish"

    capabilities: ClassVar[list[str]] = [
        "sentiment",
        "opinion_analysis",
        "stance_detection",
        "bias_measurement",
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
            name="analyze_sentiment",
            description=(
                "Score the overall sentiment of a text as positive, negative, or"
                " neutral with a continuous score in [-1, 1]."
            ),
            parameters={
                "text": {"type": "string", "description": "Text to analyse."},
                "granularity": {
                    "type": "string",
                    "enum": ["document", "sentence", "aspect"],
                    "default": "document",
                    "description": "Analysis granularity.",
                },
            },
        ),
        Tool(
            name="detect_stance",
            description=(
                "Detect whether the author supports, opposes, or is neutral toward"
                " a specific target entity or claim."
            ),
            parameters={
                "text": {"type": "string", "description": "Source text."},
                "target": {
                    "type": "string",
                    "description": "Entity or claim to measure stance against.",
                },
            },
        ),
        Tool(
            name="measure_bias",
            description=(
                "Measure bias across configurable dimensions (political, emotional,"
                " framing, source, confirmation) and return per-dimension scores"
                " plus a list of raised flags."
            ),
            parameters={
                "text": {"type": "string", "description": "Text to evaluate."},
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "nullable": True,
                    "description": (
                        "Bias dimensions to measure. Defaults to all five"
                        " built-in dimensions when omitted."
                    ),
                },
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Analyse opinion and sentiment from the request query.

        Dispatches to one or more tools based on the requested action and
        parameters in the intent, then assembles a structured result.

        Args:
            request: Incoming specialist request containing intent, query,
                and optional tool parameters.

        Returns:
            SpecialistResponse with ``status``, structured ``result`` dict,
            and execution ``metadata``.
        """
        start = time.monotonic()

        try:
            result = await self._dispatch(request)
            status: str = "success"
        except Exception as exc:
            result = {"error": str(exc)}
            status = "error"

        duration_ms = (time.monotonic() - start) * 1000

        return SpecialistResponse(
            specialist_name=self.name,
            status=status,  # type: ignore[arg-type]
            result=result,
            metadata={
                "source_repo": self.source_repo,
                "action": request.intent.action,
                "domain": request.intent.domain,
                "tools_used": request.tools_requested or ["analyze_sentiment"],
            },
            duration_ms=round(duration_ms, 2),
        )

    async def _dispatch(self, request: SpecialistRequest) -> dict[str, Any]:
        """Select and call the appropriate tool(s) based on the request intent.

        Args:
            request: The incoming specialist request.

        Returns:
            Structured result dict combining outputs from invoked tools.
        """
        text: str = request.query.user_input
        params: dict[str, Any] = request.intent.parameters
        action: str = request.intent.action.lower()
        tools_requested: list[str] = request.tools_requested or []

        result: dict[str, Any] = {}

        run_sentiment = (
            "sentiment" in action
            or "analyze_sentiment" in tools_requested
            or not tools_requested
        )
        run_stance = (
            "stance" in action
            or "detect_stance" in tools_requested
        )
        run_bias = (
            "bias" in action
            or "measure_bias" in tools_requested
        )

        if run_sentiment:
            granularity: str = params.get("granularity", "document")
            result["sentiment"] = analyze_sentiment(text, granularity=granularity)

        if run_stance:
            target: str = params.get("target", "")
            result["stance"] = detect_stance(text, target=target)

        if run_bias:
            dimensions: list[str] | None = params.get("dimensions")
            result["bias"] = measure_bias(text, dimensions=dimensions)

        if not result:
            result["sentiment"] = analyze_sentiment(text)

        return result
