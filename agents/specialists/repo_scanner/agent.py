"""
RepoScanner specialist — meta-specialist for auto-discovering and scaffolding
new specialists from trending GitHub repos.

This specialist IS the OSS Agent Lab repository itself acting as a reflective
meta-agent. It consumes the Capability Scoring Engine's output to decide
whether a candidate repo is worth wrapping, then auto-scaffolds the specialist
directory when the score crosses the AUTO_SCAFFOLD threshold (>= 80).

Typical pipeline:
    1. Extract the target repo slug from the request parameters or user input.
    2. Run scan_repo() to analyse structural signals.
    3. Run evaluate_score() to compute a composite capability score.
    4. If score >= 80, run scaffold_specialist() to materialise the skeleton.
    5. Return a SpecialistResponse containing all stage outputs.
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from agents.specialists.repo_scanner.tools import (
    evaluate_score,
    scaffold_specialist,
    scan_repo,
)
from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse

_AUTO_SCAFFOLD_THRESHOLD = 80.0


class RepoScannerSpecialist(BaseSpecialist):
    """Meta-specialist: auto-discovers and scaffolds specialists from GitHub repos.

    Each call to :meth:`execute` runs the full three-stage discovery pipeline
    for a single candidate repo: structural analysis, capability scoring, and
    (when the score qualifies) directory scaffolding. The specialist is
    stateless — every request is fully independent.

    Attributes:
        name: Specialist identifier used for routing.
        description: Human-readable capability summary.
        source_repo: This specialist IS this repo — it is self-referential.
        capabilities: List of string capability tags.
        output_formats: All five supported output modes.
        tools: Tool descriptors made available to the agent runtime.
    """

    name: ClassVar[str] = "repo_scanner"
    description: ClassVar[str] = (
        "Meta-specialist that auto-discovers and scaffolds new specialists from trending "
        "GitHub repos using the Capability Scoring Engine"
    )
    source_repo: ClassVar[str] = "jeremylongshore/oss-agent-lab"
    capabilities: ClassVar[list[str]] = [
        "auto_scaffold",
        "repo_analysis",
        "specialist_generation",
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
            name="scan_repo",
            description=(
                "Analyse a GitHub repo for specialist-wrapping potential. Returns structural "
                "signals (has_python, has_tests, has_readme), a name suggestion, detected "
                "capabilities, and a preliminary recommendation."
            ),
            parameters={
                "repo": {
                    "type": "string",
                    "description": "GitHub repo slug in 'owner/name' format (e.g. 'openai/swarm')",
                },
            },
        ),
        Tool(
            name="scaffold_specialist",
            description=(
                "Generate a new specialist directory by copying the _template skeleton. "
                "Creates __init__.py, agent.py, tools.py, and SKILL.md under "
                "agents/specialists/<name>/. Returns status, path, and file list."
            ),
            parameters={
                "repo": {
                    "type": "string",
                    "description": "Source GitHub repo slug (recorded for provenance)",
                },
                "name": {
                    "type": "string",
                    "description": "Snake-case specialist name for the new directory",
                },
            },
        ),
        Tool(
            name="evaluate_score",
            description=(
                "Compute a composite capability score (0-100) for a GitHub repo using "
                "simulated Capability Scoring Engine signals. Returns estimated_score, "
                "action (auto_scaffold/evaluate/watch/skip), and signal breakdown."
            ),
            parameters={
                "repo": {
                    "type": "string",
                    "description": "GitHub repo slug in 'owner/name' format",
                },
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Run the full repo-scanner pipeline for a candidate GitHub repo.

        Extracts the target repo from ``request.intent.parameters["repo"]``
        when present; otherwise falls back to ``request.query.user_input``.
        An optional ``name`` override in the intent parameters controls the
        scaffolded directory name (defaults to the name suggested by scan_repo).

        Args:
            request: The routed specialist request carrying an :class:`Intent`
                and a :class:`Query`.

        Returns:
            A :class:`SpecialistResponse` with:
                - ``status``: ``"success"`` on a clean run.
                - ``result``: Dict containing ``repo``, ``scan``, ``score``,
                  and (conditionally) ``scaffold``.
                - ``metadata``: Pipeline configuration details.
                - ``duration_ms``: Wall-clock time for the full pipeline.
        """
        t_start = time.perf_counter()

        params: dict[str, Any] = request.intent.parameters or {}
        repo: str = str(params.get("repo") or request.query.user_input).strip()

        # Stage 1 — structural analysis.
        scan = scan_repo(repo)

        # Stage 2 — capability scoring.
        score = evaluate_score(repo)

        # Stage 3 — conditional scaffolding.
        scaffold: dict[str, Any] | None = None
        if score["estimated_score"] >= _AUTO_SCAFFOLD_THRESHOLD:
            specialist_name: str = str(
                params.get("name") or scan["name_suggestion"]
            )
            scaffold = scaffold_specialist(repo=repo, name=specialist_name)

        duration_ms = (time.perf_counter() - t_start) * 1000.0

        result: dict[str, Any] = {
            "repo": repo,
            "scan": scan,
            "score": score,
        }
        if scaffold is not None:
            result["scaffold"] = scaffold

        metadata: dict[str, Any] = {
            "source_repo": self.source_repo,
            "score_threshold": _AUTO_SCAFFOLD_THRESHOLD,
            "scaffolded": scaffold is not None,
            "action": score["action"],
        }

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result=result,
            metadata=metadata,
            duration_ms=round(duration_ms, 3),
        )
