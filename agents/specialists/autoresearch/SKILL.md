---
name: autoresearch
display_name: Autoresearch Specialist
description: Self-improving research loops with hypothesis generation, experiment design, and result analysis
version: 0.1.0
source_repo: karpathy/autoresearch
license: MIT
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

Wraps the [karpathy/autoresearch](https://github.com/karpathy/autoresearch) patterns to provide
self-improving research loops inside OSS Agent Lab. Given a topic or question, the specialist
generates falsifiable hypotheses, runs simulated experiments, and produces an evidence-backed
analysis with confidence scores and next-step recommendations — ready to iterate.

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

## Usage

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

## Response Shape

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

## Source

Wraps [karpathy/autoresearch](https://github.com/karpathy/autoresearch).
