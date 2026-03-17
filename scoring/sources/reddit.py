"""Reddit ML/AI subreddit signals — mentions, upvotes, cross-posts."""


async def fetch_signals(repo: str) -> dict:
    """Fetch Reddit signals for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with mention_count, upvotes, cross_posts, subreddit_list signals.
    """
    raise NotImplementedError("Epic 5: Reddit signals")
