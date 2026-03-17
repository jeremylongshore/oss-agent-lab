"""
Tools for the SwarmPredict specialist.

Implements swarm intelligence prediction patterns inspired by 666ghj/MiroFish:
multi-model voting, prediction aggregation, and consensus evaluation.

Each function is a pure transformation — no I/O side effects. Real swarm
backends (remote model endpoints, databases) would be injected via the context
parameter rather than hard-coded here.
"""

from __future__ import annotations

import uuid
from typing import Any


def create_prediction_swarm(
    target: str,
    num_models: int = 5,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a swarm of prediction agents for the given target.

    Initialises a set of virtual model agents, each seeded with the target
    and any caller-supplied context. In production the model list would be
    resolved against a registry; here each entry carries enough metadata for
    downstream aggregation.

    Args:
        target: The prediction target — a question, ticker symbol, event name,
            or any string that scopes what is being predicted.
        num_models: Number of independent model agents in the swarm.
            Must be >= 1. Defaults to 5.
        context: Optional supplementary context passed through to every agent
            (e.g. historical data, domain hints, time horizon).

    Returns:
        A dict with:
            - ``swarm_id``: Unique identifier for this swarm instance.
            - ``models``: List of model-descriptor dicts, each with ``model_id``,
              ``model_type``, ``weight``, and ``status``.
            - ``target``: Echo of the requested prediction target.
            - ``num_models``: Actual swarm size created.
            - ``context``: The context dict that was supplied (or empty dict).

    Raises:
        ValueError: If num_models < 1.
    """
    if num_models < 1:
        raise ValueError(f"num_models must be >= 1, got {num_models}")

    ctx = context or {}
    model_types = ["gradient_boost", "neural_net", "bayesian", "random_forest", "svm"]

    models = [
        {
            "model_id": f"model_{i}",
            "model_type": model_types[i % len(model_types)],
            "weight": 1.0 / num_models,
            "status": "ready",
        }
        for i in range(num_models)
    ]

    return {
        "swarm_id": str(uuid.uuid4()),
        "models": models,
        "target": target,
        "num_models": num_models,
        "context": ctx,
    }


def aggregate_predictions(
    predictions: list[dict[str, Any]],
    method: str = "weighted_vote",
) -> dict[str, Any]:
    """Aggregate predictions from multiple swarm models into a single consensus.

    Supported aggregation methods:

    - ``weighted_vote``: Weighted average of numeric ``value`` fields, using
      each prediction's ``confidence`` as its weight.
    - ``majority_vote``: The most frequently predicted discrete class wins;
      numeric values are averaged unweighted as a fallback.
    - ``mean``: Simple unweighted average of all numeric ``value`` fields.

    Args:
        predictions: List of prediction dicts.  Each entry should contain at
            minimum a ``value`` (numeric or string) and optionally ``confidence``
            (float 0-1) and ``model_id`` (str).
        method: Aggregation strategy.  One of ``"weighted_vote"``,
            ``"majority_vote"``, or ``"mean"``.  Defaults to ``"weighted_vote"``.

    Returns:
        A dict with:
            - ``consensus_value``: The aggregated prediction.
            - ``agreement_ratio``: Float 0-1 reflecting how closely models agree.
              For numeric predictions this is 1 - (std / mean); for class
              predictions it is the share of votes captured by the winner.
            - ``individual_predictions``: Echo of the input list, each entry
              augmented with a ``normalised_weight`` field.
            - ``method``: The aggregation method that was used.
            - ``num_predictions``: Number of predictions that were aggregated.

    Raises:
        ValueError: If ``predictions`` is empty or ``method`` is unknown.
    """
    if not predictions:
        raise ValueError("predictions list must not be empty")

    valid_methods = {"weighted_vote", "majority_vote", "mean"}
    if method not in valid_methods:
        raise ValueError(f"Unknown method {method!r}. Choose from {sorted(valid_methods)}")

    # Separate numeric from categorical predictions.
    numeric_values: list[float] = []
    confidences: list[float] = []
    for pred in predictions:
        val = pred.get("value")
        conf = float(pred.get("confidence", 1.0))
        if isinstance(val, (int, float)):
            numeric_values.append(float(val))
            confidences.append(conf)

    if numeric_values:
        consensus_value, agreement_ratio = _aggregate_numeric(numeric_values, confidences, method)
    else:
        # Categorical / string voting.
        raw_values = [str(p.get("value", "")) for p in predictions]
        consensus_value, agreement_ratio = _aggregate_categorical(raw_values)

    total_conf = sum(confidences) if confidences else len(predictions)
    augmented = [
        {
            **pred,
            "normalised_weight": (
                float(pred.get("confidence", 1.0)) / total_conf if total_conf else 0.0
            ),
        }
        for pred in predictions
    ]

    return {
        "consensus_value": consensus_value,
        "agreement_ratio": round(agreement_ratio, 4),
        "individual_predictions": augmented,
        "method": method,
        "num_predictions": len(predictions),
    }


def evaluate_consensus(
    aggregated: dict[str, Any],
    threshold: float = 0.7,
) -> dict[str, Any]:
    """Evaluate the strength of a swarm consensus and produce a recommendation.

    Args:
        aggregated: The dict returned by :func:`aggregate_predictions`.
        threshold: Minimum ``agreement_ratio`` required to consider consensus
            reached.  Must be in [0, 1].  Defaults to 0.7.

    Returns:
        A dict with:
            - ``consensus_reached``: ``True`` if ``agreement_ratio`` meets the
              threshold.
            - ``confidence``: A float 0-1 blending agreement_ratio with the
              mean model confidence from the individual predictions.
            - ``recommendation``: A human-readable action string.  One of
              ``"high_confidence_proceed"``, ``"moderate_confidence_review"``,
              ``"low_confidence_abstain"``.
            - ``agreement_ratio``: Echo from the aggregated input.
            - ``threshold``: Echo of the threshold that was applied.

    Raises:
        ValueError: If ``threshold`` is outside [0, 1].
        KeyError: If ``aggregated`` is missing required keys.
    """
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"threshold must be in [0, 1], got {threshold}")

    agreement_ratio: float = aggregated["agreement_ratio"]
    individual: list[dict[str, Any]] = aggregated.get("individual_predictions", [])

    # Mean confidence across all individual predictions.
    if individual:
        mean_conf = sum(float(p.get("confidence", 1.0)) for p in individual) / len(individual)
    else:
        mean_conf = 1.0

    # Blend agreement and confidence equally.
    blended_confidence = round((agreement_ratio + mean_conf) / 2.0, 4)
    consensus_reached = agreement_ratio >= threshold

    if blended_confidence >= 0.75:
        recommendation = "high_confidence_proceed"
    elif blended_confidence >= 0.5:
        recommendation = "moderate_confidence_review"
    else:
        recommendation = "low_confidence_abstain"

    return {
        "consensus_reached": consensus_reached,
        "confidence": blended_confidence,
        "recommendation": recommendation,
        "agreement_ratio": agreement_ratio,
        "threshold": threshold,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _aggregate_numeric(
    values: list[float],
    confidences: list[float],
    method: str,
) -> tuple[float, float]:
    """Return (consensus_value, agreement_ratio) for a numeric prediction set."""
    n = len(values)
    total_conf = sum(confidences) or float(n)

    if method == "weighted_vote":
        consensus = sum(v * c for v, c in zip(values, confidences, strict=True)) / total_conf
    else:
        # mean or majority_vote fallback for numeric data
        consensus = sum(values) / n

    mean = sum(values) / n
    if mean == 0.0:
        agreement_ratio = 1.0 if all(v == 0.0 for v in values) else 0.0
    else:
        variance = sum((v - mean) ** 2 for v in values) / n
        std = variance**0.5
        # Coefficient of variation, inverted and clamped.
        agreement_ratio = max(0.0, min(1.0, 1.0 - (std / abs(mean))))

    return round(consensus, 6), agreement_ratio


def _aggregate_categorical(values: list[str]) -> tuple[str, float]:
    """Return (winner, agreement_ratio) for a categorical prediction set."""
    from collections import Counter

    counts = Counter(values)
    winner, top_count = counts.most_common(1)[0]
    agreement_ratio = top_count / len(values)
    return winner, agreement_ratio
