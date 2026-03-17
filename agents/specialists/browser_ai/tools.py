"""
Tools for the BrowserAI specialist.

Simulates headless web automation backed by lightpanda-io/browser: a fast,
lightweight browser engine purpose-built for AI workloads. Each tool is a pure
function — no real network I/O occurs in this simulation layer.
"""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse


def navigate(url: str, wait_for: str | None = None) -> dict[str, Any]:
    """Navigate to a URL and return page load metadata.

    Simulates lightpanda browser page navigation. In production this would
    drive the actual browser binary over its CDP/WebSocket interface.

    Args:
        url: Fully-qualified URL to load (e.g. ``"https://example.com"``).
        wait_for: Optional CSS selector or event name to wait for before
            considering the page ready (e.g. ``"#main-content"``,
            ``"networkidle"``). When ``None`` the tool waits for
            ``DOMContentLoaded``.

    Returns:
        Dict with the following keys:

        - ``status_code`` (int): HTTP response code for the main document.
        - ``title`` (str): Page ``<title>`` text.
        - ``url`` (str): Final URL after any redirects.
        - ``load_time_ms`` (float): Elapsed time from navigation start to
          page-ready event, in milliseconds.
    """
    if not url.strip():
        raise ValueError("url must not be empty")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"url scheme must be http or https; got {parsed.scheme!r}")

    # Simulate a deterministic but plausible load time (50-300 ms).
    seed = sum(ord(c) for c in url)
    load_time_ms = round(50.0 + (seed % 251), 2)

    # Derive a synthetic title from the host + path.
    host = parsed.netloc or "unknown"
    path_slug = (parsed.path.strip("/").replace("/", " — ") or "Home").title()
    title = f"{host} | {path_slug}"

    # Simulate occasional redirects (e.g. http → https).
    final_url = url if url.startswith("https://") else url.replace("http://", "https://", 1)

    # Simulate a 200 for well-formed URLs; 404 for obviously missing resources.
    status_code = 404 if "/404" in url else 200

    if wait_for:
        # Waiting for a selector adds latency in a real browser.
        load_time_ms = round(load_time_ms + 30.0, 2)

    return {
        "status_code": status_code,
        "title": title,
        "url": final_url,
        "load_time_ms": load_time_ms,
    }


def extract_content(
    url: str,
    selector: str = "body",
    format: str = "text",
) -> dict[str, Any]:
    """Extract content from a web page matching a CSS selector.

    Simulates the lightpanda DOM extraction API. Supports ``text``, ``html``,
    and ``markdown`` output formats.

    Args:
        url: URL of the page to extract content from.
        selector: CSS selector targeting the element(s) to extract
            (default: ``"body"``).
        format: Output format for the extracted content — one of
            ``"text"``, ``"html"``, or ``"markdown"`` (default: ``"text"``).

    Returns:
        Dict with the following keys:

        - ``content`` (str): Extracted content in the requested format.
        - ``selector_matched`` (bool): Whether the selector matched any
          elements in the DOM.
        - ``element_count`` (int): Number of elements matched by the selector.
    """
    if not url.strip():
        raise ValueError("url must not be empty")

    known_formats = {"text", "html", "markdown"}
    if format not in known_formats:
        raise ValueError(f"format must be one of {sorted(known_formats)!r}; got {format!r}")

    parsed = urlparse(url)
    host = parsed.netloc or "unknown"
    path = parsed.path.strip("/") or "index"

    # Simulate selector matching — "body" always matches; others may not.
    selector_matched = selector in {"body", "main", "article", "#content", ".content"}
    element_count = 1 if selector_matched else 0

    if not selector_matched:
        return {
            "content": "",
            "selector_matched": False,
            "element_count": 0,
        }

    # Produce format-appropriate synthetic content.
    raw_text = (
        f"Extracted content from {host}/{path} "
        f"(selector: {selector!r}). "
        "This is simulated page content representing the text that lightpanda "
        "would extract from the live DOM."
    )

    if format == "html":
        content = f"<div data-selector={selector!r}><p>{raw_text}</p></div>"
    elif format == "markdown":
        content = f"## Content from `{selector}`\n\n{raw_text}\n"
    else:
        content = raw_text

    return {
        "content": content,
        "selector_matched": selector_matched,
        "element_count": element_count,
    }


def take_screenshot(url: str, viewport: str = "1920x1080") -> dict[str, Any]:
    """Capture a screenshot of a rendered web page.

    Simulates the lightpanda screenshot API, which renders the full page in the
    headless browser and returns a PNG image path. In production the file would
    be written to a temporary directory managed by the browser subprocess.

    Args:
        url: URL of the page to screenshot.
        viewport: Viewport dimensions as ``"WIDTHxHEIGHT"`` (default:
            ``"1920x1080"``). Both width and height must be positive integers.

    Returns:
        Dict with the following keys:

        - ``screenshot_path`` (str): Absolute path to the captured PNG file.
        - ``dimensions`` (dict[str, int]): Rendered image ``width`` and
          ``height`` in pixels.
        - ``format`` (str): Image format (always ``"png"``).
    """
    if not url.strip():
        raise ValueError("url must not be empty")

    # Validate and parse viewport string.
    parts = viewport.lower().split("x")
    if len(parts) != 2:
        raise ValueError(f"viewport must be 'WIDTHxHEIGHT'; got {viewport!r}")
    try:
        width, height = int(parts[0]), int(parts[1])
    except ValueError as err:
        raise ValueError(f"viewport dimensions must be integers; got {viewport!r}") from err
    if width <= 0 or height <= 0:
        raise ValueError(f"viewport dimensions must be positive; got {viewport!r}")

    parsed = urlparse(url)
    host = (parsed.netloc or "unknown").replace(".", "_")
    path_slug = (parsed.path.strip("/").replace("/", "_") or "index")[:40]
    timestamp_ms = int(time.time() * 1000)
    filename = f"screenshot_{host}_{path_slug}_{timestamp_ms}.png"
    screenshot_path = f"/tmp/browser_ai/screenshots/{filename}"

    return {
        "screenshot_path": screenshot_path,
        "dimensions": {"width": width, "height": height},
        "format": "png",
    }
