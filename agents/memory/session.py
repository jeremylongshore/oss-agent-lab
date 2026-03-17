"""
Session Memory — in-memory session context with optional file persistence.

Manages conversation history and agent memory across sessions.
Simple keyword-based recall for v1 (no external deps).
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from oss_agent_lab.contracts import SessionContext


class SessionMemory:
    """Persistent session memory with history and keyword-based recall."""

    def __init__(
        self,
        session_id: str | None = None,
        persist_dir: str | None = None,
    ) -> None:
        self.session_id: str = session_id or str(uuid.uuid4())
        self.persist_dir: Path | None = Path(persist_dir) if persist_dir else None
        self._history: list[dict[str, Any]] = []

        # Auto-load from disk if persist_dir and session file exist.
        if self.persist_dir is not None:
            self._load_sync()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def store(self, entry: dict[str, Any]) -> None:
        """Store an entry in session memory.

        Args:
            entry: Arbitrary dict representing a memory entry.
        """
        self._history.append(entry)
        if self.persist_dir is not None:
            await self.persist()

    async def recall(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Recall relevant entries from memory via keyword matching.

        Splits the query into lowercase terms, then scores each history
        entry by how many term matches appear across all its string values.
        Returns the *top_k* entries with the highest match count (only
        entries with at least one match are returned).

        Args:
            query: Search query for memory retrieval.
            top_k: Maximum number of results to return.

        Returns:
            List of relevant memory entries, ordered by relevance.
        """
        terms: list[str] = query.lower().split()
        if not terms:
            return []

        scored: list[tuple[int, int, dict[str, Any]]] = []
        for idx, entry in enumerate(self._history):
            count = self._score_entry(entry, terms)
            if count > 0:
                scored.append((count, idx, entry))

        # Sort by match count descending, then by recency (index) descending.
        scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
        return [entry for _, _, entry in scored[:top_k]]

    def get_context(self) -> SessionContext:
        """Get current session context.

        Returns:
            SessionContext with session_id and full history.
        """
        return SessionContext(
            session_id=self.session_id,
            history=self._history,
            memory=None,
        )

    async def persist(self) -> None:
        """Save history to a JSON file if persist_dir is set."""
        if self.persist_dir is None:
            return
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        path = self.persist_dir / f"{self.session_id}.json"
        data: dict[str, Any] = {
            "session_id": self.session_id,
            "history": self._history,
        }
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    async def load(self) -> None:
        """Load history from a JSON file if it exists."""
        self._load_sync()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_sync(self) -> None:
        """Synchronous load used by __init__ and load()."""
        if self.persist_dir is None:
            return
        path = self.persist_dir / f"{self.session_id}.json"
        if not path.exists():
            return
        try:
            raw: str = path.read_text(encoding="utf-8")
            data: dict[str, Any] = json.loads(raw)
            self._history = data.get("history", [])
        except (json.JSONDecodeError, OSError):
            # Corrupted file — start fresh.
            self._history = []

    @staticmethod
    def _score_entry(entry: dict[str, Any], terms: list[str]) -> int:
        """Count how many query terms appear in the entry's string values.

        Args:
            entry: A history entry dict.
            terms: Lowercased query terms.

        Returns:
            Number of term matches found.
        """
        count = 0
        for value in entry.values():
            text = str(value).lower()
            for term in terms:
                if term in text:
                    count += 1
        return count
