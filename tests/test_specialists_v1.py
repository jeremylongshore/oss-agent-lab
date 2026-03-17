"""Integration tests for the first three specialists: autoresearch, swarm_predict, deer_flow."""

from __future__ import annotations

import pytest
from helpers import make_request

from oss_agent_lab.contracts import SpecialistResponse

# ---------------------------------------------------------------------------
# Autoresearch
# ---------------------------------------------------------------------------


class TestAutoresearchSpecialist:
    @pytest.mark.asyncio
    async def test_execute_returns_success(self) -> None:
        from agents.specialists.autoresearch.agent import AutoresearchSpecialist

        s = AutoresearchSpecialist()
        req = make_request("autoresearch", "Research transformers", topic="transformers")
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
        assert any(t.name == "generate_hypothesis" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.autoresearch.tools import (
            analyze_results,
            generate_hypothesis,
            run_experiment,
        )

        hyp = generate_hypothesis("AI safety")
        assert "hypotheses" in hyp
        assert "topic" in hyp

        exp = run_experiment("AI models are safe")
        assert "experiment_id" in exp
        assert "findings" in exp

        analysis = analyze_results([{"finding": "test", "strength": 0.8}])
        assert "summary" in analysis
        assert "confidence_score" in analysis


# ---------------------------------------------------------------------------
# Swarm Predict
# ---------------------------------------------------------------------------


class TestSwarmPredictSpecialist:
    @pytest.mark.asyncio
    async def test_execute_returns_success(self) -> None:
        from agents.specialists.swarm_predict.agent import SwarmPredictSpecialist

        s = SwarmPredictSpecialist()
        req = make_request(
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
        assert any(t.name == "create_prediction_swarm" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.swarm_predict.tools import (
            aggregate_predictions,
            create_prediction_swarm,
            evaluate_consensus,
        )

        swarm = create_prediction_swarm("test target")
        assert "swarm_id" in swarm
        assert "models" in swarm

        preds = [{"value": 42.0, "confidence": 0.8, "model": "m1"}]
        agg = aggregate_predictions(preds)
        assert "consensus_value" in agg
        assert "agreement_ratio" in agg

        result = evaluate_consensus(agg)
        assert "consensus_reached" in result
        assert "confidence" in result


# ---------------------------------------------------------------------------
# Deer Flow
# ---------------------------------------------------------------------------


class TestDeerFlowSpecialist:
    @pytest.mark.asyncio
    async def test_execute_returns_success(self) -> None:
        from agents.specialists.deer_flow.agent import DeerFlowSpecialist

        s = DeerFlowSpecialist()
        req = make_request(
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
        assert any(t.name == "research_topic" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.deer_flow.tools import (
            create_artifact,
            generate_code,
            research_topic,
        )

        research = research_topic("web scraping")
        assert "findings" in research
        assert "summary" in research

        code = generate_code("A function that adds two numbers")
        assert "code" in code
        assert "language" in code

        artifact = create_artifact({"content": "test report"})
        assert "artifact_id" in artifact
        assert "format" in artifact


# ---------------------------------------------------------------------------
# Cross-specialist consistency
# ---------------------------------------------------------------------------


_V1_SPECIALISTS = [
    (
        "agents.specialists.autoresearch.agent",
        "AutoresearchSpecialist",
        "autoresearch",
        "Research AI",
    ),
    (
        "agents.specialists.swarm_predict.agent",
        "SwarmPredictSpecialist",
        "swarm_predict",
        "Predict trends",
    ),
    ("agents.specialists.deer_flow.agent", "DeerFlowSpecialist", "deer_flow", "Generate code"),
]


class TestSpecialistConsistency:
    """All specialists must follow the same contract."""

    @pytest.mark.parametrize(
        "mod_path,cls_name,name,query_text",
        _V1_SPECIALISTS,
        ids=[t[2] for t in _V1_SPECIALISTS],
    )
    @pytest.mark.asyncio
    async def test_returns_specialist_response(
        self, mod_path: str, cls_name: str, name: str, query_text: str
    ) -> None:
        import importlib

        mod = importlib.import_module(mod_path)
        specialist = getattr(mod, cls_name)()
        req = make_request(name, query_text)
        resp = await specialist.execute(req)
        assert isinstance(resp, SpecialistResponse), f"{name} didn't return SpecialistResponse"
        assert resp.specialist_name == name
        assert resp.status == "success"

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
