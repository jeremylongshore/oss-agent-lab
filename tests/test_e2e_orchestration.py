"""E2E integration tests for the orchestration pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.conductor.agent import ConductorAgent
from agents.memory.session import SessionMemory
from agents.router.agent import RouterAgent
from agents.router.registry import SpecialistRegistry
from oss_agent_lab.contracts import (
    Intent,
    Query,
    SessionContext,
    SpecialistRequest,
    SpecialistResponse,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_SKILL_MD = """\
---
name: test_specialist
display_name: Test Specialist
description: A test specialist for integration tests
version: 0.1.0
capabilities:
  - research
  - ai
allowed_tools:
  - search_tool
---

# Test Specialist
"""


@pytest.fixture()
def specialist_dir(tmp_path: Path) -> Path:
    """Create a temporary specialists directory with a discoverable specialist."""
    spec_dir = tmp_path / "specialists" / "test_specialist"
    spec_dir.mkdir(parents=True)
    (spec_dir / "SKILL.md").write_text(SAMPLE_SKILL_MD, encoding="utf-8")
    return tmp_path / "specialists"


@pytest.fixture()
def registry_with_mock() -> SpecialistRegistry:
    """Registry with a manually registered mock specialist."""
    registry = SpecialistRegistry(specialists_dir=Path("/nonexistent"))
    registry.register(
        "mock_researcher",
        {
            "name": "mock_researcher",
            "description": "Mock research specialist",
            "capabilities": ["research", "ai"],
        },
    )
    return registry


@pytest.fixture()
def sample_intent() -> Intent:
    return Intent(
        action="research",
        domain="ai",
        confidence=0.95,
        parameters={"topic": "transformers"},
    )


@pytest.fixture()
def sample_query() -> Query:
    return Query(user_input="Tell me about transformers in AI")


# ---------------------------------------------------------------------------
# 1. Registry discovers specialists from SKILL.md
# ---------------------------------------------------------------------------


class TestRegistryDiscoversTemplate:
    def test_discovers_specialist_from_skill_md(self, specialist_dir: Path) -> None:
        """Discover a specialist dir containing a SKILL.md with YAML frontmatter."""
        registry = SpecialistRegistry(specialists_dir=specialist_dir)
        count = registry.discover()

        assert count == 1
        meta = registry.get("test_specialist")
        assert meta is not None
        assert meta["name"] == "test_specialist"
        assert "research" in meta["capabilities"]
        assert "ai" in meta["capabilities"]
        assert meta["description"] == "A test specialist for integration tests"


# ---------------------------------------------------------------------------
# 2. Registry match_capabilities
# ---------------------------------------------------------------------------


class TestRegistryMatchCapabilities:
    def test_match_returns_specialist(self, registry_with_mock: SpecialistRegistry) -> None:
        """A registered specialist with matching capabilities is returned."""
        matches = registry_with_mock.match_capabilities(["research"])
        assert "mock_researcher" in matches

    def test_no_match_returns_empty(self, registry_with_mock: SpecialistRegistry) -> None:
        """Capabilities that don't overlap return an empty list."""
        matches = registry_with_mock.match_capabilities(["finance"])
        assert matches == []


# ---------------------------------------------------------------------------
# 3. Conductor classifies intent (mocked Anthropic client)
# ---------------------------------------------------------------------------


class TestConductorClassifiesIntent:
    @pytest.mark.asyncio
    async def test_process_returns_intent(self, sample_query: Query) -> None:
        """ConductorAgent.process() returns a well-formed Intent (API mocked)."""
        intent_json = json.dumps(
            {
                "action": "research",
                "domain": "ai",
                "confidence": 0.92,
                "parameters": {"topic": "transformers"},
            }
        )

        # Build a mock Anthropic response message.
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = intent_json

        mock_message = MagicMock()
        mock_message.content = [mock_text_block]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        conductor = ConductorAgent()
        conductor._client = mock_client  # type: ignore[assignment]

        intent = await conductor.process(sample_query)

        assert isinstance(intent, Intent)
        assert intent.action == "research"
        assert intent.domain == "ai"
        assert intent.confidence == pytest.approx(0.92)
        assert intent.parameters["topic"] == "transformers"


# ---------------------------------------------------------------------------
# 4. Router dispatches to specialist
# ---------------------------------------------------------------------------


class TestRouterDispatchesToSpecialist:
    @pytest.mark.asyncio
    async def test_route_returns_specialist_responses(
        self,
        sample_intent: Intent,
        registry_with_mock: SpecialistRegistry,
    ) -> None:
        """Router routes an intent to a matching specialist and returns responses."""
        router = RouterAgent(registry=registry_with_mock)

        # Mock _dispatch_to_specialist to avoid real module import.
        expected_response = SpecialistResponse(
            specialist_name="mock_researcher",
            status="success",
            result={"findings": ["transformers are great"]},
            duration_ms=42.0,
        )
        router._dispatch_to_specialist = AsyncMock(  # type: ignore[method-assign]
            return_value=expected_response,
        )

        responses = await router.route(sample_intent)

        assert len(responses) == 1
        assert responses[0].specialist_name == "mock_researcher"
        assert responses[0].status == "success"
        assert responses[0].result == {"findings": ["transformers are great"]}


# ---------------------------------------------------------------------------
# 5. Full pipeline mock: Conductor -> Router -> Specialist
# ---------------------------------------------------------------------------


class TestFullPipelineMock:
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self, registry_with_mock: SpecialistRegistry) -> None:
        """Full flow: Query -> Conductor (mocked) -> Intent -> Router -> Response."""
        query = Query(user_input="Analyze trending AI repos")

        # --- Conductor (mocked) ---
        intent_json = json.dumps(
            {
                "action": "research",
                "domain": "ai",
                "confidence": 0.88,
                "parameters": {"topic": "trending AI"},
            }
        )

        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = intent_json

        mock_message = MagicMock()
        mock_message.content = [mock_text_block]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        conductor = ConductorAgent()
        conductor._client = mock_client  # type: ignore[assignment]

        intent = await conductor.process(query)
        assert isinstance(intent, Intent)
        assert intent.action == "research"

        # --- Router ---
        router = RouterAgent(registry=registry_with_mock)

        specialist_response = SpecialistResponse(
            specialist_name="mock_researcher",
            status="success",
            result={"summary": "trending repos analyzed"},
            duration_ms=100.0,
        )
        router._dispatch_to_specialist = AsyncMock(  # type: ignore[method-assign]
            return_value=specialist_response,
        )

        responses = await router.route(intent)

        assert len(responses) == 1
        resp = responses[0]
        assert resp.specialist_name == "mock_researcher"
        assert resp.status == "success"
        assert resp.result == {"summary": "trending repos analyzed"}

        # Verify the dispatch was called with a SpecialistRequest.
        call_args = router._dispatch_to_specialist.call_args
        dispatched_request: SpecialistRequest = call_args[0][0]
        assert isinstance(dispatched_request, SpecialistRequest)
        assert dispatched_request.specialist_name == "mock_researcher"
        assert dispatched_request.intent == intent


# ---------------------------------------------------------------------------
# 6. Session memory store and recall
# ---------------------------------------------------------------------------


class TestSessionMemoryStoreAndRecall:
    @pytest.mark.asyncio
    async def test_store_and_recall(self) -> None:
        """Store entries, recall by keyword, verify results."""
        mem = SessionMemory()

        await mem.store({"role": "user", "content": "Tell me about transformers"})
        await mem.store({"role": "assistant", "content": "Transformers use attention"})
        await mem.store({"role": "user", "content": "What about finance models?"})

        results = await mem.recall("transformers")
        assert len(results) >= 1
        # Both transformer-related entries should appear.
        contents = [r.get("content", "") for r in results]
        assert any("transformers" in c.lower() for c in contents)

    @pytest.mark.asyncio
    async def test_recall_returns_empty_for_no_match(self) -> None:
        """Recall with a query that matches nothing returns empty."""
        mem = SessionMemory()
        await mem.store({"role": "user", "content": "hello world"})

        results = await mem.recall("xyzzyx_no_match")
        assert results == []

    @pytest.mark.asyncio
    async def test_recall_respects_top_k(self) -> None:
        """Recall respects the top_k limit."""
        mem = SessionMemory()
        for i in range(10):
            await mem.store({"content": f"item {i} about AI"})

        results = await mem.recall("AI", top_k=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_get_context(self) -> None:
        """get_context returns a SessionContext with the full history."""
        mem = SessionMemory(session_id="test-session")
        await mem.store({"role": "user", "content": "hi"})

        ctx = mem.get_context()
        assert isinstance(ctx, SessionContext)
        assert ctx.session_id == "test-session"
        assert len(ctx.history) == 1

    def test_session_id_auto_generated(self) -> None:
        """Session ID is a UUID when not provided."""
        mem = SessionMemory()
        assert len(mem.session_id) == 36  # UUID format: 8-4-4-4-12


# ---------------------------------------------------------------------------
# 7. Session memory persistence
# ---------------------------------------------------------------------------


class TestSessionMemoryPersistence:
    @pytest.mark.asyncio
    async def test_persist_and_reload(self, tmp_path: Path) -> None:
        """Store entries with persistence, create new instance, verify recall works."""
        session_id = "persist-test-session"
        persist_dir = str(tmp_path / "memory")

        # First instance: store entries.
        mem1 = SessionMemory(session_id=session_id, persist_dir=persist_dir)
        await mem1.store({"role": "user", "content": "machine learning research"})
        await mem1.store({"role": "assistant", "content": "here are the results"})

        # Verify file was created.
        expected_file = tmp_path / "memory" / f"{session_id}.json"
        assert expected_file.exists()

        # Second instance: same session_id and persist_dir should load history.
        mem2 = SessionMemory(session_id=session_id, persist_dir=persist_dir)

        results = await mem2.recall("machine learning")
        assert len(results) >= 1
        assert any("machine learning" in r.get("content", "") for r in results)

        # Context should have the full history.
        ctx = mem2.get_context()
        assert len(ctx.history) == 2

    @pytest.mark.asyncio
    async def test_persist_creates_directory(self, tmp_path: Path) -> None:
        """persist() creates the persist_dir if it doesn't exist."""
        persist_dir = str(tmp_path / "nested" / "deep" / "memory")
        mem = SessionMemory(session_id="mkdir-test", persist_dir=persist_dir)
        await mem.store({"data": "test"})

        assert (tmp_path / "nested" / "deep" / "memory" / "mkdir-test.json").exists()


# ---------------------------------------------------------------------------
# 8. Router handles no matching specialists
# ---------------------------------------------------------------------------


class TestRouterHandlesNoMatchingSpecialists:
    @pytest.mark.asyncio
    async def test_no_match_returns_error_response(self) -> None:
        """When no specialist matches, router returns a graceful error response."""
        registry = SpecialistRegistry(specialists_dir=Path("/nonexistent"))
        registry.register(
            "weather_bot",
            {
                "name": "weather_bot",
                "capabilities": ["weather", "forecast"],
            },
        )

        router = RouterAgent(registry=registry)

        # Intent with capabilities that don't match any specialist.
        intent = Intent(
            action="encrypt",
            domain="security",
            confidence=0.9,
            parameters={},
        )

        responses = await router.route(intent)

        assert len(responses) == 1
        resp = responses[0]
        assert resp.status == "error"
        assert resp.specialist_name == "router"
        assert "No specialists found" in str(resp.result)
