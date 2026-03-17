"""
Tools for the StockAnalyst specialist.

Implements financial analysis patterns inspired by virattt/ai-hedge-fund and
ZhuLinsen/daily_stock_analysis: fundamental analysis, technical indicators, and
news sentiment scoring.

Each function is a pure transformation — no I/O side effects. Live market data
and news feeds would be injected via caller-supplied parameters in production
rather than simulated here.
"""

from __future__ import annotations

from typing import Any


def analyze_ticker(ticker: str, period: str = "1y") -> dict[str, Any]:
    """Run fundamental analysis for a given ticker symbol.

    Evaluates key financial ratios, market cap, and overall investment stance
    for the requested period. In production this function would fetch real-time
    or historical data from a market-data provider; here the outputs are derived
    deterministically from the ticker string to allow end-to-end pipeline testing.

    Args:
        ticker: The stock ticker symbol (e.g. ``"AAPL"``, ``"MSFT"``).
            Case-insensitive; normalised to uppercase internally.
        period: Lookback window for the analysis. Common values are ``"1m"``,
            ``"3m"``, ``"6m"``, ``"1y"``, ``"3y"``, ``"5y"``. Defaults to
            ``"1y"``.

    Returns:
        A dict with:
            - ``ticker``: Normalised ticker symbol.
            - ``period``: The period that was analysed.
            - ``price``: Simulated current price in USD.
            - ``market_cap``: Simulated market capitalisation in USD billions.
            - ``pe_ratio``: Price-to-earnings ratio.
            - ``recommendation``: One of ``"buy"``, ``"hold"``, ``"sell"``.
            - ``sector``: Inferred sector string for the ticker.

    Raises:
        ValueError: If ``ticker`` is empty.
    """
    if not ticker:
        raise ValueError("ticker must not be empty")

    sym = ticker.upper().strip()
    seed = sum(ord(c) for c in sym)

    # Deterministic but ticker-varied simulated fundamentals.
    price = round(50.0 + (seed % 450), 2)
    market_cap = round(10.0 + (seed % 2990) * 0.1, 2)
    pe_raw = 10 + (seed % 30)
    pe_ratio = round(float(pe_raw), 1)

    sectors = ["Technology", "Healthcare", "Financials", "Consumer Discretionary", "Energy"]
    sector = sectors[seed % len(sectors)]

    if pe_ratio < 20:
        recommendation = "buy"
    elif pe_ratio < 30:
        recommendation = "hold"
    else:
        recommendation = "sell"

    return {
        "ticker": sym,
        "period": period,
        "price": price,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "recommendation": recommendation,
        "sector": sector,
    }


def technical_indicators(
    ticker: str,
    indicators: list[str] | None = None,
) -> dict[str, Any]:
    """Calculate technical indicators for a given ticker symbol.

    Computes momentum and trend signals commonly used in quantitative trading
    strategies. Supported indicators: ``"rsi"``, ``"macd"``, ``"moving_averages"``.
    All three are computed by default when *indicators* is ``None``.

    Args:
        ticker: The stock ticker symbol. Case-insensitive.
        indicators: Optional list of indicator names to compute. If ``None``
            or empty, all supported indicators are returned.

    Returns:
        A dict with:
            - ``ticker``: Normalised ticker symbol.
            - ``indicators_computed``: List of indicator names that were run.
            - ``rsi``: Relative Strength Index (0-100). ``None`` if not requested.
            - ``macd``: Dict with ``"line"``, ``"signal"``, and ``"histogram"``
              values. ``None`` if not requested.
            - ``moving_averages``: Dict with ``"sma_20"``, ``"sma_50"``, and
              ``"sma_200"`` price levels. ``None`` if not requested.
            - ``signals``: List of human-readable signal strings derived from the
              computed indicators.

    Raises:
        ValueError: If ``ticker`` is empty.
    """
    if not ticker:
        raise ValueError("ticker must not be empty")

    sym = ticker.upper().strip()
    seed = sum(ord(c) for c in sym)

    _all = {"rsi", "macd", "moving_averages"}
    requested = {ind.lower() for ind in indicators} if indicators else _all
    computed = sorted(requested & _all)

    rsi: float | None = None
    macd: dict[str, float] | None = None
    moving_averages: dict[str, float] | None = None
    signals: list[str] = []

    if "rsi" in requested:
        rsi = round(20.0 + (seed % 60), 1)
        if rsi < 30:
            signals.append("RSI oversold — potential reversal upward")
        elif rsi > 70:
            signals.append("RSI overbought — potential pullback ahead")
        else:
            signals.append("RSI neutral")

    if "macd" in requested:
        macd_line = round(-2.0 + (seed % 40) * 0.1, 3)
        signal_line = round(macd_line - (0.5 + (seed % 10) * 0.05), 3)
        histogram = round(macd_line - signal_line, 3)
        macd = {"line": macd_line, "signal": signal_line, "histogram": histogram}
        if histogram > 0:
            signals.append("MACD bullish crossover")
        else:
            signals.append("MACD bearish crossover")

    if "moving_averages" in requested:
        base_price = round(50.0 + (seed % 450), 2)
        moving_averages = {
            "sma_20": round(base_price * (1 + (seed % 5) * 0.01), 2),
            "sma_50": round(base_price * (1 + (seed % 8) * 0.01), 2),
            "sma_200": round(base_price * (1 - (seed % 6) * 0.01), 2),
        }
        if moving_averages["sma_20"] > moving_averages["sma_50"]:
            signals.append("Short-term trend above medium-term: bullish bias")
        else:
            signals.append("Short-term trend below medium-term: bearish bias")

    return {
        "ticker": sym,
        "indicators_computed": computed,
        "rsi": rsi,
        "macd": macd,
        "moving_averages": moving_averages,
        "signals": signals,
    }


def news_sentiment(ticker: str, days: int = 7) -> dict[str, Any]:
    """Analyse news sentiment for a given ticker over a recent lookback window.

    Aggregates sentiment signals from recent news articles and surfaces key
    themes influencing the stock narrative. In production this function would
    call a news API (e.g. Finnhub, Alpha Vantage) and run NLP scoring; here
    outputs are simulated deterministically to enable full pipeline testing.

    Args:
        ticker: The stock ticker symbol. Case-insensitive.
        days: Number of calendar days to look back for news articles.
            Must be >= 1. Defaults to 7.

    Returns:
        A dict with:
            - ``ticker``: Normalised ticker symbol.
            - ``days_analysed``: The lookback window that was used.
            - ``overall_sentiment``: One of ``"positive"``, ``"neutral"``,
              ``"negative"``.
            - ``articles_analyzed``: Simulated count of news articles processed.
            - ``key_themes``: List of dominant theme strings extracted from
              the article corpus.
            - ``sentiment_score``: Float in [-1.0, 1.0] where -1.0 is maximally
              negative, 0.0 is neutral, and 1.0 is maximally positive.

    Raises:
        ValueError: If ``ticker`` is empty or ``days`` < 1.
    """
    if not ticker:
        raise ValueError("ticker must not be empty")
    if days < 1:
        raise ValueError(f"days must be >= 1, got {days}")

    sym = ticker.upper().strip()
    seed = sum(ord(c) for c in sym)

    articles_analyzed = 5 + (seed % 46)  # range: 5 - 50

    # Score in [-1.0, 1.0] derived from seed.
    raw_score = ((seed % 201) - 100) / 100.0
    sentiment_score = round(raw_score, 3)

    if sentiment_score > 0.1:
        overall_sentiment = "positive"
    elif sentiment_score < -0.1:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    all_themes = [
        "earnings beat",
        "regulatory scrutiny",
        "product launch",
        "analyst upgrade",
        "supply chain concerns",
        "leadership change",
        "market expansion",
        "competitor pressure",
    ]
    # Pick 2-4 themes deterministically.
    theme_count = 2 + (seed % 3)
    key_themes = [all_themes[(seed + i) % len(all_themes)] for i in range(theme_count)]

    return {
        "ticker": sym,
        "days_analysed": days,
        "overall_sentiment": overall_sentiment,
        "articles_analyzed": articles_analyzed,
        "key_themes": key_themes,
        "sentiment_score": sentiment_score,
    }
