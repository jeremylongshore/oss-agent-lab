"""Trendshift momentum scores and category rankings."""

from typing import Any

import httpx

_API_URL = "https://trendshift.io/api/repositories"
_TIMEOUT = 10.0


async def fetch_signals(repo: str) -> dict[str, Any]:
    """Fetch Trendshift momentum signals for a repo.

    Queries the Trendshift repository search endpoint and extracts a
    normalised momentum score from the first matching result.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with:
            momentum_score (float 0-1): 0.0 on error or not found.
    """
    default: dict[str, Any] = {"momentum_score": 0.0}

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(
                _API_URL,
                params={"q": repo},
                headers={"Accept": "application/json"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()
    except Exception:
        return default

    try:
        # API may return a list or a dict with a "repositories" / "items" key
        items: list[Any] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("repositories", "items", "data", "results"):
                if isinstance(data.get(key), list):
                    items = data[key]
                    break

        if not items:
            return default

        # Find the best matching entry by repo slug
        repo_lower = repo.lower()
        match: dict[str, Any] | None = None
        for item in items:
            if not isinstance(item, dict):
                continue
            full_name = (
                item.get("full_name")
                or item.get("fullName")
                or f"{item.get('owner', '')}/{item.get('name', '')}"
            )
            if full_name.lower() == repo_lower:
                match = item
                break

        if match is None and items:
            match = items[0] if isinstance(items[0], dict) else None

        if match is None:
            return default

        # Extract a raw score — field names vary by API version
        raw_score = (
            match.get("momentum_score")
            or match.get("momentumScore")
            or match.get("score")
            or 0.0
        )
        normalized = max(0.0, min(1.0, float(raw_score)))
    except Exception:
        return default

    return {"momentum_score": round(normalized, 4)}
