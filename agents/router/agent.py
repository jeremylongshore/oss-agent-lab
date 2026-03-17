"""
Router Agent — Tier 2: Capability matching, parallel dispatch, and aggregation.

Receives intents from Conductor, queries the Registry for matching specialists,
dispatches requests in parallel, and aggregates results.
"""
from oss_agent_lab.contracts import Intent, SpecialistResponse


class RouterAgent:
    """Tier 2 agent: intent → specialist matching → dispatch → aggregation."""

    async def route(self, intent: Intent) -> list[SpecialistResponse]:
        """Route an intent to matching specialists.

        Args:
            intent: Classified intent from Conductor.

        Returns:
            Aggregated responses from matched specialists.
        """
        raise NotImplementedError("Router implementation: Epic 2")
