"""
Specialist Registry — auto-discovers specialists from the specialists/ directory.

Scans for SKILL.md files, loads metadata, builds a capability index.
Supports dynamic registration at runtime.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def _parse_frontmatter(path: Path) -> dict[str, Any] | None:
    """Extract YAML frontmatter from a SKILL.md file.

    Args:
        path: Path to the SKILL.md file.

    Returns:
        Parsed frontmatter dict, or None if parsing fails.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Failed to read %s: %s", path, exc)
        return None

    # Frontmatter must start and end with '---' lines.
    if not text.startswith("---"):
        logger.warning("SKILL.md missing frontmatter: %s", path)
        return None

    end_idx = text.index("---", 3) if "---" in text[3:] else -1
    if end_idx == -1:
        logger.warning("SKILL.md has unclosed frontmatter: %s", path)
        return None

    yaml_block = text[3:end_idx].strip()
    try:
        data: Any = yaml.safe_load(yaml_block)
    except yaml.YAMLError as exc:
        logger.warning("SKILL.md has malformed YAML frontmatter in %s: %s", path, exc)
        return None

    if not isinstance(data, dict):
        logger.warning("SKILL.md frontmatter is not a mapping in %s", path)
        return None

    return data


class SpecialistRegistry:
    """Registry that auto-discovers and indexes specialists."""

    def __init__(self, specialists_dir: Path | None = None) -> None:
        self.specialists_dir = specialists_dir or Path(__file__).parent.parent / "specialists"
        self._registry: dict[str, dict[str, Any]] = {}

    def discover(self) -> int:
        """Scan specialists/ directory and register all found specialists.

        Skips the ``_template/`` directory and any subdirectory that lacks a
        valid SKILL.md with parseable YAML frontmatter.

        Returns:
            Number of specialists discovered.
        """
        if not self.specialists_dir.is_dir():
            logger.warning("Specialists directory not found: %s", self.specialists_dir)
            return 0

        count = 0
        for child in sorted(self.specialists_dir.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith("_"):
                continue

            skill_path = child / "SKILL.md"
            if not skill_path.exists():
                logger.debug("No SKILL.md in %s, skipping", child.name)
                continue

            metadata = _parse_frontmatter(skill_path)
            if metadata is None:
                continue

            name = metadata.get("name", child.name)
            metadata["_dir"] = str(child)
            self._registry[name] = metadata
            count += 1
            logger.debug("Discovered specialist: %s", name)

        logger.info("Discovered %d specialist(s) from %s", count, self.specialists_dir)
        return count

    def get(self, name: str) -> dict[str, Any] | None:
        """Get specialist metadata by name.

        Args:
            name: The specialist identifier.

        Returns:
            Metadata dict if found, else None.
        """
        return self._registry.get(name)

    def match_capabilities(self, capabilities: list[str]) -> list[str]:
        """Find specialists whose capabilities overlap with the requested list.

        Args:
            capabilities: List of capability identifiers to match.

        Returns:
            List of specialist names that have at least one matching capability.
        """
        requested = set(capabilities)
        matched: list[str] = []
        for name, meta in self._registry.items():
            specialist_caps = set(meta.get("capabilities", []))
            if specialist_caps & requested:
                matched.append(name)
        return matched

    def list_all(self) -> list[dict[str, Any]]:
        """List all registered specialists with metadata.

        Returns:
            List of metadata dicts for every registered specialist.
        """
        return list(self._registry.values())

    def register(self, name: str, metadata: dict[str, Any]) -> None:
        """Manually register a specialist at runtime.

        Args:
            name: Unique specialist identifier.
            metadata: Metadata dict (should follow SKILL.md frontmatter schema).
        """
        self._registry[name] = metadata
        logger.debug("Manually registered specialist: %s", name)
