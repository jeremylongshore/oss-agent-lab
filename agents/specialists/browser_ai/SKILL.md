---
name: browser_ai
display_name: Browser AI Specialist
description: Headless web automation for AI — navigate pages, extract DOM content, and capture screenshots
version: 0.1.0
source_repo: lightpanda-io/browser
license: MIT
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

The Browser AI specialist wraps [lightpanda-io/browser](https://github.com/lightpanda-io/browser)
— a lightweight, Zig-written headless browser engine built specifically for AI agent workloads.
It provides a composable pipeline for web navigation, DOM content extraction, and screenshot
capture, all accessible through a single `execute()` call or as standalone tool functions.

## Capabilities

- **browse**: Load any HTTP/HTTPS URL in a headless browser context, following redirects and
  capturing page-ready timing.
- **web_automation**: Drive the full browser pipeline — navigate, extract, screenshot — in a
  single request with configurable parameters.
- **scrape**: Extract structured content from the rendered DOM using CSS selectors. Supports
  plain text, raw HTML, and Markdown output formats.
- **screenshot**: Capture a PNG screenshot of the fully-rendered page at an arbitrary viewport
  size. Returns the file path and image dimensions.

## Tools

| Tool | Description | Parameters | Side Effects |
|------|-------------|------------|--------------|
| `navigate` | Load a URL and return load metadata | `url`, `wait_for` | None |
| `extract_content` | Extract DOM content via CSS selector | `url`, `selector`, `format` | None |
| `take_screenshot` | Capture a PNG of the rendered page | `url`, `viewport` | Writes PNG to `/tmp/browser_ai/screenshots/` |

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
  navigate(url, wait_for)
      │  → status_code, title, final_url, load_time_ms
      ▼
  extract_content(final_url, selector, format)
      │  → content, selector_matched, element_count
      ▼
  take_screenshot(final_url, viewport)
      │  → screenshot_path, dimensions, format
      ▼
  SpecialistResponse(result={url, navigation, extraction, screenshot})
```

## Usage

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

## Source

Wraps [lightpanda-io/browser](https://github.com/lightpanda-io/browser) — a fast, memory-efficient
headless browser written in Zig, designed to serve AI agent workloads with low overhead and a
clean programmatic API.
