"""The Rundown AI-specific repo tracking and editorial picks."""

from typing import Any

import httpx

_SEARCH_URL = "https://www.therundown.ai/search"
_TIMEOUT = 10.0


async def fetch_signals(repo: str) -> dict[str, Any]:
    """Fetch The Rundown signals for a repo.

    Searches The Rundown for mentions of the given GitHub repository.
    Returns a binary signal: 1.0 if the repo is mentioned, 0.0 otherwise.
    Any HTTP or parse error also returns 0.0.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with:
            mention (float 0-1): 1.0 if the repo appears in The Rundown, else 0.0.
    """
    default: dict[str, Any] = {"mention": 0.0}

    # Use the repository name (without owner) as the search term for broader coverage
    repo_name = repo.split("/")[-1] if "/" in repo else repo

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(
                _SEARCH_URL,
                params={"q": repo_name},
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/json",
                    "User-Agent": "Mozilla/5.0 (compatible; oss-agent-lab/1.0)",
                },
                follow_redirects=True,
            )
            response.raise_for_status()
            body = response.text
    except Exception:
        return default

    try:
        # Check for the full repo slug or repo name in the response body
        repo_lower = repo.lower()
        repo_name_lower = repo_name.lower()
        body_lower = body.lower()

        mentioned = repo_lower in body_lower or repo_name_lower in body_lower
    except Exception:
        return default

    return {"mention": 1.0 if mentioned else 0.0}
