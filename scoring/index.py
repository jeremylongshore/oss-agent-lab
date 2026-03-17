"""
Temporal Capability Index — timestamped score time series.

Tracks score evolution over time to detect:
- Rising repos (score increasing week-over-week)
- Peaked repos (score plateauing)
- Declining repos (score dropping)
"""
import json
from dataclasses import asdict, dataclass, field
from typing import Any


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

    # ------------------------------------------------------------------
    # Original methods (unchanged)
    # ------------------------------------------------------------------

    def add(self, entry: IndexEntry) -> None:
        """Append an entry to the index."""
        self.entries.append(entry)

    def get_rising(self, min_score: float = 60.0) -> list[IndexEntry]:
        """Get repos with rising scores above threshold."""
        return [e for e in self.entries if e.trend == "rising" and e.score >= min_score]

    def get_repo_history(self, repo: str) -> list[IndexEntry]:
        """Get score history for a specific repo."""
        return [e for e in self.entries if e.repo == repo]

    # ------------------------------------------------------------------
    # New methods
    # ------------------------------------------------------------------

    def detect_trend(self, repo: str) -> str:
        """Analyse a repo's score history and return its trend label.

        Returns:
            "new"       — fewer than 2 historical data points.
            "rising"    — most recent score is higher than the previous one.
            "declining" — most recent score is < 90 % of the previous score.
            "peaked"    — score is broadly flat (within ±10 % of previous).
        """
        history = self.get_repo_history(repo)
        if len(history) < 2:
            return "new"

        # Use the two most-recent entries (preserve insertion order as time order)
        prev = history[-2].score
        last = history[-1].score

        if last > prev:
            return "rising"
        if last < prev * 0.9:
            return "declining"
        return "peaked"

    def add_score(self, score: "Any") -> IndexEntry:
        """Create an IndexEntry from a CapabilityScore, detect trend, and store it.

        The ``score`` argument is typed as ``Any`` to avoid a circular import at
        the module level; it must be a ``CapabilityScore`` instance in practice.

        Args:
            score: A ``scoring.scorer.CapabilityScore`` instance.

        Returns:
            The newly created and stored ``IndexEntry``.
        """
        # Detect trend using existing history *before* appending the new entry
        trend = self.detect_trend(score.repo)

        entry = IndexEntry(
            repo=score.repo,
            score=score.total,
            timestamp=score.timestamp,
            trend=trend,
        )
        self.add(entry)
        return entry

    def to_json(self) -> str:
        """Serialise the index to a JSON string.

        Returns:
            A JSON-encoded string representing all entries in insertion order.
        """
        data: dict[str, Any] = {
            "entries": [asdict(e) for e in self.entries],
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, data: str) -> "TemporalIndex":
        """Deserialise a TemporalIndex from a JSON string produced by ``to_json``.

        Args:
            data: JSON string previously returned by ``to_json``.

        Returns:
            A new ``TemporalIndex`` populated with the stored entries.

        Raises:
            ValueError: If the JSON is malformed or missing required fields.
        """
        try:
            parsed: dict[str, Any] = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON for TemporalIndex: {exc}") from exc

        raw_entries = parsed.get("entries", [])
        entries: list[IndexEntry] = []
        for raw in raw_entries:
            try:
                entries.append(
                    IndexEntry(
                        repo=raw["repo"],
                        score=float(raw["score"]),
                        timestamp=raw["timestamp"],
                        trend=raw["trend"],
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Malformed IndexEntry in JSON: {raw!r}") from exc

        instance = cls()
        instance.entries = entries
        return instance

    def get_actionable(self, min_score: float = 60.0) -> list[IndexEntry]:
        """Return entries that are worth acting on immediately.

        An entry is actionable when its score meets the threshold *and* its
        trend is either "rising" (already gaining traction) or "new" (too
        early to judge decay, treat as opportunity).

        Args:
            min_score: Minimum total score required (default 60.0).

        Returns:
            List of matching ``IndexEntry`` objects in insertion order.
        """
        actionable_trends = {"rising", "new"}
        return [
            e
            for e in self.entries
            if e.score >= min_score and e.trend in actionable_trends
        ]
