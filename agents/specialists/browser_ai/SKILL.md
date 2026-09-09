---
name: browser_ai
description: Simulate browser navigation metadata, selector extraction, and screenshot paths without network or file writes. Use when testing the Browser AI contract offline. Trigger with simulate browser or browser contract.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; this prototype does not launch Lightpanda, fetch URLs, parse a DOM, or create PNG files.'
tags: [browser, simulation, offline, automation, prototype]
argument-hint: '[URL] [--selector CSS] [--format text|html|markdown]'
model: inherit
effort: low
display_name: Browser AI Specialist
source_repo: lightpanda-io/browser
tier: core
capabilities:
  - browse
  - web_automation
  - scrape
  - screenshot
allowed_tools:
  - navigate
  - extract_content
  - take_screenshot
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Browser AI Specialist

## Overview

The Browser AI specialist mirrors part of the [lightpanda-io/browser](https://github.com/lightpanda-io/browser)
interface for offline contract tests. It composes synthetic navigation, extraction, and screenshot
metadata through one `execute()` call or standalone Python functions.

The current implementation is synthetic. It parses the URL string, derives deterministic metadata,
returns synthetic content, and constructs a PNG path without fetching a page or writing a file.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Supply an `http://` or `https://` URL; do not expect the target to be contacted.
- Read [the runtime contract](references/runtime-contract.md) before interpreting outputs.

## Capabilities

- **browse**: Validate an HTTP(S) URL string and synthesize redirect, status, title, and timing fields.
- **web_automation**: Exercise the three-stage result contract in one local request.
- **scrape**: Return format-shaped synthetic content for a small selector allowlist.
- **screenshot**: Validate a viewport and return an unwritten PNG path plus dimensions.

## Tools

| Tool | Description | Parameters | Side Effects |
|------|-------------|------------|--------------|
| `navigate` | Synthesize URL load metadata | `url`, `wait_for` | None |
| `extract_content` | Synthesize selector-shaped content | `url`, `selector`, `format` | None |
| `take_screenshot` | Construct PNG path metadata | `url`, `viewport` | None; no file is written |

### Tool Parameter Reference

**`navigate`**
- `url: str` — fully-qualified URL to load (required)
- `wait_for: str | None` — CSS selector or browser event to await before page-ready
  (default: `None`, waits for `DOMContentLoaded`)

**`extract_content`**
- `url: str` — URL of the page to extract from (required)
- `selector: str` — CSS selector targeting the element(s) to extract (default: `"body"`)
- `format: str` — output format: `"text"` | `"html"` | `"markdown"` (default: `"text"`)

**`take_screenshot`**
- `url: str` — URL of the page to screenshot (required)
- `viewport: str` — viewport size as `"WIDTHxHEIGHT"` (default: `"1920x1080"`)

## Pipeline Flow

```
SpecialistRequest
      │
      ▼
  simulate navigate(url, wait_for)
      │  → status_code, title, final_url, load_time_ms
      ▼
  simulate extract_content(final_url, selector, format)
      │  → content, selector_matched, element_count
      ▼
  simulate take_screenshot(final_url, viewport)
      │  → screenshot_path, dimensions, format
      ▼
  SpecialistResponse(result={url, navigation, extraction, screenshot})
```

## Instructions

1. Validate that the input is a fully qualified HTTP(S) URL.
2. Choose a supported selector, output format, and positive `WIDTHxHEIGHT` viewport.
3. Run the specialist or an individual tool through the local Python package.
4. Report all page, content, timing, status, and screenshot values as synthetic fixtures.

## Examples

### Python API

```python
from agents.specialists.browser_ai.agent import BrowserAiSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = BrowserAiSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="scrape",
        domain="web_automation",
        confidence=0.95,
        parameters={
            "url": "https://github.com/lightpanda-io/browser",
            "selector": "article",
            "format": "markdown",
            "viewport": "1280x800",
        },
    ),
    query=Query(user_input="https://github.com/lightpanda-io/browser"),
    specialist_name="browser_ai",
)

response = await specialist.execute(request)
print(response.result["extraction"]["content"])
print(response.result["screenshot"]["screenshot_path"])
```

### CLI

```bash
oss-lab run browser_ai "https://github.com/lightpanda-io/browser"
```

### Navigation only

```python
from agents.specialists.browser_ai.tools import navigate

result = navigate("https://example.com", wait_for="#main-content")
print(result["title"], result["load_time_ms"])
```

### Content extraction standalone

```python
from agents.specialists.browser_ai.tools import extract_content

result = extract_content(
    url="https://example.com",
    selector="article",
    format="markdown",
)
print(result["content"])
```

### Screenshot standalone

```python
from agents.specialists.browser_ai.tools import take_screenshot

result = take_screenshot(url="https://example.com", viewport="1280x800")
print(result["screenshot_path"])
```

## Output

The specialist returns `navigation`, `extraction`, and `screenshot` dictionaries. The screenshot path
is metadata only: no PNG is created. A selector outside the small built-in allowlist returns zero
matches, regardless of the real page.

## Error Handling

- Reject empty URLs, non-HTTP(S) schemes, unsupported content formats, and malformed viewports.
- Treat a returned 200 or 404 as string-derived simulation, not an observed HTTP response.
- Do not retry or troubleshoot network access because this implementation performs none.

## Resources

Wraps [lightpanda-io/browser](https://github.com/lightpanda-io/browser) — a fast, memory-efficient
headless browser written in Zig, designed to serve AI agent workloads with low overhead and a
clean programmatic API.

The local specialist is inspired by that interface but does not embed Lightpanda. See
[the runtime contract](references/runtime-contract.md).
