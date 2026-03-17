"""OSSInsight deep analytics — growth curves, contributor patterns, PR velocity."""

from typing import Any

import httpx

_BASE_URL = "https://api.ossinsight.io/v1/repos"
_TIMEOUT = 10.0
_STARS_MAX = 10_000
_STARS_MIN = 100
_CONTRIBUTORS_MAX = 20
_CONTRIBUTORS_MIN = 1


def _normalize_linear(value: float, lo: float, hi: float) -> float:
    """Clamp and linearly scale value into [0, 1]."""
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


async def fetch_signals(repo: str) -> dict[str, Any]:
    """Fetch OSSInsight analytics signals for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with:
            growth_curve (float 0-1): based on star count (>10k=1.0, <100=0.0)
            contributor_diversity (float 0-1): based on contributor count (>20=1.0, 1=0.1)
        Both default to 0.0 on any error.
    """
    default: dict[str, Any] = {"growth_curve": 0.0, "contributor_diversity": 0.0}

    parts = repo.strip("/").split("/")
    if len(parts) != 2:
        return default
    owner, name = parts

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(
                f"{_BASE_URL}/{owner}/{name}",
                headers={"Accept": "application/json"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
    except Exception:
        return default

    try:
        star_count = float(data.get("star_count") or data.get("stars") or 0)
        contributor_count = float(data.get("contributor_count") or data.get("contributors") or 0)
    except (TypeError, ValueError):
        return default

    growth_curve = _normalize_linear(star_count, _STARS_MIN, _STARS_MAX)

    # contributor_diversity: >20 → 1.0, 1 → 0.1, 0 → 0.0
    if contributor_count <= 0:
        contributor_diversity = 0.0
    elif contributor_count >= _CONTRIBUTORS_MAX:
        contributor_diversity = 1.0
    else:
        # Scale from 0.1 (at 1 contributor) to 1.0 (at 20)
        contributor_diversity = 0.1 + 0.9 * _normalize_linear(
            contributor_count, _CONTRIBUTORS_MIN, _CONTRIBUTORS_MAX
        )

    return {
        "growth_curve": round(growth_curve, 4),
        "contributor_diversity": round(contributor_diversity, 4),
    }
