import uuid
from typing import Any


def generate_hypothesis(topic: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    extra = context or {}
    domain = extra.get("domain", "general")
    return {
        "topic": topic,
        "domain": domain,
        "hypotheses": [
            {
                "id": "h1",
                "text": (
                    f"{topic} exhibits a measurable causal relationship with its primary variables."
                ),
                "confidence": 0.75,
                "rationale": "Based on established patterns in the domain literature.",
                "testable": True,
            },
            {
                "id": "h2",
                "text": (
                    f"Interventions targeting {topic} produce reproducible, "
                    "statistically significant effects."
                ),
                "confidence": 0.60,
                "rationale": "Inferred from analogous studies in related domains.",
                "testable": True,
            },
            {
                "id": "h3",
                "text": (
                    f"The effect of {topic} is moderated by contextual factors "
                    "not yet fully characterised."
                ),
                "confidence": 0.50,
                "rationale": "Reflects uncertainty and known knowledge gaps.",
                "testable": False,
            },
        ],
        "recommended": "h1",
    }


def run_experiment(hypothesis: str, method: str = "literature_review") -> dict[str, Any]:
    experiment_id = str(uuid.uuid4())[:8]
    findings_map: dict[str, list[dict[str, Any]]] = {
        "literature_review": [
            {"source": "corpus_scan", "result": "supporting", "strength": 0.70},
            {"source": "meta_analysis", "result": "mixed", "strength": 0.45},
        ],
        "simulation": [
            {"source": "monte_carlo_run", "result": "supporting", "strength": 0.80},
            {"source": "sensitivity_analysis", "result": "supporting", "strength": 0.65},
        ],
        "ablation": [
            {"source": "component_removal", "result": "refuting", "strength": 0.55},
            {"source": "feature_importance", "result": "supporting", "strength": 0.72},
        ],
    }
    findings = findings_map.get(method, findings_map["literature_review"])
    return {
        "experiment_id": experiment_id,
        "hypothesis": hypothesis,
        "method": method,
        "status": "completed",
        "findings": findings,
    }


def analyze_results(findings: list[dict[str, Any]]) -> dict[str, Any]:
    if not findings:
        return {
            "summary": "No findings provided.",
            "key_insights": [],
            "confidence_score": 0.0,
            "next_steps": ["Collect experimental data before analysis."],
        }

    supporting = [f for f in findings if f.get("result") == "supporting"]
    refuting = [f for f in findings if f.get("result") == "refuting"]
    strengths = [f.get("strength", 0.0) for f in findings if isinstance(f.get("strength"), float)]
    confidence_score = round(sum(strengths) / len(strengths), 3) if strengths else 0.0

    summary_parts = [
        f"{len(supporting)} supporting, {len(refuting)} refuting out of {len(findings)} total."
    ]
    if confidence_score >= 0.70:
        summary_parts.append("Evidence leans strongly supportive.")
    elif confidence_score >= 0.50:
        summary_parts.append("Evidence is mixed; further investigation warranted.")
    else:
        summary_parts.append("Evidence is weak; hypothesis may need revision.")

    key_insights = []
    if supporting:
        sources = ", ".join(f.get("source", "?") for f in supporting)
        key_insights.append(f"Primary support from: {sources}.")
    if refuting:
        sources = ", ".join(f.get("source", "?") for f in refuting)
        key_insights.append(f"Contradicted by: {sources}.")

    next_steps = []
    if confidence_score < 0.60:
        next_steps.append("Revise or narrow the hypothesis and re-run experiments.")
    if refuting:
        next_steps.append("Investigate refuting sources for confounding variables.")
    next_steps.append("Iterate with additional experimental methods to increase confidence.")

    return {
        "summary": " ".join(summary_parts),
        "key_insights": key_insights,
        "confidence_score": confidence_score,
        "next_steps": next_steps,
    }
