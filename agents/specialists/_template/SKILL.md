---
name: template
display_name: Template Specialist
description: Replace with actual specialist description
version: 0.1.0
source_repo: owner/repo
license: MIT
tier: experimental
capabilities:
  - capability_1
  - capability_2
allowed_tools:
  - example_tool
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Template Specialist

## Overview

Replace with a description of what this specialist does and which source repo it wraps.

## Capabilities

- **capability_1**: Description of first capability
- **capability_2**: Description of second capability

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `example_tool` | Description | None |

## Usage

### Python API
```python
from agents.specialists.template.agent import TemplateSpecialist

specialist = TemplateSpecialist()
result = await specialist.execute(request)
```

### CLI
```bash
oss-lab run template "your query here"
```

## Source

Wraps [owner/repo](https://github.com/owner/repo).
