from typing import Any, ClassVar

from agents.specialists.autoresearch.tools import (
    analyze_results,
    generate_hypothesis,
    run_experiment,
)
from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class AutoresearchSpecialist(BaseSpecialist):
    """Self-improving research loops: hypothesis generation, experiment design, result analysis."""

    name: ClassVar[str] = "autoresearch"
    description: ClassVar[str] = (
        "Self-improving research loops: hypothesis generation, experiment design, result analysis"
    )
    source_repo: ClassVar[str] = "karpathy/autoresearch"
    capabilities: ClassVar[list[str]] = [
        "research",
        "hypothesis_generation",
        "experiment_design",
        "result_analysis",
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
            name="run_experiment",
            description="Simulates running an experiment for a given hypothesis.",
            parameters={"hypothesis": "str", "method": "str"},
        ),
        Tool(
            name="analyze_results",
            description="Analyzes experiment findings and returns insights and confidence score.",
            parameters={"findings": "list[dict]"},
        ),
        Tool(
            name="generate_hypothesis",
            description="Generates structured hypotheses about a topic.",
            parameters={"topic": "str", "context": "dict | None"},
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        params: dict[str, Any] = request.intent.parameters or {}
        topic: str = params.get("topic") or request.query.user_input
        method: str = params.get("method", "literature_review")
        context: dict[str, Any] | None = params.get("context") or request.query.context

        hypothesis_result = generate_hypothesis(topic, context)

        primary_hypothesis = hypothesis_result["hypotheses"][0]["text"]
        experiment_result = run_experiment(primary_hypothesis, method)

        analysis = analyze_results(experiment_result["findings"])

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result={
                "topic": topic,
                "hypotheses": hypothesis_result["hypotheses"],
                "recommended_hypothesis": hypothesis_result["recommended"],
                "experiment": {
                    "id": experiment_result["experiment_id"],
                    "method": experiment_result["method"],
                    "status": experiment_result["status"],
                },
                "analysis": analysis,
            },
            metadata={
                "source_repo": self.source_repo,
                "method": method,
                "hypothesis_count": len(hypothesis_result["hypotheses"]),
            },
        )
