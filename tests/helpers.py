"""Shared test fixtures and helpers."""

from __future__ import annotations

from oss_agent_lab.contracts import Intent, Query, SpecialistRequest


def make_request(
    specialist_name: str,
    user_input: str,
    action: str = "research",
    domain: str = "ai",
    **params: object,
) -> SpecialistRequest:
    """Build a ``SpecialistRequest`` for testing."""
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
