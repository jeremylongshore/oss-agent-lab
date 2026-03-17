"""
Specialist Registry — auto-discovers specialists from the specialists/ directory.

Scans for SKILL.md files, loads metadata, builds a capability index.
Supports dynamic registration at runtime.
"""
from pathlib import Path


class SpecialistRegistry:
    """Registry that auto-discovers and indexes specialists."""

    def __init__(self, specialists_dir: Path | None = None):
        self.specialists_dir = specialists_dir or Path(__file__).parent.parent / "specialists"
        self._registry: dict[str, dict] = {}

    def discover(self) -> int:
        """Scan specialists/ directory and register all found specialists.

        Returns:
            Number of specialists discovered.
        """
        raise NotImplementedError("Registry implementation: Epic 2")

    def get(self, name: str) -> dict | None:
        """Get specialist metadata by name."""
        return self._registry.get(name)

    def match_capabilities(self, capabilities: list[str]) -> list[str]:
        """Find specialists that match requested capabilities.

        Args:
            capabilities: List of capability identifiers to match.

        Returns:
            List of specialist names that match.
        """
        raise NotImplementedError("Registry implementation: Epic 2")

    def list_all(self) -> list[dict]:
        """List all registered specialists with metadata."""
        return list(self._registry.values())
