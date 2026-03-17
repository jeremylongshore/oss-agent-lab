---
name: opinion_analyst
display_name: Opinion Analyst
description: >
  Public opinion analysis and sentiment at scale — sentiment scoring,
  stance detection, and multi-dimensional bias measurement.
version: 0.1.0
source_repo: 666ghj/BettaFish
license: MIT
tier: experimental
capabilities:
  - sentiment
  - opinion_analysis
  - stance_detection
  - bias_measurement
allowed_tools:
  - analyze_sentiment
  - detect_stance
  - measure_bias
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Opinion Analyst

## Overview

OpinionAnalyst wraps [666ghj/BettaFish](https://github.com/666ghj/BettaFish), a
public-opinion analysis library built for high-throughput sentiment mining.  The
specialist surfaces three core capabilities — sentiment scoring, stance detection,
and bias measurement — as callable tools within the OSS Agent Lab pipeline.

## Capabilities

- **sentiment**: Document-, sentence-, and aspect-level sentiment scoring with a
  continuous score in `[-1.0, 1.0]`.
- **opinion_analysis**: Holistic opinion mining that combines sentiment with
  aspect extraction for nuanced understanding.
- **stance_detection**: Determines whether the author supports, opposes, or is
  neutral toward a named entity or claim.
- **bias_measurement**: Measures political, emotional, framing, source-attribution,
  and confirmation bias; returns per-dimension scores and human-readable flags.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `analyze_sentiment` | Score sentiment (positive/negative/neutral) with confidence and aspects | None |
| `detect_stance` | Classify stance (support/oppose/neutral) toward a target | None |
| `measure_bias` | Score bias across configurable dimensions, return flags | None |

## Usage

### Python API

```python
import asyncio
from agents.specialists.opinion_analyst.agent import OpinionAnalystSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = OpinionAnalystSpecialist()

request = SpecialistRequest(
    intent=Intent(action="sentiment", domain="opinion", confidence=0.9),
    query=Query(user_input="The new policy is an outstanding step forward."),
    specialist_name="opinion_analyst",
)

result = asyncio.run(specialist.execute(request))
print(result.result)
# {'sentiment': {'sentiment': 'positive', 'confidence': 0.65,
#                'aspects': [], 'overall_score': 0.2}}
```

### Stance Detection

```python
request = SpecialistRequest(
    intent=Intent(
        action="stance",
        domain="opinion",
        confidence=0.9,
        parameters={"target": "climate policy"},
    ),
    query=Query(user_input="I strongly support climate policy reforms."),
    specialist_name="opinion_analyst",
    tools_requested=["detect_stance"],
)
result = asyncio.run(specialist.execute(request))
```

### Bias Measurement

```python
request = SpecialistRequest(
    intent=Intent(
        action="bias",
        domain="opinion",
        confidence=0.9,
        parameters={"dimensions": ["political", "emotional"]},
    ),
    query=Query(user_input="The radical left regime is destroying our nation!"),
    specialist_name="opinion_analyst",
    tools_requested=["measure_bias"],
)
result = asyncio.run(specialist.execute(request))
```

### CLI

```bash
oss-lab run opinion_analyst "The product quality is excellent and worth every penny."
```

## Source

Wraps [666ghj/BettaFish](https://github.com/666ghj/BettaFish).
