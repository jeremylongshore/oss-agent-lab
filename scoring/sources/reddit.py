"""Reddit ML/AI subreddit signals — mentions, upvotes, cross-posts."""

from typing import Any

import httpx

_SEARCH_URL = "https://www.reddit.com/search.json"
_TIMEOUT = 10.0
_UPVOTES_MAX = 1_000


async def fetch_signals(repo: str) -> dict[str, Any]:
    """Fetch Reddit signals for a repo via the Reddit JSON search API.

    Searches Reddit for posts mentioning the repo, then sums upvote scores
    across the top results to produce a normalised community depth signal.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with:
            community_depth (float 0-1): normalised total upvotes (>1000 = 1.0).
        Defaults to 0.0 on any error.
    """
    default: dict[str, Any] = {"community_depth": 0.0}

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(
                _SEARCH_URL,
                params={"q": repo, "sort": "relevance", "limit": "10"},
                headers={
                    "Accept": "application/json",
                    "User-Agent": "oss-agent-lab/1.0 (scoring bot)",
                },
                follow_redirects=True,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
    except Exception:
        return default

    try:
        listing = data.get("data") or {}
        children: list[Any] = listing.get("children") or []
        if not isinstance(children, list):
            return default

        total_upvotes = 0
        for child in children:
            if not isinstance(child, dict):
                continue
            post_data = child.get("data") or {}
            if not isinstance(post_data, dict):
                continue
            try:
                score = int(post_data.get("score") or 0)
                total_upvotes += max(0, score)  # ignore negative karma
            except (TypeError, ValueError):
                pass

        community_depth = max(0.0, min(1.0, total_upvotes / _UPVOTES_MAX))
    except Exception:
        return default

    return {"community_depth": round(community_depth, 4)}
