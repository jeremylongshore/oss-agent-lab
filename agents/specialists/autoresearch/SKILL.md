---
name: autoresearch
description: Generate deterministic prototype hypotheses, simulated experiment findings, and aggregate confidence summaries. Use when exercising an offline research-loop contract, not when collecting real evidence. Trigger with research prototype.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; current experiment findings are synthetic and use no external corpus or model.'
tags: [research, simulation, hypotheses, offline, prototype]
argument-hint: '[topic] [--method literature_review|simulation|ablation]'
model: inherit
effort: low
display_name: Autoresearch Specialist
source_repo: karpathy/autoresearch
tier: core
capabilities:
  - research
  - hypothesis_generation
  - experiment_design
  - result_analysis
allowed_tools:
  - run_experiment
  - analyze_results
  - generate_hypothesis
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Autoresearch Specialist

## Overview

Adapts the interface shape of [karpathy/autoresearch](https://github.com/karpathy/autoresearch) into
an OSS Agent Lab demonstration. Given a topic, the specialist formats three hypothesis templates,
selects a canned finding set, and summarizes its numeric strengths for contract testing.

The current implementation is a contract simulator: it uses fixed hypothesis templates and canned
finding sets. It does not search literature, run a model, execute an experiment, or establish facts.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Treat every finding and confidence value as synthetic test data.
- Read [the runtime contract](references/runtime-contract.md) for accepted methods and limitations.

## Capabilities

- **research**: End-to-end research loop for a given topic or question.
- **hypothesis_generation**: Produces multiple ranked, testable hypotheses with rationale.
- **experiment_design**: Selects and runs an experiment method (literature review, simulation, ablation).
- **result_analysis**: Aggregates findings into insights, a confidence score, and next steps.

## Tools

| Tool | Description | Side Effects |
|---|---|---|
| `generate_hypothesis` | Generates structured hypotheses for a topic | None |
| `run_experiment` | Simulates running an experiment for a hypothesis | None (v1 is local; future: network) |
| `analyze_results` | Analyzes experiment findings; returns insights and confidence score | None |

## Instructions

1. Extract a non-empty topic and choose `literature_review`, `simulation`, or `ablation`.
2. Run the specialist through the Python API or `oss-lab` CLI.
3. Label hypotheses, findings, and scores as simulated in any downstream response.
4. Reject requests that require sourced research; use a real research system instead.

## Examples

### Python API

```python
from agents.specialists.autoresearch.agent import AutoresearchSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = AutoresearchSpecialist()

request = SpecialistRequest(
    intent=Intent(action="research", domain="science", confidence=0.9),
    query=Query(user_input="effects of sleep deprivation on cognitive performance"),
    specialist_name="autoresearch",
)

result = await specialist.execute(request)
print(result.result["analysis"]["summary"])
```

### CLI

```bash
oss-lab run autoresearch "effects of sleep deprivation on cognitive performance"
```

### With method override

```python
request = SpecialistRequest(
    intent=Intent(
        action="research",
        domain="science",
        confidence=0.9,
        parameters={"method": "simulation"},
    ),
    query=Query(user_input="quantum error correction thresholds"),
    specialist_name="autoresearch",
)
```

## Output

```json
{
  "topic": "...",
  "hypotheses": [
    {"id": "h1", "text": "...", "confidence": 0.75, "rationale": "...", "testable": true}
  ],
  "recommended_hypothesis": "h1",
  "experiment": {"id": "abc12345", "method": "literature_review", "status": "completed"},
  "analysis": {
    "summary": "...",
    "key_insights": ["..."],
    "confidence_score": 0.575,
    "next_steps": ["..."]
  }
}
```

## Error Handling

- An unknown method falls back to the canned `literature_review` finding set; report the effective
  method and do not imply that sources were consulted.
- Empty findings produce zero confidence and a collect-data recommendation.
- Never convert the returned `corpus_scan` or `meta_analysis` labels into citations.

## Resources

Wraps [karpathy/autoresearch](https://github.com/karpathy/autoresearch).
See [the runtime contract](references/runtime-contract.md) for the implemented prototype boundary.
