"""
GUI Agent specialist — natural language web UI control.

Wraps alibaba/page-agent to provide element detection, targeted UI interaction,
and automated form-filling from plain-English instructions. The specialist
processes a natural-language web-interaction request, detects the relevant page
elements, and performs the requested action sequence.

Usage:
    specialist = GuiAgentSpecialist()
    response = await specialist.execute(request)
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse

from .tools import detect_elements, fill_form, interact_element


class GuiAgentSpecialist(BaseSpecialist):
    """Natural-language web UI control via alibaba/page-agent.

    Accepts a plain-English web-interaction request and executes it in three
    stages:
    1. Element detection — discovers interactive elements on the target page.
    2. Element interaction — performs the requested action on matched elements.
    3. Form filling — when form data is provided, populates and validates fields.
    """

    name: ClassVar[str] = "gui_agent"
    description: ClassVar[str] = (
        "Natural language web UI control: element detection, interaction, and form filling"
    )
    source_repo: ClassVar[str] = "alibaba/page-agent"

    capabilities: ClassVar[list[str]] = [
        "gui_automation",
        "web_interaction",
        "element_detection",
        "form_filling",
    ]

    output_formats: ClassVar[list[OutputFormat]] = [
        OutputFormat.PYTHON_API,
        OutputFormat.CLI,
        OutputFormat.MCP_SERVER,
        OutputFormat.AGENT_SKILL,
        OutputFormat.REST_API,
    ]

    tools: ClassVar[list[Tool]] = [
        Tool(
            name="detect_elements",
            description=(
                "Detect interactive UI elements on a web page, optionally filtered by "
                "a natural-language description of the target element."
            ),
            parameters={
                "url": "str",
                "description": "str | None = None",
            },
        ),
        Tool(
            name="interact_element",
            description=(
                "Perform a specified action (click, type, hover, focus, or clear) on a "
                "UI element identified by its stable element ID."
            ),
            parameters={
                "element_id": "str",
                "action": "str = 'click'",
                "value": "str | None = None",
            },
        ),
        Tool(
            name="fill_form",
            description=(
                "Fill a web form at the given URL with a mapping of field labels to "
                "values, returning fill status and any validation errors."
            ),
            parameters={
                "url": "str",
                "form_data": "dict[str, str]",
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Process a natural-language web interaction request end-to-end.

        Stages:
            1. Extract the target URL and interaction description from the request.
            2. Detect page elements matching the description via ``detect_elements``.
            3. Interact with the first matched element via ``interact_element``.
            4. If ``form_data`` is present in parameters, fill the form via
               ``fill_form`` and include those results.

        Args:
            request: Incoming specialist request containing the intent (with
                optional ``url``, ``description``, ``action``, ``value``, and
                ``form_data`` parameters) and the raw user query.

        Returns:
            SpecialistResponse with status ``"success"`` and a ``result`` dict
            containing ``detection``, ``interaction``, and optionally ``form``
            sub-sections, plus execution metadata.
        """
        start_ms = time.monotonic() * 1000
        params: dict[str, Any] = dict(request.intent.parameters)

        # Extract parameters with sensible fallbacks.
        url: str = str(params.get("url", "https://example.com"))
        description: str | None = params.get("description") or request.query.user_input or None
        action: str = str(params.get("action", "click"))
        value: str | None = params.get("value")

        # Stage 1: detect elements on the target page.
        detection = detect_elements(url=url, description=description)

        # Stage 2: interact with the first detected element.
        elements: list[dict[str, Any]] = detection["elements"]
        first_element_id: str = elements[0]["id"] if elements else "elem-unknown"
        interaction = interact_element(
            element_id=first_element_id,
            action=action,
            value=value,
        )

        result: dict[str, Any] = {
            "url": url,
            "description": description,
            "detection": detection,
            "interaction": interaction,
        }

        # Stage 3 (optional): fill form when form_data is provided.
        form_result: dict[str, Any] | None = None
        raw_form_data = params.get("form_data")
        if raw_form_data and isinstance(raw_form_data, dict):
            form_data: dict[str, str] = {str(k): str(v) for k, v in raw_form_data.items()}
            form_result = fill_form(url=url, form_data=form_data)
            result["form"] = form_result

        duration_ms = time.monotonic() * 1000 - start_ms

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result=result,
            metadata={
                "source_repo": self.source_repo,
                "url": url,
                "action": action,
                "elements_detected": detection["element_count"],
                "form_filled": form_result is not None,
                "submit_ready": form_result["submit_ready"] if form_result else None,
            },
            duration_ms=round(duration_ms, 2),
        )
