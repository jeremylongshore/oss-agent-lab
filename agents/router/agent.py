"""
Router Agent — Tier 2: Capability matching, parallel dispatch, and aggregation.

Receives intents from Conductor, queries the Registry for matching specialists,
dispatches requests in parallel, and aggregates results.
"""

from __future__ import annotations

import asyncio
import importlib
import logging
import time
from typing import Any

from oss_agent_lab.contracts import Intent, Query, SpecialistRequest, SpecialistResponse

from .registry import SpecialistRegistry

logger = logging.getLogger(__name__)


class RouterAgent:
    """Tier 2 agent: intent -> specialist matching -> dispatch -> aggregation."""

    def __init__(self, registry: SpecialistRegistry | None = None) -> None:
        if registry is not None:
            self._registry = registry
        else:
            self._registry = SpecialistRegistry()
            discovered = self._registry.discover()
            logger.info("RouterAgent auto-discovered %d specialist(s)", discovered)

    async def route(self, intent: Intent) -> list[SpecialistResponse]:
        """Route an intent to matching specialists.

        Extracts capabilities from the intent's action and domain, queries the
        registry for matching specialists, dispatches requests concurrently,
        and returns aggregated responses.

        Args:
            intent: Classified intent from Conductor.

        Returns:
            Aggregated responses from matched specialists.
        """
        capabilities = [intent.action, intent.domain]

        matched_names = self._registry.match_capabilities(capabilities)

        if not matched_names:
            logger.warning(
                "No specialists matched capabilities %s for intent action=%s domain=%s",
                capabilities,
                intent.action,
                intent.domain,
            )
            return [
                SpecialistResponse(
                    specialist_name="router",
                    status="error",
                    result=(
                        f"No specialists found matching capabilities: {capabilities}. "
                        f"Available specialists: "
                        f"{[m.get('name', '?') for m in self._registry.list_all()]}"
                    ),
                )
            ]

        # Build a SpecialistRequest for each matched specialist.
        query = Query(
            user_input=intent.parameters.get("user_input", ""),
            context=intent.parameters,
        )
        requests = [
            SpecialistRequest(
                intent=intent,
                query=query,
                specialist_name=name,
            )
            for name in matched_names
        ]

        logger.info(
            "Dispatching to %d specialist(s): %s",
            len(requests),
            [r.specialist_name for r in requests],
        )

        responses: list[SpecialistResponse] = await asyncio.gather(
            *(self._dispatch_to_specialist(req) for req in requests),
        )

        return responses

    async def _dispatch_to_specialist(
        self,
        request: SpecialistRequest,
    ) -> SpecialistResponse:
        """Import, instantiate, and execute a single specialist.

        Dynamically loads ``agents.specialists.<name>.agent`` and looks for a
        class with an ``execute`` method. Failures are caught and returned as
        error responses.

        Args:
            request: The specialist request to dispatch.

        Returns:
            Response from the specialist, or an error response on failure.
        """
        name = request.specialist_name
        start = time.monotonic()

        try:
            module = importlib.import_module(f"agents.specialists.{name}.agent")
        except ImportError as exc:
            logger.warning("Failed to import specialist %s: %s", name, exc)
            return SpecialistResponse(
                specialist_name=name,
                status="error",
                result=f"Import error: {exc}",
                duration_ms=_elapsed_ms(start),
            )

        # Find the specialist class — the first BaseSpecialist subclass in the module.
        specialist_cls = _find_specialist_class(module)
        if specialist_cls is None:
            logger.warning("No specialist class found in agents.specialists.%s.agent", name)
            return SpecialistResponse(
                specialist_name=name,
                status="error",
                result="No specialist class found in module",
                duration_ms=_elapsed_ms(start),
            )

        try:
            specialist = specialist_cls()
            response: SpecialistResponse = await specialist.execute(request)
            response.duration_ms = _elapsed_ms(start)
            return response
        except Exception as exc:
            logger.exception("Specialist %s raised an exception", name)
            return SpecialistResponse(
                specialist_name=name,
                status="error",
                result=f"Execution error: {exc}",
                duration_ms=_elapsed_ms(start),
            )


def _elapsed_ms(start: float) -> float:
    """Return milliseconds elapsed since *start* (monotonic)."""
    return (time.monotonic() - start) * 1000.0


def _find_specialist_class(module: Any) -> type | None:
    """Locate the first BaseSpecialist subclass defined in *module*.

    Args:
        module: The imported specialist module.

    Returns:
        The specialist class, or None.
    """
    from oss_agent_lab.base import BaseSpecialist

    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and issubclass(attr, BaseSpecialist)
            and attr is not BaseSpecialist
        ):
            return attr
    return None
