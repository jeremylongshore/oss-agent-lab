"""OSSInsight deep analytics — growth curves, contributor patterns, PR velocity."""


async def fetch_signals(repo: str) -> dict:
    """Fetch OSSInsight analytics signals for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Dict with growth_curve, contributor_patterns, pr_velocity signals.
    """
    raise NotImplementedError("Epic 5: OSSInsight analytics")
