"""Integration tests for the first three specialists: autoresearch, swarm_predict, deer_flow."""

from __future__ import annotations

import pytest

from oss_agent_lab.contracts import Intent, Query, SpecialistRequest, SpecialistResponse


def _make_request(
    specialist_name: str,
    user_input: str,
    action: str = "research",
    domain: str = "ai",
    **params: object,
) -> SpecialistRequest:
    return SpecialistRequest(
        intent=Intent(
            action=action,
            domain=domain,
            confidence=0.9,
            parameters=dict(params),
        ),
        query=Query(user_input=user_input),
        specialist_name=specialist_name,
    )


# ---------------------------------------------------------------------------
# Autoresearch
# ---------------------------------------------------------------------------


class TestAutoresearchSpecialist:
    @pytest.mark.asyncio
    async def test_execute_returns_success(self) -> None:
        from agents.specialists.autoresearch.agent import AutoresearchSpecialist

        s = AutoresearchSpecialist()
        req = _make_request("autoresearch", "Research transformers", topic="transformers")
        resp = await s.execute(req)

        assert isinstance(resp, SpecialistResponse)
        assert resp.specialist_name == "autoresearch"
        assert resp.status == "success"
        assert "hypotheses" in resp.result or "hypothesis" in str(resp.result).lower()

    def test_class_attributes(self) -> None:
        from agents.specialists.autoresearch.agent import AutoresearchSpecialist

        s = AutoresearchSpecialist()
        assert s.name == "autoresearch"
        assert s.source_repo == "karpathy/autoresearch"
        assert "research" in s.capabilities
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.autoresearch.tools import (
            analyze_results,
            generate_hypothesis,
            run_experiment,
        )

        hyp = generate_hypothesis("AI safety")
        assert isinstance(hyp, dict)

        exp = run_experiment("AI models are safe")
        assert isinstance(exp, dict)
        assert "experiment_id" in exp or "findings" in exp or "status" in exp

        analysis = analyze_results([{"finding": "test", "strength": 0.8}])
        assert isinstance(analysis, dict)


# ---------------------------------------------------------------------------
# Swarm Predict
# ---------------------------------------------------------------------------


class TestSwarmPredictSpecialist:
    @pytest.mark.asyncio
    async def test_execute_returns_success(self) -> None:
        from agents.specialists.swarm_predict.agent import SwarmPredictSpecialist

        s = SwarmPredictSpecialist()
        req = _make_request(
            "swarm_predict",
            "Predict S&P 500 next week",
            action="predict",
            domain="finance",
            target="S&P 500",
        )
        resp = await s.execute(req)

        assert isinstance(resp, SpecialistResponse)
        assert resp.specialist_name == "swarm_predict"
        assert resp.status == "success"

    def test_class_attributes(self) -> None:
        from agents.specialists.swarm_predict.agent import SwarmPredictSpecialist

        s = SwarmPredictSpecialist()
        assert s.name == "swarm_predict"
        assert s.source_repo == "666ghj/MiroFish"
        assert "predict" in s.capabilities or "consensus" in s.capabilities
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.swarm_predict.tools import (
            aggregate_predictions,
            create_prediction_swarm,
            evaluate_consensus,
        )

        swarm = create_prediction_swarm("test target")
        assert isinstance(swarm, dict)

        preds = [{"value": 42.0, "confidence": 0.8, "model": "m1"}]
        agg = aggregate_predictions(preds)
        assert isinstance(agg, dict)

        result = evaluate_consensus(agg)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Deer Flow
# ---------------------------------------------------------------------------


class TestDeerFlowSpecialist:
    @pytest.mark.asyncio
    async def test_execute_returns_success(self) -> None:
        from agents.specialists.deer_flow.agent import DeerFlowSpecialist

        s = DeerFlowSpecialist()
        req = _make_request(
            "deer_flow",
            "Build a web scraper",
            action="code_generation",
            domain="code",
        )
        resp = await s.execute(req)

        assert isinstance(resp, SpecialistResponse)
        assert resp.specialist_name == "deer_flow"
        assert resp.status == "success"

    def test_class_attributes(self) -> None:
        from agents.specialists.deer_flow.agent import DeerFlowSpecialist

        s = DeerFlowSpecialist()
        assert s.name == "deer_flow"
        assert s.source_repo == "bytedance/deer-flow"
        assert "code_generation" in s.capabilities or "research" in s.capabilities
        assert len(s.tools) >= 3

    def test_tools(self) -> None:
        from agents.specialists.deer_flow.tools import (
            create_artifact,
            generate_code,
            research_topic,
        )

        research = research_topic("web scraping")
        assert isinstance(research, dict)

        code = generate_code("A function that adds two numbers")
        assert isinstance(code, dict)

        artifact = create_artifact({"content": "test report"})
        assert isinstance(artifact, dict)


# ---------------------------------------------------------------------------
# Cross-specialist consistency
# ---------------------------------------------------------------------------


class TestSpecialistConsistency:
    """All specialists must follow the same contract."""

    @pytest.mark.asyncio
    async def test_all_return_specialist_response(self) -> None:
        from agents.specialists.autoresearch.agent import AutoresearchSpecialist
        from agents.specialists.deer_flow.agent import DeerFlowSpecialist
        from agents.specialists.swarm_predict.agent import SwarmPredictSpecialist

        specialists = [
            (AutoresearchSpecialist(), "autoresearch", "Research AI"),
            (SwarmPredictSpecialist(), "swarm_predict", "Predict trends"),
            (DeerFlowSpecialist(), "deer_flow", "Generate code"),
        ]

        for specialist, name, query_text in specialists:
            req = _make_request(name, query_text)
            resp = await specialist.execute(req)
            assert isinstance(resp, SpecialistResponse), f"{name} didn't return SpecialistResponse"
            assert resp.specialist_name == name, f"{name} wrong specialist_name"
            assert resp.status == "success", f"{name} status != success"

    def test_all_have_skill_metadata(self) -> None:
        from agents.specialists.autoresearch.agent import AutoresearchSpecialist
        from agents.specialists.deer_flow.agent import DeerFlowSpecialist
        from agents.specialists.swarm_predict.agent import SwarmPredictSpecialist

        for cls in [AutoresearchSpecialist, SwarmPredictSpecialist, DeerFlowSpecialist]:
            s = cls()
            meta = s.get_skill_metadata()
            assert "name" in meta
            assert "source_repo" in meta
            assert "capabilities" in meta
            assert len(meta["capabilities"]) >= 1
            assert len(meta["tools"]) >= 1
