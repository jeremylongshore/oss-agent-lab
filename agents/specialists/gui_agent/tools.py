"""
Tools for the GUI Agent specialist.

Implements element detection, element interaction, and form-filling capabilities
inspired by the alibaba/page-agent natural-language web UI control pattern. Each
tool is a pure function that can be composed into a full web-automation pipeline
or called independently.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


def detect_elements(url: str, description: str | None = None) -> dict[str, Any]:
    """Detect interactive UI elements on a web page.

    Simulates the page-agent element detection stage: navigates to the given URL,
    applies optional natural-language filtering, and returns a structured list of
    detected elements with their types, visible text, and CSS selectors.

    Args:
        url: The fully-qualified URL of the page to inspect.
        description: Optional natural-language hint used to narrow detection to
            elements matching a semantic description (e.g. "login button",
            "email field"). When None all interactive elements are returned.

    Returns:
        Dict with the following keys:
            elements (list[dict[str, Any]]): Detected elements, each containing:
                - id (str): Stable element identifier.
                - type (str): Element category (e.g. "button", "input", "link").
                - text (str): Visible label or placeholder text.
                - selector (str): CSS selector for programmatic targeting.
            page_title (str): Document title of the inspected page.
            element_count (int): Total number of elements returned.
    """
    if not url.strip():
        raise ValueError("url must not be empty")

    # Simulate a page-specific element catalogue keyed by URL keyword.
    domain = url.split("/")[2] if "//" in url else url
    slug = description.lower().replace(" ", "_") if description else "all"

    base_elements: list[dict[str, Any]] = [
        {
            "id": f"elem-{uuid.uuid4().hex[:8]}",
            "type": "input",
            "text": "Email address",
            "selector": "input[type='email']",
        },
        {
            "id": f"elem-{uuid.uuid4().hex[:8]}",
            "type": "input",
            "text": "Password",
            "selector": "input[type='password']",
        },
        {
            "id": f"elem-{uuid.uuid4().hex[:8]}",
            "type": "button",
            "text": "Sign in",
            "selector": "button[type='submit']",
        },
        {
            "id": f"elem-{uuid.uuid4().hex[:8]}",
            "type": "link",
            "text": "Forgot password?",
            "selector": "a.forgot-password",
        },
        {
            "id": f"elem-{uuid.uuid4().hex[:8]}",
            "type": "checkbox",
            "text": "Remember me",
            "selector": "input[type='checkbox']#remember",
        },
    ]

    # Apply description-based filtering when a hint is provided.
    if description:
        keywords = description.lower().split()
        filtered = [
            el
            for el in base_elements
            if any(kw in el["text"].lower() or kw in el["type"].lower() for kw in keywords)
        ]
        elements = filtered if filtered else base_elements[:2]
    else:
        elements = base_elements

    return {
        "elements": elements,
        "page_title": f"Page at {domain} — detected via page-agent ({slug})",
        "element_count": len(elements),
    }


def interact_element(
    element_id: str,
    action: str = "click",
    value: str | None = None,
) -> dict[str, Any]:
    """Interact with a detected UI element.

    Simulates the page-agent interaction stage: performs a specified action
    (click, type, hover, focus, or clear) on an element identified by its stable
    ID and returns the resulting element state.

    Args:
        element_id: The stable element identifier returned by ``detect_elements``.
        action: The interaction to perform. Supported values: ``"click"``,
            ``"type"``, ``"hover"``, ``"focus"``, ``"clear"``.
            Defaults to ``"click"``.
        value: The text to type when ``action="type"``. Ignored for all other
            actions. Must be provided when ``action="type"``.

    Returns:
        Dict with the following keys:
            success (bool): Whether the interaction completed without error.
            action_performed (str): Echo of the action that was executed.
            element_state (str): Post-interaction state of the element
                (e.g. "clicked", "focused", "filled", "hovered", "cleared").
            response_time_ms (float): Simulated round-trip time in milliseconds.

    Raises:
        ValueError: If ``action`` is not a supported value, or if ``action``
            is ``"type"`` but ``value`` is not provided.
    """
    supported_actions = {"click", "type", "hover", "focus", "clear"}
    if action not in supported_actions:
        raise ValueError(f"action must be one of {sorted(supported_actions)!r}; got {action!r}")
    if action == "type" and not value:
        raise ValueError("value must be provided when action is 'type'")
    if not element_id.strip():
        raise ValueError("element_id must not be empty")

    state_map: dict[str, str] = {
        "click": "clicked",
        "type": "filled",
        "hover": "hovered",
        "focus": "focused",
        "clear": "cleared",
    }
    element_state = state_map[action]
    if action == "type" and value:
        element_state = f"filled with {value!r}"

    # Simulate a realistic latency range based on action type.
    latency_ms: dict[str, float] = {
        "click": 42.5,
        "type": 18.3 + (len(value) * 0.8 if value else 0.0),
        "hover": 12.1,
        "focus": 9.7,
        "clear": 15.4,
    }
    response_time_ms = round(latency_ms.get(action, 20.0), 2)

    return {
        "success": True,
        "action_performed": action,
        "element_state": element_state,
        "response_time_ms": response_time_ms,
    }


def fill_form(url: str, form_data: dict[str, str]) -> dict[str, Any]:
    """Fill a web form with the provided field values.

    Simulates the page-agent form-filling stage: navigates to the target URL,
    maps natural-language field names to detected elements, populates each field,
    and reports the outcome with any validation errors.

    Args:
        url: The fully-qualified URL of the page hosting the form.
        form_data: Mapping of field labels or semantic names to the values to
            enter (e.g. ``{"email": "user@example.com", "password": "s3cr3t"}``).

    Returns:
        Dict with the following keys:
            fields_filled (int): Number of fields successfully populated.
            success (bool): True when all fields were filled without validation
                errors; False otherwise.
            validation_errors (list[str]): Descriptions of any validation
                failures encountered (empty list when all fields pass).
            submit_ready (bool): Whether the form is in a submittable state
                (True when ``success`` is True and no errors are present).

    Raises:
        ValueError: If ``url`` is empty or ``form_data`` is empty.
    """
    if not url.strip():
        raise ValueError("url must not be empty")
    if not form_data:
        raise ValueError("form_data must not be empty")

    validation_rules: dict[str, str] = {
        "email": "@",
        "url": "http",
        "phone": "",
    }

    validation_errors: list[str] = []
    fields_filled = 0

    for field_name, field_value in form_data.items():
        # Simulate per-field fill latency (not blocking in real impl).
        time.sleep(0)  # placeholder for async fill call

        key = field_name.lower()
        rule_token = validation_rules.get(key)

        if rule_token and rule_token not in field_value:
            validation_errors.append(
                f"Field '{field_name}': value {field_value!r} failed validation "
                f"(expected to contain {rule_token!r})."
            )
        else:
            fields_filled += 1

    success = len(validation_errors) == 0

    return {
        "fields_filled": fields_filled,
        "success": success,
        "validation_errors": validation_errors,
        "submit_ready": success,
    }
