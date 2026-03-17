---
name: repo_scanner
display_name: "Repo Scanner"
description: "Meta-specialist that auto-discovers and scaffolds new specialists from trending GitHub repos"
version: "1.0.0"
source_repo: "jeremylongshore/oss-agent-lab"
license: "MIT"
tier: "core"
capabilities:
  - auto_scaffold
  - repo_analysis
  - specialist_generation
allowed_tools:
  - scan_repo
  - scaffold_specialist
  - evaluate_score
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Repo Scanner Specialist

## Overview

A meta-specialist that IS the OSS Agent Lab repository acting on itself. It
consumes the Capability Scoring Engine's signal pipeline to evaluate whether a
candidate GitHub repo is worth wrapping as a new specialist, then
auto-scaffolds the directory skeleton when the score crosses the threshold.

Wraps [jeremylongshore/oss-agent-lab](https://github.com/jeremylongshore/oss-agent-lab).

## Capabilities

- **auto_scaffold**: Materialise a new specialist directory from the `_template`
  skeleton when a repo's composite score reaches >= 80.
- **repo_analysis**: Analyse structural signals (Python presence, tests, README,
  licence) and infer likely capabilities from repo naming conventions.
- **specialist_generation**: Orchestrate the full scan → score → scaffold pipeline
  and surface a unified result with provenance metadata.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `scan_repo` | Structural analysis: name suggestion, detected capabilities, has_python/tests/readme, recommendation | None |
| `evaluate_score` | Composite capability score (0-100) with action and signal breakdown | None |
| `scaffold_specialist` | Copy `_template/` into `agents/specialists/<name>/` | Creates files on disk |

## Parameters

All parameters are passed via `request.intent.parameters`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo` | `str` | *(query text)* | GitHub repo in `owner/name` format |
| `name` | `str` | *(from scan)* | Override for the scaffolded specialist directory name |

## Usage

### Python API

```python
from agents.specialists.repo_scanner.agent import RepoScannerSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = RepoScannerSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="scan",
        domain="meta",
        confidence=0.95,
        parameters={"repo": "openai/swarm"},
    ),
    query=Query(user_input="openai/swarm"),
    specialist_name="repo_scanner",
)

response = await specialist.execute(request)
print(response.result["score"]["action"])   # "auto_scaffold" | "evaluate" | "watch" | "skip"
print(response.result.get("scaffold"))      # None or {"status": "created", "path": ..., "files": [...]}
```

### CLI

```bash
oss-lab run repo_scanner "openai/swarm"
```

### Response Shape

```json
{
  "repo": "openai/swarm",
  "scan": {
    "repo": "openai/swarm",
    "name_suggestion": "swarm",
    "capabilities_detected": ["agent_orchestration"],
    "has_python": true,
    "has_tests": true,
    "has_readme": true,
    "recommendation": "auto_scaffold"
  },
  "score": {
    "repo": "openai/swarm",
    "estimated_score": 87.04,
    "action": "auto_scaffold",
    "signals": {
      "discovery": 32.1,
      "quality": 28.5,
      "durability": 26.44,
      "github_star_velocity": 0.87,
      "readme_quality": 0.91,
      "test_coverage": 0.75,
      "maintenance_activity": 0.60,
      "community_depth": 0.44
    }
  },
  "scaffold": {
    "status": "created",
    "path": "/home/jeremy/000-projects/oss-agent-lab/agents/specialists/swarm",
    "files": ["__init__.py", "agent.py", "SKILL.md", "tools.py"]
  }
}
```

## Scoring Thresholds

| Score | Action | Description |
|-------|--------|-------------|
| >= 80 | `auto_scaffold` | Immediately scaffold specialist + flag for review |
| 60-79 | `evaluate` | Queue for human evaluation |
| 40-59 | `watch` | Add to watch list; re-score weekly |
| < 40  | `skip` | Not ready for wrapping |

## Source

Wraps [jeremylongshore/oss-agent-lab](https://github.com/jeremylongshore/oss-agent-lab).
