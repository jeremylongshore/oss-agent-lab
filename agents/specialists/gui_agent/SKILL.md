---
name: gui_agent
description: Simulate element detection, UI actions, and form-validation results without opening a browser or changing a page. Use when exercising the GUI Agent contract offline. Trigger with simulate GUI or page-agent prototype.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; current tools synthesize page elements and interaction results and perform no browser or network I/O.'
tags: [gui, browser, simulation, forms, prototype]
argument-hint: '[instruction] [--url URL]'
model: inherit
effort: low
display_name: GUI Agent Specialist
source_repo: alibaba/page-agent
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

The GUI Agent specialist mirrors a small portion of the
[alibaba/page-agent](https://github.com/alibaba/page-agent) interface for local contract tests. Given
an instruction and URL string, it generates login-form fixtures, returns an action-state record, and
applies simple validation tokens to supplied form data.

The current implementation never opens the URL. It returns a built-in element catalogue, synthetic
interaction state, and rule-based form validation without changing any browser or remote page.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Provide test-only values; do not put real passwords, tokens, or personal data in form inputs.
- Read [the runtime contract](references/runtime-contract.md) for synthetic behavior and limits.

## Authentication

None. The current implementation does not contact a page or service. Do not enter live credentials;
form values are echoed into synthetic state and are suitable only for non-sensitive test data.

## Capabilities

- **gui_automation**: Exercise the detection/action/form response pipeline with fixture data.
- **web_interaction**: Map click, type, hover, focus, or clear to synthetic state.
- **element_detection**: Filter a built-in element catalogue using description words.
- **form_filling**: Apply local field rules and return a synthetic readiness flag.

## Tools

| Tool | Description | Parameters | Side Effects |
|------|-------------|------------|--------------|
| `detect_elements` | Generate and filter login-form fixtures | `url`, `description` | None |
| `interact_element` | Return a synthetic action state for an element ID | `element_id`, `action`, `value` | None |
| `fill_form` | Apply local validation rules to field-value pairs | `url`, `form_data` | None |

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

## Instructions

1. Provide a URL string and a narrow natural-language element description.
2. Call detection before interaction and use only the returned synthetic element ID.
3. Use form filling only with non-sensitive test data.
4. Report all elements, actions, timings, and readiness fields as simulated results.

## Examples

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

## Output

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

## Error Handling

- Reject empty URL or element ID values and unsupported actions.
- Require `value` for `type`; report form validation errors without claiming a remote form changed.
- Do not retry network or browser operations because none occur.

## Resources

Wraps [alibaba/page-agent](https://github.com/alibaba/page-agent) — a natural-language
web UI control agent that translates plain-English instructions into browser automation
actions using vision-language models and structured element grounding.

The local specialist is a simulator, not an embedded page-agent runtime. See
[the runtime contract](references/runtime-contract.md).
