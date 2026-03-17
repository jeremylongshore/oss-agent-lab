"""Tests for ConductorAgent — Tier 1 intent classification."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from oss_agent_lab.contracts import Intent, Query


class TestConductorAgent:
    """Tests for the ConductorAgent class."""

    def _make_api_response(self, text: str) -> MagicMock:
        """Helper to create a mock Anthropic Message response."""
        block = MagicMock()
        block.type = "text"
        block.text = text
        response = MagicMock()
        response.content = [block]
        return response

    @pytest.mark.asyncio
    async def test_process_returns_intent(self) -> None:
        with patch("agents.conductor.agent.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=self._make_api_response(
                    '{"action": "research", "domain": "ai", "confidence": 0.92, "parameters": {"topic": "transformers"}}'
                )
            )

            from agents.conductor.agent import ConductorAgent

            agent = ConductorAgent()
            agent._client = mock_client

            query = Query(user_input="Research transformers architecture")
            intent = await agent.process(query)

            assert isinstance(intent, Intent)
            assert intent.action == "research"
            assert intent.domain == "ai"
            assert intent.confidence == 0.92
            assert intent.parameters == {"topic": "transformers"}

    @pytest.mark.asyncio
    async def test_process_with_context(self) -> None:
        with patch("agents.conductor.agent.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=self._make_api_response(
                    '{"action": "analyze", "domain": "finance", "confidence": 0.85, "parameters": {"ticker": "AAPL"}}'
                )
            )

            from agents.conductor.agent import ConductorAgent

            agent = ConductorAgent()
            agent._client = mock_client

            query = Query(
                user_input="Analyze AAPL stock",
                context={"timeframe": "1y"},
            )
            intent = await agent.process(query)

            assert intent.action == "analyze"
            assert intent.domain == "finance"
            # Verify context was included in the API call
            call_args = mock_client.messages.create.call_args
            assert "1y" in str(call_args)

    @pytest.mark.asyncio
    async def test_fallback_on_api_error(self) -> None:
        with patch("agents.conductor.agent.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client
            mock_anthropic.APIError = Exception
            mock_client.messages.create = AsyncMock(side_effect=Exception("API down"))

            from agents.conductor.agent import ConductorAgent

            agent = ConductorAgent()
            agent._client = mock_client

            query = Query(user_input="test query")
            intent = await agent.process(query)

            assert intent.action == "general"
            assert intent.domain == "general"
            assert intent.confidence == 0.3

    @pytest.mark.asyncio
    async def test_fallback_on_invalid_json(self) -> None:
        with patch("agents.conductor.agent.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client
            mock_client.messages.create = AsyncMock(
                return_value=self._make_api_response("not valid json at all")
            )

            from agents.conductor.agent import ConductorAgent

            agent = ConductorAgent()
            agent._client = mock_client

            query = Query(user_input="test")
            intent = await agent.process(query)

            assert intent.action == "general"
            assert intent.confidence == 0.3

    @pytest.mark.asyncio
    async def test_fallback_on_empty_response(self) -> None:
        with patch("agents.conductor.agent.anthropic") as mock_anthropic:
            mock_client = AsyncMock()
            mock_anthropic.AsyncAnthropic.return_value = mock_client
            response = MagicMock()
            response.content = []  # No text blocks
            mock_client.messages.create = AsyncMock(return_value=response)

            from agents.conductor.agent import ConductorAgent

            agent = ConductorAgent()
            agent._client = mock_client

            query = Query(user_input="test")
            intent = await agent.process(query)

            assert intent.action == "general"

    def test_parse_response_valid(self) -> None:
        with patch("agents.conductor.agent.anthropic"):
            from agents.conductor.agent import ConductorAgent

            agent = ConductorAgent.__new__(ConductorAgent)
            response = self._make_api_response(
                '{"action": "browse", "domain": "code", "confidence": 0.8, "parameters": {}}'
            )
            intent = agent._parse_response(response)
            assert intent.action == "browse"
            assert intent.domain == "code"

    def test_parse_response_missing_fields_uses_defaults(self) -> None:
        with patch("agents.conductor.agent.anthropic"):
            from agents.conductor.agent import ConductorAgent

            agent = ConductorAgent.__new__(ConductorAgent)
            response = self._make_api_response('{"action": "research"}')
            intent = agent._parse_response(response)
            assert intent.action == "research"
            assert intent.domain == "general"
            assert intent.confidence == 0.5
