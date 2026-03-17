"""
Session Memory — persistent session context using cognee patterns.

Manages conversation history and agent memory across sessions.
Supports in-memory and persistent (file-based) backends.
"""
from oss_agent_lab.contracts import SessionContext


class SessionMemory:
    """Persistent session memory with history and knowledge graph integration."""

    def __init__(self, session_id: str | None = None, persist_dir: str | None = None):
        self.session_id = session_id
        self.persist_dir = persist_dir
        self._history: list[dict] = []

    async def store(self, entry: dict) -> None:
        """Store an entry in session memory."""
        self._history.append(entry)

    async def recall(self, query: str, top_k: int = 5) -> list[dict]:
        """Recall relevant entries from memory.

        Args:
            query: Search query for memory retrieval.
            top_k: Number of results to return.

        Returns:
            List of relevant memory entries.
        """
        raise NotImplementedError("Memory implementation: Epic 2")

    def get_context(self) -> SessionContext:
        """Get current session context."""
        return SessionContext(
            session_id=self.session_id or "default",
            history=self._history,
            memory=None,
        )
