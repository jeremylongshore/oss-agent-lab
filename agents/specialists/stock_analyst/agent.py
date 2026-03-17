"""
StockAnalyst specialist — multi-agent financial analysis pipeline.

Wraps patterns from virattt/ai-hedge-fund and ZhuLinsen/daily_stock_analysis.
Orchestrates three analysis layers for a requested ticker: fundamental analysis,
technical indicators, and news sentiment scoring. Results are merged into a
single structured response suitable for downstream consumption.

Typical pipeline:
    1. Extract ticker symbol (and optional parameters) from the request.
    2. Run fundamental analysis via analyze_ticker().
    3. Compute technical indicators via technical_indicators().
    4. Score recent news sentiment via news_sentiment().
    5. Merge all three layers into a SpecialistResponse.
"""

from __future__ import annotations

import time
from typing import Any, ClassVar

from agents.specialists.stock_analyst.tools import (
    analyze_ticker,
    news_sentiment,
    technical_indicators,
)
from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class StockAnalystSpecialist(BaseSpecialist):
    """Multi-agent financial analysis: fundamentals, technicals, and news sentiment.

    Each call to :meth:`execute` runs the full three-stage pipeline for a
    single ticker, merging results from all analysis layers into a unified
    response. The specialist is stateless — every request is independent.

    Attributes:
        name: Specialist identifier used for routing.
        description: Human-readable capability summary.
        source_repo: Primary upstream GitHub repository this specialist wraps.
        capabilities: List of string capability tags.
        output_formats: Supported output modes.
        tools: Tool descriptors made available to the agent runtime.
    """

    name: ClassVar[str] = "stock_analyst"
    description: ClassVar[str] = (
        "Multi-agent financial analysis: fundamental analysis, technical indicators, "
        "and news sentiment for any ticker symbol"
    )
    source_repo: ClassVar[str] = "virattt/ai-hedge-fund"
    capabilities: ClassVar[list[str]] = [
        "analyze",
        "finance",
        "stock_analysis",
        "technical_analysis",
    ]

    output_formats: ClassVar[list[OutputFormat]] = [
        OutputFormat.PYTHON_API,
        OutputFormat.CLI,
        OutputFormat.MCP_SERVER,
        OutputFormat.AGENT_SKILL,
        OutputFormat.REST_API,
    ]

    tools: ClassVar[list[Tool]] = [
        Tool(
            name="analyze_ticker",
            description=(
                "Run fundamental analysis for a ticker symbol. Returns price, market cap, "
                "P/E ratio, sector, and a buy/hold/sell recommendation."
            ),
            parameters={
                "ticker": {"type": "string", "description": "Stock ticker symbol (e.g. AAPL)"},
                "period": {
                    "type": "string",
                    "description": "Lookback period: 1m, 3m, 6m, 1y, 3y, 5y",
                    "default": "1y",
                },
            },
        ),
        Tool(
            name="technical_indicators",
            description=(
                "Calculate technical indicators for a ticker: RSI, MACD, and moving averages. "
                "Returns computed values and derived buy/sell signals."
            ),
            parameters={
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "indicators": {
                    "type": "array",
                    "description": "Indicators to compute: rsi, macd, moving_averages",
                    "default": None,
                },
            },
        ),
        Tool(
            name="news_sentiment",
            description=(
                "Analyse recent news sentiment for a ticker. Returns overall sentiment, "
                "article count, key themes, and a sentiment score in [-1, 1]."
            ),
            parameters={
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
                "days": {
                    "type": "integer",
                    "description": "Lookback window in calendar days",
                    "default": 7,
                },
            },
        ),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Run the full financial analysis pipeline for the requested ticker.

        Extracts the ticker symbol from ``request.intent.parameters["ticker"]``
        when present; otherwise falls back to ``request.query.user_input``.
        Additional per-tool parameters (``period``, ``indicators``, ``days``)
        may also be passed via ``request.intent.parameters``.

        Args:
            request: The routed specialist request carrying an :class:`Intent`
                and a :class:`Query`.

        Returns:
            A :class:`SpecialistResponse` with:
                - ``status``: ``"success"`` on a clean run.
                - ``result``: Dict containing ``ticker``, ``fundamental``,
                  ``technical``, ``sentiment``, and ``summary``.
                - ``metadata``: Pipeline configuration and timing details.
                - ``duration_ms``: Wall-clock time for the full pipeline.
        """
        t_start = time.perf_counter()

        params: dict[str, Any] = request.intent.parameters or {}
        ticker: str = str(params.get("ticker") or request.query.user_input).strip()
        period: str = str(params.get("period", "1y"))
        indicators: list[str] | None = params.get("indicators") or None
        news_days: int = int(params.get("days", 7))

        # Stage 1 — fundamental analysis.
        fundamental = analyze_ticker(ticker=ticker, period=period)

        # Stage 2 — technical indicators.
        technical = technical_indicators(ticker=ticker, indicators=indicators)

        # Stage 3 — news sentiment.
        sentiment = news_sentiment(ticker=ticker, days=news_days)

        # Derive a composite summary from all three layers.
        summary = _build_summary(fundamental, technical, sentiment)

        duration_ms = (time.perf_counter() - t_start) * 1000.0

        result: dict[str, Any] = {
            "ticker": fundamental["ticker"],
            "fundamental": fundamental,
            "technical": technical,
            "sentiment": sentiment,
            "summary": summary,
        }

        metadata: dict[str, Any] = {
            "source_repos": [self.source_repo, "ZhuLinsen/daily_stock_analysis"],
            "period": period,
            "indicators_requested": indicators,
            "news_days": news_days,
        }

        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result=result,
            metadata=metadata,
            duration_ms=round(duration_ms, 3),
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_summary(
    fundamental: dict[str, Any],
    technical: dict[str, Any],
    sentiment: dict[str, Any],
) -> dict[str, Any]:
    """Merge signals from all three analysis layers into a composite summary.

    Weights fundamental recommendation (40%), technical signals (30%), and
    news sentiment (30%) to produce an overall stance.

    Args:
        fundamental: Output from :func:`analyze_ticker`.
        technical: Output from :func:`technical_indicators`.
        sentiment: Output from :func:`news_sentiment`.

    Returns:
        A dict with ``overall_stance``, ``confidence``, ``key_signals``, and
        ``risk_note``.
    """
    # Fundamental score: buy=1.0, hold=0.5, sell=0.0.
    rec_map = {"buy": 1.0, "hold": 0.5, "sell": 0.0}
    fundamental_score = rec_map.get(fundamental.get("recommendation", "hold"), 0.5)

    # Technical score: fraction of bullish signals.
    signals: list[str] = technical.get("signals", [])
    bullish_count = sum(1 for s in signals if "bullish" in s.lower() or "oversold" in s.lower())
    technical_score = bullish_count / len(signals) if signals else 0.5

    # Sentiment score: normalise from [-1, 1] to [0, 1].
    raw_sentiment: float = sentiment.get("sentiment_score", 0.0)
    sentiment_score = (raw_sentiment + 1.0) / 2.0

    composite = (fundamental_score * 0.4) + (technical_score * 0.3) + (sentiment_score * 0.3)

    if composite >= 0.65:
        overall_stance = "bullish"
    elif composite >= 0.4:
        overall_stance = "neutral"
    else:
        overall_stance = "bearish"

    confidence = round(composite, 3)

    key_signals: list[str] = [
        f"Fundamental: {fundamental.get('recommendation', 'hold')} "
        f"(P/E {fundamental.get('pe_ratio', 'N/A')})",
        f"Sentiment: {sentiment.get('overall_sentiment', 'neutral')} (score {raw_sentiment:+.3f})",
    ]
    key_signals.extend(signals[:3])

    risk_note = (
        "Simulated outputs — not financial advice. Verify with live market data before acting."
    )

    return {
        "overall_stance": overall_stance,
        "confidence": confidence,
        "key_signals": key_signals,
        "risk_note": risk_note,
    }
