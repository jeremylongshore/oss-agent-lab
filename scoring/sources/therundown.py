"""The Rundown AI-specific repo tracking and editorial picks."""


async def fetch_signals(repo: str) -> dict:
    """Fetch The Rundown signals for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with mention_count, editorial_pick, ai_relevance_score signals.
    """
    raise NotImplementedError("Epic 5: The Rundown signals")
