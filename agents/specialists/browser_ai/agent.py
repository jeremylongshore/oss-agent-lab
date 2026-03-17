"""
BrowserAI specialist — headless web automation for AI workloads.

Wraps lightpanda-io/browser: a lightweight, Zig-written headless browser engine
designed specifically for AI agents. The specialist provides a clean async
interface for navigation, content extraction, and screenshot capture, composing
the three tools in a single execute() call.

Usage:
    specialist = BrowserAiSpecialist()
    response = await specialist.execute(request)
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse

from .tools import extract_content, navigate, take_screenshot


class BrowserAiSpecialist(BaseSpecialist):
    """Headless web automation specialist powered by lightpanda-io/browser.

    Executes a three-stage pipeline for each request:

    1. Navigate — load the target URL and capture load metadata.
    2. Extract — pull structured content from the rendered DOM.
    3. Screenshot — capture a PNG of the rendered viewport.

    The specialist is stateless; every :meth:`execute` call is independent.

    Attributes:
        name: Specialist identifier used for routing.
        description: Human-readable capability summary.
        source_repo: Upstream GitHub repository this specialist wraps.
        capabilities: List of string capability tags.
        output_formats: Supported output modes.
        tools: Tool descriptors made available to the agent runtime.
    """

    name: ClassVar[str] = "browser_ai"
    description: ClassVar[str] = (
        "Headless web automation for AI: navigate pages, extract content, and capture screenshots"
    )
    source_repo: ClassVar[str] = "lightpanda-io/browser"

    capabilities: ClassVar[list[str]] = [
        "browse",
        "web_automation",
        "scrape",
        "screenshot",
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
            name="navigate",
            description=(
                "Load a URL in the headless browser and return HTTP status, page title, "
                "final URL after redirects, and load time in milliseconds."
            ),
            parameters={
                "url": {"type": "string", "description": "Fully-qualified URL to load"},
                "wait_for": {
                    "type": "string",
                    "description": "CSS selector or event to wait for before page-ready",
                    "default": None,
                },
            },
        ),
        Tool(
            name="extract_content",
            description=(
                "Extract DOM content matching a CSS selector from the rendered page. "
                "Supports text, HTML, and markdown output formats."
            ),
            parameters={
                "url": {"type": "string", "description": "URL of the page to extract from"},
                "selector": {
                    "type": "string",
                    "description": "CSS selector targeting the element(s) to extract",
                    "default": "body",
                },
                "format": {
                    "type": "string",
                    "description": "Output format: text | html | markdown",
                    "default": "text",
                },
            },
        ),
        Tool(
            name="take_screenshot",
            description=(
                "Capture a PNG screenshot of the fully-rendered page at the specified "
                "viewport dimensions. Returns the file path and image metadata."
            ),
            parameters={
                "url": {"type": "string", "description": "URL of the page to screenshot"},
                "viewport": {
                    "type": "string",
                    "description": "Viewport size as WIDTHxHEIGHT (e.g. '1920x1080')",
                    "default": "1920x1080",
                },
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Run the full browser automation pipeline for the given request.

        Extracts the target URL and optional parameters from the request, then
        runs navigation, content extraction, and screenshot in sequence.

        The URL is resolved from ``request.intent.parameters["url"]`` when
        present; otherwise ``request.query.user_input`` is used directly.
        Additional parameters (``selector``, ``format``, ``wait_for``,
        ``viewport``) may be supplied via ``request.intent.parameters``.

        Args:
            request: The routed specialist request, carrying an
                :class:`~oss_agent_lab.contracts.Intent` and a
                :class:`~oss_agent_lab.contracts.Query`.

        Returns:
            A :class:`~oss_agent_lab.contracts.SpecialistResponse` with:

            - ``status``: ``"success"`` on a clean run.
            - ``result``: Dict containing ``url``, ``navigation``,
              ``extraction``, and ``screenshot`` sub-sections.
            - ``metadata``: Source repo, selector, and format details.
            - ``duration_ms``: Wall-clock time for the full pipeline.
        """
        t_start = time.perf_counter()

        params: dict[str, Any] = request.intent.parameters or {}

        # Resolve the target URL — prefer an explicit parameter, fall back to raw input.
        url: str = str(params.get("url") or request.query.user_input).strip()
        selector: str = str(params.get("selector", "body"))
        content_format: str = str(params.get("format", "text"))
        wait_for: str | None = params.get("wait_for")
        viewport: str = str(params.get("viewport", "1920x1080"))

        # Stage 1: navigate to the target URL.
        nav_result = navigate(url=url, wait_for=wait_for)

        # Stage 2: extract content from the rendered page.
        # Use the final (post-redirect) URL returned by navigate.
        extraction_result = extract_content(
            url=nav_result["url"],
            selector=selector,
            format=content_format,
        )

        # Stage 3: capture a screenshot of the rendered viewport.
        screenshot_result = take_screenshot(url=nav_result["url"], viewport=viewport)

        duration_ms = (time.perf_counter() - t_start) * 1000.0

        result: dict[str, Any] = {
            "url": nav_result["url"],
            "navigation": nav_result,
            "extraction": extraction_result,
            "screenshot": screenshot_result,
        }

        metadata: dict[str, Any] = {
            "source_repo": self.source_repo,
            "selector": selector,
            "content_format": content_format,
            "viewport": viewport,
            "http_status": nav_result["status_code"],
        }

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result=result,
            metadata=metadata,
            duration_ms=round(duration_ms, 3),
        )
