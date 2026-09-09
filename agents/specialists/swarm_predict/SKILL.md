---
name: swarm_predict
description: Generate synthetic per-model values and exercise numeric or categorical consensus aggregation. Use when testing the Swarm Prediction contract, not when forecasting real events. Trigger with simulate swarm prediction.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; no models or external data sources are called, and generated values are not forecasts.'
tags: [ensemble, consensus, simulation, prediction, offline]
argument-hint: '[target] [--num-models N] [--method weighted_vote|majority_vote|mean]'
model: inherit
effort: low
display_name: Swarm Prediction Specialist
source_repo: 666ghj/MiroFish
tier: core
capabilities:
  - predict
  - ensemble
  - swarm_intelligence
  - consensus
allowed_tools:
  - create_prediction_swarm
  - aggregate_predictions
  - evaluate_consensus
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Swarm Prediction Specialist

## Overview

`swarm_predict` mirrors aggregation patterns from
[666ghj/MiroFish](https://github.com/666ghj/MiroFish). It creates configurable virtual model
descriptors, generates numeric fixture values from the target string, and resolves an arithmetic
consensus through weighted aggregation and agreement scoring.

The specialist is stateless and returns a self-contained result dict. The standalone aggregation tool
also supports caller-supplied numeric or categorical values through weighted vote, majority vote, or
simple mean.

The current end-to-end specialist does not call any model. It generates target-derived numeric fixture
values, then exercises the real aggregation functions. Its result is not a forecast.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Provide a test target, a positive swarm size, and a threshold between 0 and 1.
- Read [the runtime contract](references/runtime-contract.md) for aggregation semantics.

## Capabilities

- **predict**: Derive numeric fixture values from a target and aggregate them.
- **ensemble**: Combine N synthetic or caller-supplied values.
- **swarm_intelligence**: Exercise virtual model descriptors without model execution.
- **consensus**: Compute an agreement ratio and blended arithmetic confidence.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `create_prediction_swarm` | Initialise N virtual model descriptors | None |
| `aggregate_predictions` | Merge individual predictions via weighted/majority/mean vote | None |
| `evaluate_consensus` | Score agreement ratio and emit a recommendation | None |

## Parameters

### Request-level (`intent.parameters`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `target` | `str` | *(query.user_input)* | Prediction target; falls back to the raw user query |
| `num_models` | `int` | `5` | Swarm size |
| `method` | `str` | `"weighted_vote"` | Aggregation strategy: `weighted_vote`, `majority_vote`, `mean` |
| `threshold` | `float` | `0.7` | Minimum agreement ratio for consensus to be declared |

### Aggregation methods

- **weighted_vote** — weighted average using each model's confidence as its
  weight.  Preferred for numeric targets where confidence is informative.
- **majority_vote** — discrete winner-takes-all; numeric values are averaged
  as a fallback.  Suited for classification targets.
- **mean** — unweighted average.  Baseline; useful for ablation.

## Output

```python
{
    "target": str,
    "predictions": list[dict],      # individual model outputs
    "consensus": float | str,       # aggregated prediction
    "confidence": float,            # blended confidence score 0-1
    "recommendation": str,          # "high_confidence_proceed" | "moderate_confidence_review" | "low_confidence_abstain"
    "swarm_id": str,                # UUID for this swarm instance
}
```

## Instructions

1. Choose a target, swarm size, aggregation method, and consensus threshold.
2. Run the specialist for synthetic numeric fixtures, or call aggregation with caller-supplied values.
3. Report agreement and confidence as arithmetic over inputs, not calibrated predictive accuracy.
4. Do not use the recommendation for financial, medical, safety, or other consequential decisions.

## Examples

### Python API

```python
import asyncio
from agents.specialists.swarm_predict.agent import SwarmPredictSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = SwarmPredictSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="predict",
        domain="swarm_intelligence",
        confidence=0.9,
        parameters={"target": "BTC/USD price in 24h", "num_models": 7},
    ),
    query=Query(user_input="BTC/USD price in 24h"),
    specialist_name="swarm_predict",
)

response = asyncio.run(specialist.execute(request))
print(response.result["consensus"], response.result["recommendation"])
```

### CLI

```bash
oss-lab run swarm_predict "BTC/USD price in 24h"
```

### With custom parameters

```bash
oss-lab run swarm_predict "next quarter revenue" \
  --param num_models=10 \
  --param method=majority_vote \
  --param threshold=0.8
```

## Error Handling

- Reject a swarm smaller than one, an empty prediction list, unknown method, or invalid threshold.
- Validate caller-supplied prediction provenance before interpreting a consensus.
- Treat `high_confidence_proceed` as a test label, not authorization to act.

## Resources

Wraps [666ghj/MiroFish](https://github.com/666ghj/MiroFish).
The local implementation only exercises virtual descriptors and aggregation. See
[the runtime contract](references/runtime-contract.md).
