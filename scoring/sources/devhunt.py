"""DevHunt community upvotes and dev tool discovery signals."""

import contextlib
from typing import Any

import httpx

_API_URL = "https://devhunt.org/api/tools"
_TIMEOUT = 10.0
_UPVOTES_MAX = 100


async def fetch_signals(repo: str) -> dict[str, Any]:
    """Fetch DevHunt signals for a repo.

    Searches DevHunt for the given GitHub repo and returns a normalised
    upvote score. The DevHunt API is best-effort; any HTTP or parse error
    returns a zero signal.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with:
            upvotes (float 0-1): >100 upvotes = 1.0, 0 upvotes = 0.0.
    """
    default: dict[str, Any] = {"upvotes": 0.0}

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(
                _API_URL,
                params={"q": repo, "github": repo},
                headers={"Accept": "application/json"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()
    except Exception:
        return default

    try:
        items: list[Any] = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("tools", "items", "data", "results"):
                if isinstance(data.get(key), list):
                    items = data[key]
                    break

        if not items:
            return default

        # Match by github repo URL or slug
        repo_lower = repo.lower()
        best_upvotes = 0
        for item in items:
            if not isinstance(item, dict):
                continue
            github_url = str(item.get("github_url") or item.get("githubUrl") or "").lower()
            item_repo = github_url.rstrip("/").split("github.com/")[-1]
            if item_repo == repo_lower or repo_lower in github_url:
                raw = item.get("upvotes") or item.get("votes") or item.get("vote_count") or 0
                with contextlib.suppress(TypeError, ValueError):
                    best_upvotes = max(best_upvotes, int(raw))

        if best_upvotes == 0 and items:
            # Fallback: take first result's upvotes
            first = items[0] if isinstance(items[0], dict) else {}
            raw = first.get("upvotes") or first.get("votes") or first.get("vote_count") or 0
            try:
                best_upvotes = int(raw)
            except (TypeError, ValueError):
                best_upvotes = 0

        normalized = max(0.0, min(1.0, best_upvotes / _UPVOTES_MAX))
    except Exception:
        return default

    return {"upvotes": round(normalized, 4)}
