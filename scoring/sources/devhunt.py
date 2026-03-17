"""DevHunt community upvotes and dev tool discovery signals."""


async def fetch_signals(repo: str) -> dict:
    """Fetch DevHunt signals for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with upvotes, launch_date, category, dev_tool_relevance signals.
    """
    raise NotImplementedError("Epic 5: DevHunt signals")
