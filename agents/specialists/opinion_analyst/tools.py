"""
Tools for the OpinionAnalyst specialist.

Wraps public-opinion analysis capabilities from 666ghj/BettaFish.
Each tool is a pure function: accepts inputs, returns structured output.
No side effects — all analysis runs locally on the supplied text.
"""

from typing import Any


def analyze_sentiment(text: str, granularity: str = "document") -> dict[str, Any]:
    """Perform sentiment analysis on the supplied text.

    Args:
        text: The text to analyse.
        granularity: Analysis grain — ``"document"`` (default), ``"sentence"``,
            or ``"aspect"``.

    Returns:
        Dict with keys:

        - ``sentiment``: Overall polarity — ``"positive"``, ``"negative"``,
          or ``"neutral"``.
        - ``confidence``: Model confidence in ``[0.0, 1.0]``.
        - ``aspects``: List of aspect-level dicts (``aspect``, ``sentiment``,
          ``score``) when ``granularity`` is ``"aspect"``; otherwise empty.
        - ``overall_score``: Continuous sentiment score in ``[-1.0, 1.0]``
          where ``-1`` is maximally negative and ``1`` is maximally positive.
    """
    if not text or not text.strip():
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "aspects": [],
            "overall_score": 0.0,
        }

    text_lower = text.lower()

    positive_terms = {
        "good",
        "great",
        "excellent",
        "love",
        "amazing",
        "wonderful",
        "best",
        "fantastic",
        "brilliant",
        "outstanding",
        "superb",
        "positive",
        "happy",
        "glad",
        "pleased",
        "support",
        "approve",
        "like",
        "enjoy",
        "beneficial",
    }
    negative_terms = {
        "bad",
        "terrible",
        "awful",
        "hate",
        "horrible",
        "worst",
        "poor",
        "disappointing",
        "negative",
        "sad",
        "angry",
        "oppose",
        "dislike",
        "harmful",
        "wrong",
        "fail",
        "failure",
        "problem",
        "issue",
        "concern",
    }

    words = text_lower.split()
    pos_count = sum(1 for w in words if w.strip(".,!?;:") in positive_terms)
    neg_count = sum(1 for w in words if w.strip(".,!?;:") in negative_terms)
    total = pos_count + neg_count

    if total == 0:
        raw_score = 0.0
        sentiment = "neutral"
        confidence = 0.5
    else:
        raw_score = (pos_count - neg_count) / max(len(words), 1)
        raw_score = max(-1.0, min(1.0, raw_score * 5))
        confidence = min(0.95, 0.5 + (total / max(len(words), 1)) * 2)
        if raw_score > 0.1:
            sentiment = "positive"
        elif raw_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

    aspects: list[dict[str, Any]] = []
    if granularity == "aspect":
        aspect_keywords: dict[str, list[str]] = {
            "quality": ["quality", "performance", "reliable", "stable"],
            "value": ["price", "cost", "value", "worth", "expensive", "cheap"],
            "usability": ["easy", "simple", "difficult", "hard", "intuitive"],
        }
        for aspect_name, keywords in aspect_keywords.items():
            hits = [w for w in words if w.strip(".,!?;:") in keywords]
            if hits:
                aspect_score = raw_score * 0.8
                aspects.append(
                    {
                        "aspect": aspect_name,
                        "sentiment": sentiment,
                        "score": round(aspect_score, 4),
                    }
                )

    return {
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "aspects": aspects,
        "overall_score": round(raw_score, 4),
    }


def detect_stance(text: str, target: str) -> dict[str, Any]:
    """Detect the author's stance toward a specific target entity or claim.

    Args:
        text: Source text in which to detect stance.
        target: The entity, topic, or claim the stance is measured against.

    Returns:
        Dict with keys:

        - ``stance``: Detected stance — ``"support"``, ``"oppose"``,
          or ``"neutral"``.
        - ``confidence``: Model confidence in ``[0.0, 1.0]``.
        - ``reasoning``: Short natural-language explanation of the stance.
        - ``evidence_count``: Number of stance-indicative passages found.
    """
    if not text or not text.strip() or not target or not target.strip():
        return {
            "stance": "neutral",
            "confidence": 0.0,
            "reasoning": "Insufficient input to determine stance.",
            "evidence_count": 0,
        }

    text_lower = text.lower()
    target_lower = target.lower()

    support_patterns = [
        f"support {target_lower}",
        f"agree with {target_lower}",
        f"in favour of {target_lower}",
        f"in favor of {target_lower}",
        f"backing {target_lower}",
        f"endorse {target_lower}",
        f"{target_lower} is good",
        f"{target_lower} is great",
        f"{target_lower} is right",
        f"for {target_lower}",
    ]
    oppose_patterns = [
        f"oppose {target_lower}",
        f"against {target_lower}",
        f"disagree with {target_lower}",
        f"reject {target_lower}",
        f"{target_lower} is bad",
        f"{target_lower} is wrong",
        f"{target_lower} is harmful",
        f"anti-{target_lower}",
        f"opposed to {target_lower}",
        f"criticise {target_lower}",
        f"criticize {target_lower}",
    ]

    support_hits = [p for p in support_patterns if p in text_lower]
    oppose_hits = [p for p in oppose_patterns if p in text_lower]

    # Fall back to general sentiment when no explicit target phrases found.
    if not support_hits and not oppose_hits:
        sentiment_result = analyze_sentiment(text)
        score = sentiment_result["overall_score"]
        if score > 0.1:
            stance = "support"
            reasoning = f"Text carries a positive tone that implies support for '{target}'."
            confidence = sentiment_result["confidence"] * 0.6
        elif score < -0.1:
            stance = "oppose"
            reasoning = f"Text carries a negative tone that implies opposition to '{target}'."
            confidence = sentiment_result["confidence"] * 0.6
        else:
            stance = "neutral"
            reasoning = f"No clear stance toward '{target}' detected."
            confidence = 0.5
        evidence_count = 0
    else:
        evidence_count = len(support_hits) + len(oppose_hits)
        if len(support_hits) > len(oppose_hits):
            stance = "support"
            reasoning = (
                f"Found {len(support_hits)} supporting expression(s) referencing '{target}'."
            )
            confidence = min(0.95, 0.6 + len(support_hits) * 0.1)
        elif len(oppose_hits) > len(support_hits):
            stance = "oppose"
            reasoning = f"Found {len(oppose_hits)} opposing expression(s) referencing '{target}'."
            confidence = min(0.95, 0.6 + len(oppose_hits) * 0.1)
        else:
            stance = "neutral"
            reasoning = "Equal supporting and opposing signals detected — stance is mixed."
            confidence = 0.5

    return {
        "stance": stance,
        "confidence": round(confidence, 4),
        "reasoning": reasoning,
        "evidence_count": evidence_count,
    }


def measure_bias(
    text: str,
    dimensions: list[str] | None = None,
) -> dict[str, Any]:
    """Measure bias in text across multiple dimensions.

    Args:
        text: The text to evaluate for bias.
        dimensions: Bias dimensions to measure. Defaults to
            ``["political", "emotional", "framing", "source", "confirmation"]``
            when ``None``.

    Returns:
        Dict with keys:

        - ``overall_bias_score``: Aggregate bias score in ``[0.0, 1.0]``
          where ``0`` is unbiased and ``1`` is maximally biased.
        - ``dimensions``: Dict mapping each requested dimension to its
          sub-score in ``[0.0, 1.0]``.
        - ``flags``: List of human-readable bias flags raised during analysis.
    """
    default_dimensions = ["political", "emotional", "framing", "source", "confirmation"]
    dims = dimensions if dimensions is not None else default_dimensions

    if not text or not text.strip():
        return {
            "overall_bias_score": 0.0,
            "dimensions": {d: 0.0 for d in dims},
            "flags": [],
        }

    text_lower = text.lower()
    words = text_lower.split()
    word_count = max(len(words), 1)

    dimension_signals: dict[str, list[str]] = {
        "political": [
            "liberal",
            "conservative",
            "democrat",
            "republican",
            "left-wing",
            "right-wing",
            "socialist",
            "capitalist",
            "progressive",
            "radical",
            "regime",
            "establishment",
            "elites",
            "patriots",
        ],
        "emotional": [
            "outrage",
            "shocking",
            "horrifying",
            "disgusting",
            "devastating",
            "incredible",
            "unbelievable",
            "alarming",
            "explosive",
            "bombshell",
            "crisis",
            "catastrophe",
            "disaster",
            "miracle",
        ],
        "framing": [
            "so-called",
            "allegedly",
            "claimed",
            "supposedly",
            "admitted",
            "confessed",
            "refuses to",
            "fails to",
            "forced to",
            "despite",
        ],
        "source": [
            "anonymous source",
            "insider",
            "expert says",
            "studies show",
            "everyone knows",
            "many people",
            "some say",
            "reports claim",
        ],
        "confirmation": [
            "as expected",
            "of course",
            "obviously",
            "clearly",
            "naturally",
            "as we knew",
            "proven again",
            "confirms what",
            "yet again",
        ],
    }

    scores: dict[str, float] = {}
    flags: list[str] = []

    for dim in dims:
        signals = dimension_signals.get(dim, [])
        hit_count = sum(1 for signal in signals if signal in text_lower)
        raw = hit_count / max(len(signals), 1)
        score = min(1.0, raw * 3.0)
        scores[dim] = round(score, 4)

        if score > 0.3:
            flags.append(f"Elevated {dim} bias detected (score={score:.2f}).")
        if dim == "emotional" and score > 0.5:
            flags.append("High emotional language — text may be sensationalised.")
        if dim == "political" and score > 0.4:
            flags.append("Strong political framing present.")

    # Penalise exclamation marks as a simple sensationalism heuristic.
    exclamation_ratio = text.count("!") / word_count
    if exclamation_ratio > 0.05:
        flags.append("Excessive exclamation marks suggest sensationalist tone.")

    # ALL-CAPS words (3+ chars) signal shouting/emphasis bias.
    caps_words = [w for w in text.split() if len(w) >= 3 and w.isupper()]
    if len(caps_words) / word_count > 0.05:
        flags.append("High proportion of ALL-CAPS words detected.")

    dim_values = list(scores.values())
    overall = round(sum(dim_values) / max(len(dim_values), 1), 4) if dim_values else 0.0

    return {
        "overall_bias_score": overall,
        "dimensions": scores,
        "flags": flags,
    }
