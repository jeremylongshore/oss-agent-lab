---
name: swarm_predict
display_name: Swarm Prediction Specialist
description: Ensemble predictions via swarm intelligence with multi-model voting and consensus
version: 0.1.0
source_repo: 666ghj/MiroFish
license: MIT
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

`swarm_predict` wraps the swarm intelligence prediction patterns from
[666ghj/MiroFish](https://github.com/666ghj/MiroFish).  Rather than relying
on a single model, it spins up a configurable swarm of independent model
agents, collects their individual predictions, and resolves a consensus
through weighted aggregation and agreement scoring.

The specialist is fully stateless — each request spawns a fresh swarm and
returns a self-contained result dict.  It supports numeric and categorical
prediction targets and exposes three aggregation strategies: weighted vote,
majority vote, and simple mean.

## Capabilities

- **predict**: Route any prediction target through the swarm pipeline and
  receive a consensus value with confidence score.
- **ensemble**: Combine outputs from N independent model agents (default 5)
  to reduce variance and single-model bias.
- **swarm_intelligence**: Each agent operates independently before results
  are merged, mirroring biological swarm behaviour.
- **consensus**: Agreement ratio and blended confidence score surface when
  models agree strongly enough to act on the prediction.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `create_prediction_swarm` | Initialise N model agents for a given target | None |
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

## Response shape

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

## Usage

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

## Source

Wraps [666ghj/MiroFish](https://github.com/666ghj/MiroFish).
