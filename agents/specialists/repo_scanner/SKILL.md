---
name: repo_scanner
description: Estimate a repository score from its owner/name string and optionally scaffold a local specialist directory. Use when exercising OSS Agent Lab's offline repo intake prototype. Trigger with scan repo prototype.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 1.1.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+, an OSS Agent Lab checkout installed with pip install -e ., and explicit approval before scaffolding; scan and score outputs are deterministic simulations with no GitHub API lookup.'
tags: [repository, scoring, scaffolding, simulation, filesystem]
argument-hint: '[owner/repo] [--name specialist_name]'
disable-model-invocation: true
model: inherit
effort: medium
display_name: "Repo Scanner"
source_repo: "jeremylongshore/oss-agent-lab"
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

A meta-specialist that exercises OSS Agent Lab's repository-intake shape. It derives a score from the
literal slug and can copy the local skeleton when the synthetic score crosses the threshold.

Wraps [jeremylongshore/oss-agent-lab](https://github.com/jeremylongshore/oss-agent-lab).

The scanner does not contact GitHub. Structure flags, scores, and recommendations are derived from the
repository string. Only scaffolding can write, by copying `_template` inside this checkout.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Provide a literal `owner/repo` slug and a safe snake_case target name.
- Obtain explicit user approval before a scaffold write and read
  [the runtime contract](references/runtime-contract.md).

## Capabilities

- **auto_scaffold**: Materialise a new specialist directory from the `_template`
  skeleton when a repo's composite score reaches >= 80.
- **repo_analysis**: Simulate structural flags and infer likely capabilities from repo naming.
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

## Instructions

1. Validate the literal `owner/repo` slug and run scan/score without claiming GitHub was queried.
2. Present the deterministic score, recommendation, proposed target path, and intended file set.
3. Ask for explicit approval before `scaffold_specialist` creates a directory.
4. After creation, report the exact path and files; the generated skeleton still requires review.

## Examples

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

### Output shape

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

## Output

Read-only operations return simulated structural signals and scores. Scaffolding returns `created`
only after copying the local template; if the template is absent it returns `simulated` and writes
nothing. Neither status proves that the source repository exists or is suitable.

## Error Handling

- Reject malformed repository slugs, unsafe names, and an existing target directory.
- Treat a missing template as no-write simulation, not successful creation.
- Never overwrite a specialist or broaden the destination beyond `agents/specialists/<name>`.

## Resources

Wraps [jeremylongshore/oss-agent-lab](https://github.com/jeremylongshore/oss-agent-lab).
See [the runtime contract](references/runtime-contract.md) for scoring and write boundaries.
