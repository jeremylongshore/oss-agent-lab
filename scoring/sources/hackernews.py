"""Hacker News front page detection, upvotes, discussion quality."""

import contextlib
from typing import Any

import httpx

_ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"
_TIMEOUT = 10.0
_POINTS_MAX = 500
_COMMENTS_MAX = 200


async def fetch_signals(repo: str) -> dict[str, Any]:
    """Fetch Hacker News signals for a repo via the Algolia search API.

    Searches for HN stories mentioning the repo, then sums points and
    comment counts across all hits to produce normalised signals.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with:
            frontpage_score (float 0-1): normalised total points (>500 = 1.0)
            community_depth (float 0-1): normalised total comments (>200 = 1.0)
        Both default to 0.0 on any error.
    """
    default: dict[str, Any] = {"frontpage_score": 0.0, "community_depth": 0.0}

    # Search for the full slug; also try just the repo name for broader recall
    query = repo
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(
                _ALGOLIA_URL,
                params={"query": query, "tags": "story"},
                headers={"Accept": "application/json"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
    except Exception:
        return default

    try:
        hits: list[Any] = data.get("hits") or []
        if not isinstance(hits, list):
            return default

        total_points = 0
        total_comments = 0
        for hit in hits:
            if not isinstance(hit, dict):
                continue
            with contextlib.suppress(TypeError, ValueError):
                total_points += int(hit.get("points") or 0)
            with contextlib.suppress(TypeError, ValueError):
                total_comments += int(hit.get("num_comments") or 0)

        frontpage_score = max(0.0, min(1.0, total_points / _POINTS_MAX))
        community_depth = max(0.0, min(1.0, total_comments / _COMMENTS_MAX))
    except Exception:
        return default

    return {
        "frontpage_score": round(frontpage_score, 4),
        "community_depth": round(community_depth, 4),
    }
