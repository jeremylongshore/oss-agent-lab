"""GitHub Trending scraper — daily/weekly/monthly star velocity signals."""

import re
from typing import Any

import httpx

_TRENDING_URL = "https://github.com/trending"
_TIMEOUT = 10.0
_MAX_POSITION = 25


async def fetch_trending(
    period: str = "daily", language: str | None = None
) -> list[dict[str, Any]]:
    """Fetch trending repos from GitHub.

    Args:
        period: "daily", "weekly", or "monthly"
        language: Optional language filter (e.g. "python")

    Returns:
        List of dicts with repo, stars, description, position.
        Empty list on any error.
    """
    params: dict[str, str] = {"since": period}
    if language:
        params["l"] = language

    url = _TRENDING_URL if not language else f"{_TRENDING_URL}/{language}"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(
                url,
                params={"since": period},
                headers={"Accept": "text/html"},
                follow_redirects=True,
            )
            response.raise_for_status()
            html = response.text
    except Exception:
        return []

    return _parse_trending_html(html)


def _parse_trending_html(html: str) -> list[dict[str, Any]]:
    """Extract repo data from GitHub trending HTML.

    Uses regex to pull repo slugs, star counts, and descriptions from the
    rendered page structure without requiring BeautifulSoup.
    """
    results: list[dict[str, Any]] = []

    # Each trending article contains the repo slug in an h2 > a href
    re.compile(
        r'href="/([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)"[^>]*>\s*'
        r'<span[^>]*>[^<]*</span>\s*/\s*<span[^>]*>([^<]+)</span>',
        re.DOTALL,
    )

    # Stars are in a span with aria-label containing "stars"
    re.compile(
        r'aria-label="([0-9,]+)\s+(?:users starred|stars)"',
    )

    # Description lives in a <p> tag with class containing "col-9" or "color-fg-muted"
    re.compile(
        r'<p[^>]+class="[^"]*(?:col-9|color-fg-muted)[^"]*"[^>]*>\s*(.*?)\s*</p>',
        re.DOTALL,
    )

    # Split by article tags to get per-repo blocks
    article_blocks = re.split(r'<article\b', html)[1:]

    for position, block in enumerate(article_blocks, start=1):
        if position > _MAX_POSITION:
            break

        # Repo slug
        repo_match = re.search(
            r'href="/([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)"',
            block,
        )
        if not repo_match:
            continue
        repo_slug = repo_match.group(1).strip()

        # Stars — look for star count text
        stars = 0
        star_match = re.search(r'([\d,]+)\s+stars\s+this', block)
        if not star_match:
            # Fallback: any integer near "starred" text
            star_match = re.search(r'([\d,]+)\s+star', block)
        if star_match:
            try:
                stars = int(star_match.group(1).replace(",", ""))
            except ValueError:
                stars = 0

        # Description
        description = ""
        desc_match = re.search(
            r'<p[^>]*class="[^"]*(?:col-9|color-fg-muted)[^"]*"[^>]*>\s*(.*?)\s*</p>',
            block,
            re.DOTALL,
        )
        if desc_match:
            raw = desc_match.group(1)
            description = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', raw)).strip()

        results.append(
            {
                "repo": repo_slug,
                "stars": stars,
                "description": description,
                "position": position,
            }
        )

    return results


async def get_signals(repo: str) -> dict[str, Any]:
    """Return normalised trending signals for a single repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with keys:
            star_velocity (float 0-1): 1.0 for position 1, 0.0 for position 25+
            trending_position (float 0-1): 1 - (position / MAX_POSITION), clamped
        Both default to 0.0 if the repo is not found or an error occurs.
    """
    default: dict[str, Any] = {"star_velocity": 0.0, "trending_position": 0.0}

    try:
        trending = await fetch_trending()
    except Exception:
        return default

    repo_lower = repo.lower()
    for entry in trending:
        if entry.get("repo", "").lower() == repo_lower:
            position = entry["position"]
            score = max(0.0, 1.0 - (position - 1) / (_MAX_POSITION - 1))
            return {
                "star_velocity": round(score, 4),
                "trending_position": round(max(0.0, 1.0 - position / _MAX_POSITION), 4),
            }

    return default
