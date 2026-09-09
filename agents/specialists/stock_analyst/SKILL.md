---
name: stock_analyst
description: Generate deterministic synthetic fundamentals, indicators, and news sentiment from a ticker string. Use when testing the Stock Analyst response contract, never for an investment decision. Trigger with simulate stock analysis.
allowed-tools: 'Bash(python:*), Bash(oss-lab:*)'
version: 0.2.0
author: Intent Solutions <jeremy@intentsolutions.io>
license: MIT
compatibility: 'Requires Python 3.11+ and an OSS Agent Lab checkout installed with pip install -e .; it fetches no prices, filings, fundamentals, or news and must not be treated as financial advice.'
tags: [stocks, finance, simulation, offline, testing]
argument-hint: '[TICKER] [--period 1m|3m|6m|1y|3y|5y]'
model: inherit
effort: low
display_name: Stock Analyst Specialist
source_repo: virattt/ai-hedge-fund
tier: experimental
capabilities:
  - analyze
  - finance
  - stock_analysis
  - technical_analysis
allowed_tools:
  - analyze_ticker
  - technical_indicators
  - news_sentiment
output_formats:
  - python_api
  - cli
  - mcp_server
  - agent_skill
  - rest_api
---

# Stock Analyst Specialist

## Overview

Wraps [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) and
[ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis).

Orchestrates a three-stage fixture pipeline for a requested ticker string: synthetic fundamentals,
synthetic technical indicators, and synthetic news sentiment. The layers are merged into a structured
response with a demonstration stance signal.

No market data is loaded. Every price, ratio, indicator, article count, theme, and stance is generated
deterministically from the ticker string and is unsuitable for trading or valuation.

## Prerequisites

- Use Python 3.11+ in a local OSS Agent Lab checkout and run `pip install -e .`.
- Use a valid test ticker and treat the response strictly as fixture data.
- Read [the runtime contract](references/runtime-contract.md) for supported bounds and disclaimers.

## Capabilities

- **analyze**: Exercise the full synthetic pipeline for a ticker and period label.
- **finance**: Return a finance-shaped fixture for integration tests.
- **stock_analysis**: Generate price, market cap, P/E, sector, and recommendation fixtures.
- **technical_analysis**: Generate RSI, MACD, moving-average, and signal fixtures.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `analyze_ticker` | Generate synthetic fundamental fields | None |
| `technical_indicators` | Generate synthetic indicator fields | None |
| `news_sentiment` | Generate synthetic sentiment, count, and theme fields | None |

## Parameters

All parameters are passed via `request.intent.parameters`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ticker` | `str` | *(query text)* | Stock ticker symbol, e.g. `AAPL` |
| `period` | `str` | `"1y"` | Lookback period: `1m`, `3m`, `6m`, `1y`, `3y`, `5y` |
| `indicators` | `list[str]` | all | Subset of `rsi`, `macd`, `moving_averages` |
| `days` | `int` | `7` | News lookback window in calendar days |

## Instructions

1. Normalize a non-empty ticker and choose a supported period, indicator subset, and day count.
2. Run the local Python API or CLI.
3. Label all values and recommendations as synthetic test output.
4. For real analysis, obtain timestamped data from an authoritative provider and use qualified advice.

## Examples

### Python API

```python
from agents.specialists.stock_analyst.agent import StockAnalystSpecialist
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest

specialist = StockAnalystSpecialist()

request = SpecialistRequest(
    intent=Intent(
        action="analyze",
        domain="finance",
        confidence=0.95,
        parameters={"ticker": "AAPL", "period": "1y", "days": 14},
    ),
    query=Query(user_input="AAPL"),
    specialist_name="stock_analyst",
)

response = await specialist.execute(request)
print(response.result["summary"]["overall_stance"])  # "bullish" | "neutral" | "bearish"
```

### CLI

```bash
oss-lab run stock_analyst "AAPL"
```

### Output shape

```json
{
  "ticker": "AAPL",
  "fundamental": {
    "price": 182.0,
    "market_cap": 295.4,
    "pe_ratio": 28.0,
    "recommendation": "hold",
    "sector": "Technology"
  },
  "technical": {
    "rsi": 54.0,
    "macd": {"line": 1.2, "signal": 0.8, "histogram": 0.4},
    "moving_averages": {"sma_20": 183.6, "sma_50": 185.2, "sma_200": 179.1},
    "signals": ["RSI neutral", "MACD bullish crossover", "Short-term trend above medium-term: bullish bias"]
  },
  "sentiment": {
    "overall_sentiment": "positive",
    "articles_analyzed": 23,
    "key_themes": ["earnings beat", "product launch"],
    "sentiment_score": 0.65
  },
  "summary": {
    "overall_stance": "bullish",
    "confidence": 0.715,
    "key_signals": ["Fundamental: hold (P/E 28.0)", "Sentiment: positive (+0.650)"],
    "risk_note": "Simulated outputs — not financial advice. Verify with live market data before acting."
  }
}
```

## Output

The response combines synthetic fundamental, technical, sentiment, and summary dictionaries. The
`risk_note` states that outputs are simulated; preserve it in every user-facing rendering.

## Error Handling

- Reject empty tickers, unsupported periods/indicators, and non-positive news windows.
- Never infer that an upstream API, filing, exchange, or news source was contacted.
- Refuse to frame the generated buy/hold/sell value as financial advice.

## Resources

Wraps [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) and
[ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis).

The local specialist only mirrors pipeline patterns. See
[the runtime contract](references/runtime-contract.md).
