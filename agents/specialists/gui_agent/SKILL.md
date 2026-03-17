---
name: gui_agent
display_name: GUI Agent Specialist
description: Natural language web UI control — element detection, targeted interaction, and automated form filling
version: 0.1.0
source_repo: alibaba/page-agent
license: Apache-2.0
tier: core
capabilities:
  - gui_automation
  - web_interaction
  - element_detection
  - form_filling
allowed_tools:
  - detect_elements
  - interact_element
  - fill_form
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# GUI Agent Specialist

## Overview

The GUI Agent specialist wraps the [alibaba/page-agent](https://github.com/alibaba/page-agent)
natural-language web UI control framework into a composable OSS Agent Lab specialist. Given a
plain-English instruction and a target URL, it:

1. **Detects elements** — discovers interactive UI elements on the page, optionally narrowed by
   a semantic description of the target.
2. **Interacts** — performs the requested action (click, type, hover, focus, or clear) on the
   matched element.
3. **Fills forms** — when form data is provided, populates every field, validates values, and
   reports whether the form is ready to submit.

Each stage is independently callable as a tool, making the specialist suitable for targeted
automation steps as well as full end-to-end web-interaction pipelines.

## Capabilities

- **gui_automation**: End-to-end pipeline that detects elements and performs actions from a
  natural-language description.
- **web_interaction**: Single-element actions (click, type, hover, focus, clear) driven by
  element ID.
- **element_detection**: Structured discovery of interactive elements on any URL, with optional
  semantic filtering.
- **form_filling**: Batch field population with built-in validation and submit-readiness reporting.

## Tools

| Tool | Description | Parameters | Side Effects |
|------|-------------|------------|--------------|
| `detect_elements` | Detect interactive UI elements on a page | `url`, `description` | None (read-only) |
| `interact_element` | Perform an action on a specific element | `element_id`, `action`, `value` | Modifies page state |
| `fill_form` | Fill a web form with field-value pairs | `url`, `form_data` | Modifies page state |

### Tool Parameter Reference

**`detect_elements`**
- `url: str` — fully-qualified URL of the target page (required)
- `description: str | None` — semantic hint to filter detected elements (default: `None`)

**`interact_element`**
- `element_id: str` — stable element ID from `detect_elements` (required)
- `action: str` — `"click"` | `"type"` | `"hover"` | `"focus"` | `"clear"` (default: `"click"`)
- `value: str | None` — text to type; required when `action="type"` (default: `None`)

**`fill_form`**
- `url: str` — fully-qualified URL of the page hosting the form (required)
- `form_data: dict[str, str]` — mapping of field labels to values (required)

## Pipeline Flow

```
SpecialistRequest
       │
       ▼
  detect_elements(url, description)
       │
       ▼
  interact_element(element_id, action, value?)
       │
       ▼  (when form_data in parameters)
  fill_form(url, form_data)
       │
       ▼
  SpecialistResponse(result={detection, interaction, form?})
```

Form filling is triggered when the `form_data` key is present and non-empty in
`request.intent.parameters`.

## Usage

### Python API

```python
from agents.specialists.gui_agent.agent import GuiAgentSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = GuiAgentSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="click",
        domain="web_interaction",
        confidence=0.95,
        parameters={"url": "https://example.com/login", "description": "sign in button"},
    ),
    query=Query(user_input="click the sign in button"),
    specialist_name="gui_agent",
)

response = await specialist.execute(request)
print(response.result["interaction"]["element_state"])
```

### CLI

```bash
oss-lab run gui_agent "click the sign in button on https://example.com/login"
```

### Form filling

```python
request = SpecialistRequest(
    intent=Intent(
        action="fill_form",
        domain="gui_automation",
        confidence=0.90,
        parameters={
            "url": "https://example.com/signup",
            "form_data": {"email": "user@example.com", "password": "s3cr3t"},
        },
    ),
    query=Query(user_input="fill the signup form"),
    specialist_name="gui_agent",
)

response = await specialist.execute(request)
print(response.result["form"]["submit_ready"])
```

### Element detection standalone

```python
from agents.specialists.gui_agent.tools import detect_elements

result = detect_elements(
    url="https://example.com/login",
    description="email field",
)
print(result["elements"])
print(f"Found {result['element_count']} element(s)")
```

## Response Shape

```json
{
  "url": "https://example.com/login",
  "description": "sign in button",
  "detection": {
    "elements": [
      {"id": "elem-a1b2c3d4", "type": "button", "text": "Sign in", "selector": "button[type='submit']"}
    ],
    "page_title": "Page at example.com — detected via page-agent (sign_in_button)",
    "element_count": 1
  },
  "interaction": {
    "success": true,
    "action_performed": "click",
    "element_state": "clicked",
    "response_time_ms": 42.5
  },
  "form": {
    "fields_filled": 2,
    "success": true,
    "validation_errors": [],
    "submit_ready": true
  }
}
```

## Source

Wraps [alibaba/page-agent](https://github.com/alibaba/page-agent) — a natural-language
web UI control agent that translates plain-English instructions into browser automation
actions using vision-language models and structured element grounding.
