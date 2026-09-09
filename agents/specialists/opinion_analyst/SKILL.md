---
name: opinion_analyst
description: Score supplied text with deterministic keyword heuristics for sentiment, stance, and bias. Use when testing explainable offline classification behavior, not for population-level opinion claims. Trigger with analyze text heuristically.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; the implementation uses local lexicons and rules, not BettaFish models, surveys, social feeds, or external APIs.'
tags: [sentiment, stance, bias, heuristics, offline]
argument-hint: '[text] [--target SUBJECT]'
model: inherit
effort: low
display_name: Opinion Analyst
source_repo: 666ghj/BettaFish
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

OpinionAnalyst mirrors three interface concepts from
[666ghj/BettaFish](https://github.com/666ghj/BettaFish): sentiment, stance, and bias records. The local
specialist computes them from small fixed phrase lists.

The implementation is an offline keyword-and-rule heuristic. It does not run BettaFish models, ingest
social or survey data, infer population opinion, or establish a person's beliefs or protected traits.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Provide text the user is authorized to analyze and avoid identity or high-stakes profiling.
- Read [the runtime contract](references/runtime-contract.md) for heuristic limits and outputs.

## Capabilities

- **sentiment**: Count fixed positive/negative terms and optionally label three known aspects.
- **opinion_analysis**: Exercise a structured local classification response.
- **stance_detection**: Match fixed support/opposition phrases, then fall back to sentiment.
- **bias_measurement**: Count fixed political, emotional, framing, source, and confirmation phrases.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `analyze_sentiment` | Score sentiment (positive/negative/neutral) with confidence and aspects | None |
| `detect_stance` | Classify stance (support/oppose/neutral) toward a target | None |
| `measure_bias` | Score bias across configurable dimensions, return flags | None |

## Instructions

1. Choose sentiment, stance, or bias analysis and supply the required text and target/dimensions.
2. Run the local Python API or CLI.
3. Report the returned label as a heuristic signal with its score and matched evidence count.
4. Do not generalize one text sample to a person, group, electorate, or public population.

## Examples

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

## Output

Sentiment returns a label, confidence, aspects, and score; stance returns support/oppose/neutral plus
reasoning; bias returns requested dimension scores and flags. Values reflect built-in lexicons only.

## Error Handling

- Empty inputs return neutral/zero-information results; do not interpret them as measured neutrality.
- An unknown bias dimension is scored with the tool's fallback behavior; disclose the limitation.
- Refuse discriminatory profiling, diagnosis, or consequential decisions based on heuristic output.

## Resources

Wraps [666ghj/BettaFish](https://github.com/666ghj/BettaFish).
The local code is inspired by the domain but does not embed BettaFish. See
[the runtime contract](references/runtime-contract.md).
