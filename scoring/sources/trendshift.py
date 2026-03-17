"""Trendshift momentum scores and category rankings."""


async def fetch_signals(repo: str) -> dict:
    """Fetch Trendshift momentum signals for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with momentum_score, category_rank, trending_duration signals.
    """
    raise NotImplementedError("Epic 5: Trendshift momentum")
