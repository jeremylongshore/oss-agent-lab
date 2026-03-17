"""GitHub Trending scraper — daily/weekly/monthly star velocity signals."""


async def fetch_trending(period: str = "daily", language: str | None = None) -> list[dict]:
    """Fetch trending repos from GitHub.

    Args:
        period: "daily", "weekly", or "monthly"
        language: Optional language filter

    Returns:
        List of dicts with repo, stars, description, star_velocity.
    """
    raise NotImplementedError("Epic 5: GitHub Trending scraper")
