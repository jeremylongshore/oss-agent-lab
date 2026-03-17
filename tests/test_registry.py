"""Tests for SpecialistRegistry — auto-discovery from SKILL.md frontmatter."""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.router.registry import SpecialistRegistry, _parse_frontmatter


@pytest.fixture
def tmp_specialists(tmp_path: Path) -> Path:
    """Create a temp specialists dir with sample SKILL.md files."""
    # Valid specialist
    spec1 = tmp_path / "autoresearch"
    spec1.mkdir()
    (spec1 / "SKILL.md").write_text(
        "---\n"
        "name: autoresearch\n"
        "description: Self-improving research loops\n"
        "source_repo: karpathy/autoresearch\n"
        "capabilities:\n"
        "  - research\n"
        "  - ai\n"
        "output_formats:\n"
        "  - python_api\n"
        "  - cli\n"
        "---\n"
        "\n# Autoresearch\n"
    )

    # Another valid specialist
    spec2 = tmp_path / "stock_analyst"
    spec2.mkdir()
    (spec2 / "SKILL.md").write_text(
        "---\n"
        "name: stock_analyst\n"
        "description: Financial analysis\n"
        "source_repo: virattt/ai-hedge-fund\n"
        "capabilities:\n"
        "  - analyze\n"
        "  - finance\n"
        "output_formats:\n"
        "  - python_api\n"
        "---\n"
        "\n# Stock Analyst\n"
    )

    # Template dir (should be skipped)
    template = tmp_path / "_template"
    template.mkdir()
    (template / "SKILL.md").write_text("---\nname: template\n---\n")

    # Dir without SKILL.md (should be skipped)
    no_skill = tmp_path / "incomplete"
    no_skill.mkdir()

    # Invalid YAML frontmatter
    bad_yaml = tmp_path / "bad_yaml"
    bad_yaml.mkdir()
    (bad_yaml / "SKILL.md").write_text("---\n: invalid: yaml: [\n---\n")

    # No frontmatter
    no_fm = tmp_path / "no_frontmatter"
    no_fm.mkdir()
    (no_fm / "SKILL.md").write_text("# Just a readme, no frontmatter\n")

    return tmp_path


class TestParseFromtmatter:
    def test_valid_frontmatter(self, tmp_path: Path) -> None:
        skill = tmp_path / "SKILL.md"
        skill.write_text("---\nname: test\ncapabilities:\n  - a\n---\nbody\n")
        result = _parse_frontmatter(skill)
        assert result is not None
        assert result["name"] == "test"
        assert result["capabilities"] == ["a"]

    def test_missing_file(self, tmp_path: Path) -> None:
        result = _parse_frontmatter(tmp_path / "nonexistent.md")
        assert result is None

    def test_no_frontmatter_markers(self, tmp_path: Path) -> None:
        skill = tmp_path / "SKILL.md"
        skill.write_text("just text, no dashes")
        result = _parse_frontmatter(skill)
        assert result is None

    def test_unclosed_frontmatter(self, tmp_path: Path) -> None:
        skill = tmp_path / "SKILL.md"
        skill.write_text("---\nname: test\nno closing dashes")
        result = _parse_frontmatter(skill)
        assert result is None

    def test_non_dict_frontmatter(self, tmp_path: Path) -> None:
        skill = tmp_path / "SKILL.md"
        skill.write_text("---\n- just a list\n- not a mapping\n---\n")
        result = _parse_frontmatter(skill)
        assert result is None


class TestSpecialistRegistry:
    def test_discover_finds_valid_specialists(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        count = registry.discover()
        assert count == 2  # autoresearch + stock_analyst

    def test_discover_skips_template(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        assert registry.get("template") is None

    def test_discover_skips_invalid(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        assert registry.get("bad_yaml") is None
        assert registry.get("no_frontmatter") is None
        assert registry.get("incomplete") is None

    def test_get_returns_metadata(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        meta = registry.get("autoresearch")
        assert meta is not None
        assert meta["name"] == "autoresearch"
        assert meta["source_repo"] == "karpathy/autoresearch"

    def test_get_returns_none_for_unknown(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        assert registry.get("nonexistent") is None

    def test_match_capabilities(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        matched = registry.match_capabilities(["research"])
        assert "autoresearch" in matched
        assert "stock_analyst" not in matched

    def test_match_capabilities_multiple(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        matched = registry.match_capabilities(["research", "finance"])
        assert "autoresearch" in matched
        assert "stock_analyst" in matched

    def test_match_capabilities_none_found(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        matched = registry.match_capabilities(["nonexistent_capability"])
        assert matched == []

    def test_list_all(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.discover()
        all_specs = registry.list_all()
        assert len(all_specs) == 2

    def test_manual_register(self, tmp_specialists: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_specialists)
        registry.register("custom", {"name": "custom", "capabilities": ["custom_cap"]})
        assert registry.get("custom") is not None
        matched = registry.match_capabilities(["custom_cap"])
        assert "custom" in matched

    def test_discover_nonexistent_dir(self, tmp_path: Path) -> None:
        registry = SpecialistRegistry(specialists_dir=tmp_path / "nope")
        count = registry.discover()
        assert count == 0
