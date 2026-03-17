"""Hacker News front page detection, upvotes, discussion quality."""


async def fetch_signals(repo: str) -> dict:
    """Fetch Hacker News signals for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with frontpage_score, upvotes, comment_count, discussion_quality signals.
    """
    raise NotImplementedError("Epic 5: Hacker News signals")
