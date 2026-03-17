---
name: stock_analyst
display_name: Stock Analyst Specialist
description: >
  Multi-agent financial analysis pipeline: fundamental analysis, technical
  indicators, and news sentiment scoring for any ticker symbol. Wraps patterns
  from virattt/ai-hedge-fund and ZhuLinsen/daily_stock_analysis.
version: 0.1.0
source_repo: virattt/ai-hedge-fund
license: MIT
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

Orchestrates a three-stage financial analysis pipeline for a requested ticker
symbol: fundamental analysis, technical indicator computation, and news
sentiment scoring. All three layers are merged into a single structured
response with a composite stance signal.

## Capabilities

- **analyze**: Full pipeline analysis for a given ticker and period.
- **finance**: Domain expertise in equity markets and financial ratios.
- **stock_analysis**: Fundamental metrics — price, market cap, P/E, sector, recommendation.
- **technical_analysis**: RSI, MACD, and moving averages with derived signals.

## Tools

| Tool | Description | Side Effects |
|------|-------------|--------------|
| `analyze_ticker` | Fundamental analysis: price, P/E, market cap, sector, recommendation | None |
| `technical_indicators` | RSI, MACD, moving averages, buy/sell signals | None |
| `news_sentiment` | Sentiment score, article count, key themes for recent news | None |

## Parameters

All parameters are passed via `request.intent.parameters`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ticker` | `str` | *(query text)* | Stock ticker symbol, e.g. `AAPL` |
| `period` | `str` | `"1y"` | Lookback period: `1m`, `3m`, `6m`, `1y`, `3y`, `5y` |
| `indicators` | `list[str]` | all | Subset of `rsi`, `macd`, `moving_averages` |
| `days` | `int` | `7` | News lookback window in calendar days |

## Usage

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

### Response Shape

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

## Source

Wraps [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) and
[ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis).
