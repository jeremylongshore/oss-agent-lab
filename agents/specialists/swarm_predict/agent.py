"""
SwarmPredict specialist — ensemble predictions via swarm intelligence.

Wraps patterns from 666ghj/MiroFish: multiple independent model agents vote
on a prediction target and a consensus is reached through weighted aggregation
and agreement scoring.

Typical pipeline:
    1. Extract the prediction target from the incoming request.
    2. Spin up a swarm of N virtual model agents.
    3. Each agent returns an independent prediction with a confidence score.
    4. Aggregate predictions using weighted voting.
    5. Evaluate the consensus strength against a configurable threshold.
    6. Surface the consensus value, confidence, and recommendation.
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from agents.specialists.swarm_predict.tools import (
    aggregate_predictions,
    create_prediction_swarm,
    evaluate_consensus,
)
from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class SwarmPredictSpecialist(BaseSpecialist):
    """Ensemble prediction via swarm intelligence: multi-model voting and consensus.

    Each call to :meth:`execute` orchestrates the full swarm pipeline:
    swarm creation, per-model prediction, aggregation, and consensus scoring.
    The specialist is stateless — every request spawns a fresh swarm.

    Attributes:
        name: Specialist identifier used for routing.
        description: Human-readable capability summary.
        source_repo: Upstream GitHub repository this specialist wraps.
        capabilities: List of string capability tags.
        output_formats: Supported output modes.
        tools: Tool descriptors made available to the agent runtime.
    """

    name: ClassVar[str] = "swarm_predict"
    description: ClassVar[str] = (
        "Ensemble prediction via swarm intelligence: multi-model voting and consensus"
    )
    source_repo: ClassVar[str] = "666ghj/MiroFish"
    capabilities: ClassVar[list[str]] = [
        "predict",
        "ensemble",
        "swarm_intelligence",
        "consensus",
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
            name="create_prediction_swarm",
            description=(
                "Initialise a swarm of independent prediction model agents for a given "
                "target. Returns a swarm_id, list of model descriptors, and the target."
            ),
            parameters={
                "target": {"type": "string", "description": "The prediction target"},
                "num_models": {
                    "type": "integer",
                    "description": "Number of swarm agents",
                    "default": 5,
                },
                "context": {
                    "type": "object",
                    "description": "Optional supplementary context",
                    "default": None,
                },
            },
        ),
        Tool(
            name="aggregate_predictions",
            description=(
                "Aggregate predictions from multiple swarm model agents into a single "
                "consensus value using weighted voting or majority vote."
            ),
            parameters={
                "predictions": {
                    "type": "array",
                    "description": "List of prediction dicts from individual agents",
                },
                "method": {
                    "type": "string",
                    "description": "Aggregation method: weighted_vote | majority_vote | mean",
                    "default": "weighted_vote",
                },
            },
        ),
        Tool(
            name="evaluate_consensus",
            description=(
                "Evaluate the strength of an aggregated consensus and surface a "
                "human-readable recommendation based on the agreement ratio."
            ),
            parameters={
                "aggregated": {
                    "type": "object",
                    "description": "Output from aggregate_predictions",
                },
                "threshold": {
                    "type": "number",
                    "description": "Minimum agreement ratio to consider consensus reached",
                    "default": 0.7,
                },
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Run the full swarm prediction pipeline for the incoming request.

        Extracts a prediction target from the request, creates a swarm,
        simulates per-agent predictions, aggregates them, and evaluates the
        resulting consensus.

        Args:
            request: The routed specialist request, carrying an :class:`Intent`
                and a :class:`Query`.  The prediction target is taken from
                ``request.intent.parameters["target"]`` when present; otherwise
                ``request.query.user_input`` is used directly.  Additional
                swarm parameters (``num_models``, ``method``, ``threshold``)
                may also be passed via ``request.intent.parameters``.

        Returns:
            A :class:`SpecialistResponse` with:
                - ``status``: ``"success"`` on a clean run.
                - ``result``: Dict containing ``target``, ``predictions``,
                  ``consensus``, ``confidence``, ``recommendation``, and
                  ``swarm_id``.
                - ``metadata``: Swarm configuration and timing details.
                - ``duration_ms``: Wall-clock time for the full pipeline.
        """
        t_start = time.perf_counter()

        params: dict[str, Any] = request.intent.parameters or {}
        target: str = params.get("target") or request.query.user_input
        num_models: int = int(params.get("num_models", 5))
        method: str = str(params.get("method", "weighted_vote"))
        threshold: float = float(params.get("threshold", 0.7))
        context: dict[str, Any] | None = request.query.context

        # Step 1 — create the swarm.
        swarm = create_prediction_swarm(target=target, num_models=num_models, context=context)

        # Step 2 — collect a simulated prediction from each model agent.
        raw_predictions = _simulate_model_predictions(swarm["models"], target)

        # Step 3 — aggregate.
        aggregated = aggregate_predictions(predictions=raw_predictions, method=method)

        # Step 4 — evaluate consensus.
        evaluation = evaluate_consensus(aggregated=aggregated, threshold=threshold)

        duration_ms = (time.perf_counter() - t_start) * 1000.0

        result: dict[str, Any] = {
            "target": target,
            "predictions": aggregated["individual_predictions"],
            "consensus": aggregated["consensus_value"],
            "confidence": evaluation["confidence"],
            "recommendation": evaluation["recommendation"],
            "swarm_id": swarm["swarm_id"],
        }

        metadata: dict[str, Any] = {
            "swarm_id": swarm["swarm_id"],
            "num_models": num_models,
            "aggregation_method": method,
            "consensus_threshold": threshold,
            "consensus_reached": evaluation["consensus_reached"],
            "agreement_ratio": evaluation["agreement_ratio"],
        }

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result=result,
            metadata=metadata,
            duration_ms=round(duration_ms, 3),
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _simulate_model_predictions(
    models: list[dict[str, Any]],
    target: str,
) -> list[dict[str, Any]]:
    """Produce a synthetic prediction from each model in the swarm.

    In a production deployment this function would dispatch the target to
    real model endpoints (LLM, sklearn, etc.) and await their responses.
    Here we generate deterministic-but-varied outputs from each model so that
    the aggregation and consensus logic is exercised end-to-end.

    Args:
        models: List of model descriptor dicts from :func:`create_prediction_swarm`.
        target: The original prediction target string.

    Returns:
        List of prediction dicts, one per model, each with ``model_id``,
        ``model_type``, ``value``, and ``confidence``.
    """
    # Derive a stable seed from the target string so results are reproducible
    # for the same target while still varying across targets.
    seed = sum(ord(c) for c in target)

    predictions: list[dict[str, Any]] = []
    for i, model in enumerate(models):
        # Spread values around an arbitrary baseline to simulate disagreement.
        offset = ((seed + i * 7) % 21) - 10  # range [-10, +10]
        value = round(50.0 + offset * 0.5, 2)
        confidence = round(0.55 + (((seed + i * 13) % 40) / 100.0), 4)  # 0.55 - 0.95
        predictions.append(
            {
                "model_id": model["model_id"],
                "model_type": model["model_type"],
                "value": value,
                "confidence": confidence,
            }
        )

    return predictions
