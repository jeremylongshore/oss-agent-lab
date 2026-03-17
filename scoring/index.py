"""
Temporal Capability Index — timestamped score time series.

Tracks score evolution over time to detect:
- Rising repos (score increasing week-over-week)
- Peaked repos (score plateauing)
- Declining repos (score dropping)
"""
from dataclasses import dataclass, field


@dataclass
class IndexEntry:
    """Single point in a repo's score time series."""
    repo: str
    score: float
    timestamp: str
    trend: str  # "rising" | "peaked" | "declining" | "new"


@dataclass
class TemporalIndex:
    """Time-series index of all scored repos."""
    entries: list[IndexEntry] = field(default_factory=list)

    def add(self, entry: IndexEntry) -> None:
        self.entries.append(entry)

    def get_rising(self, min_score: float = 60.0) -> list[IndexEntry]:
        """Get repos with rising scores above threshold."""
        return [e for e in self.entries if e.trend == "rising" and e.score >= min_score]

    def get_repo_history(self, repo: str) -> list[IndexEntry]:
        """Get score history for a specific repo."""
        return [e for e in self.entries if e.repo == repo]
