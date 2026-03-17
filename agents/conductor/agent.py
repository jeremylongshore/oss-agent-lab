"""
Conductor Agent — Tier 1: Natural language interface and task decomposition.

Accepts natural language queries, classifies intent, and routes to the Router.
Uses Claude SDK for intent classification.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from oss_agent_lab.contracts import Intent, Query

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an intent classifier. Given a user query, extract the structured intent.\n"
    "\n"
    "Respond with ONLY a JSON object (no markdown, no explanation) with these fields:\n"
    '- "action": one of "research", "predict", "analyze", "browse",\n'
    '  "execute", "summarize", "compare", "general"\n'
    '- "domain": one of "ai", "finance", "sentiment", "code",\n'
    '  "security", "data", "general"\n'
    '- "confidence": float 0.0-1.0 indicating classification confidence\n'
    '- "parameters": object with relevant parameters extracted from the query\n'
    "  (e.g., topic, language, url, ticker, repo, timeframe)\n"
    "\n"
    "Example response:\n"
    '{"action": "research", "domain": "ai", "confidence": 0.92,'
    ' "parameters": {"topic": "transformers"}}'
)

_FALLBACK_INTENT = Intent(
    action="general",
    domain="general",
    confidence=0.3,
    parameters={},
)


class ConductorAgent:
    """Tier 1 agent: NL input -> intent classification -> routing."""

    def __init__(
        self,
        *,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 256,
    ) -> None:
        self._client = anthropic.AsyncAnthropic()
        self._model = model
        self._max_tokens = max_tokens

    async def process(self, query: Query) -> Intent:
        """Process a natural language query into a structured intent.

        Args:
            query: User's natural language query with optional context.

        Returns:
            Classified intent with action, domain, confidence, parameters.
        """
        user_message = query.user_input
        if query.context:
            user_message += f"\n\nAdditional context: {json.dumps(query.context)}"

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
        except anthropic.APIError as exc:
            logger.warning("Anthropic API error during intent classification: %s", exc)
            return _FALLBACK_INTENT

        return self._parse_response(response)

    def _parse_response(self, response: anthropic.types.Message) -> Intent:
        """Extract an Intent from the Claude API response.

        Args:
            response: Raw message response from the Anthropic API.

        Returns:
            Parsed Intent, or fallback on failure.
        """
        text = self._extract_text(response)
        if text is None:
            logger.warning("No text content in API response")
            return _FALLBACK_INTENT

        try:
            data: dict[str, Any] = json.loads(text)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Failed to parse intent JSON: %s", exc)
            return _FALLBACK_INTENT

        try:
            return Intent(
                action=str(data.get("action", "general")),
                domain=str(data.get("domain", "general")),
                confidence=float(data.get("confidence", 0.5)),
                parameters=data.get("parameters") or {},
            )
        except (ValueError, TypeError) as exc:
            logger.warning("Failed to construct Intent from parsed data: %s", exc)
            return _FALLBACK_INTENT

    @staticmethod
    def _extract_text(response: anthropic.types.Message) -> str | None:
        """Pull the first text block out of a Message.

        Args:
            response: The API response message.

        Returns:
            The text string, or None if no text block is found.
        """
        for block in response.content:
            if block.type == "text":
                return block.text
        return None
