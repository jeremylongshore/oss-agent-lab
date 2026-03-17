"""
Capability Scorer — weighted composite scoring (0-100) from multi-source signals.

Score = 40% discovery + 35% quality + 25% durability

Thresholds:
    80-100: Auto-scaffold specialist + priority review
    60-79:  Queue for evaluation
    40-59:  Watch list
    < 40:   Skip
"""
from dataclasses import dataclass


@dataclass
class CapabilityScore:
    """Composite capability score for a GitHub repo."""
    repo: str
    total: float  # 0-100
    discovery: float  # 0-40
    quality: float  # 0-35
    durability: float  # 0-25
    timestamp: str
    sources: dict[str, float]  # source_name → normalized signal (0-1)

    @property
    def action(self) -> str:
        if self.total >= 80:
            return "auto_scaffold"
        elif self.total >= 60:
            return "evaluate"
        elif self.total >= 40:
            return "watch"
        return "skip"


async def score_repo(repo: str) -> CapabilityScore:
    """Score a GitHub repo using all available sources.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        CapabilityScore with weighted composite.
    """
    raise NotImplementedError("Scoring engine implementation: Epic 5")
