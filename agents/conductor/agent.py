"""
Conductor Agent — Tier 1: Natural language interface and task decomposition.

Accepts natural language queries, classifies intent, and routes to the Router.
Uses Claude SDK for intent classification.
"""
from oss_agent_lab.contracts import Intent, Query


class ConductorAgent:
    """Tier 1 agent: NL input → intent classification → routing."""

    async def process(self, query: Query) -> Intent:
        """Process a natural language query into a structured intent.

        Args:
            query: User's natural language query with optional context.

        Returns:
            Classified intent with action, domain, confidence, parameters.
        """
        raise NotImplementedError("Conductor implementation: Epic 2")
