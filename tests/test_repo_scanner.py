"""Tests for repo_scanner meta-specialist."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytest
from helpers import make_request

from oss_agent_lab.contracts import SpecialistResponse


class TestRepoScanner:
    @pytest.mark.asyncio
    async def test_execute(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        import agents.specialists.repo_scanner.tools as tools_mod
        from agents.specialists.repo_scanner.agent import RepoScannerSpecialist

        # Redirect scaffold_specialist to a temp dir so execute() never touches the real tree.
        monkeypatch.setattr(tools_mod, "_SPECIALISTS_DIR", tmp_path)

        s = RepoScannerSpecialist()
        req = make_request(
            "repo_scanner",
            "Scan myorg/mypkg and scaffold a specialist",
            action="scan",
            domain="code",
            repo="myorg/mypkg",
        )
        resp = await s.execute(req)

        assert isinstance(resp, SpecialistResponse)
        assert resp.status == "success"
        assert resp.specialist_name == "repo_scanner"

    def test_attributes(self) -> None:
        from agents.specialists.repo_scanner.agent import RepoScannerSpecialist

        s = RepoScannerSpecialist()
        assert s.name == "repo_scanner"
        assert isinstance(s.source_repo, str) and len(s.source_repo) > 0
        assert "auto_scaffold" in s.capabilities
        assert len(s.tools) >= 3

    def test_tools_scan_repo(self) -> None:
        from agents.specialists.repo_scanner.tools import scan_repo

        result = scan_repo("test/repo")
        assert isinstance(result, dict)
        # Must return keys needed for downstream scaffolding decisions.
        expected_keys = {
            "repo",
            "name_suggestion",
            "capabilities_detected",
            "has_python",
            "has_readme",
            "recommendation",
        }
        assert expected_keys.issubset(result.keys()), (
            f"scan_repo result missing keys. Got: {set(result.keys())}"
        )

    def test_tools_scaffold_specialist(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import agents.specialists.repo_scanner.tools as tools_mod
        from agents.specialists.repo_scanner.tools import scaffold_specialist

        # Redirect the tool's filesystem root to a temp directory so the test
        # is hermetic and never touches the real agents/specialists/ tree.
        monkeypatch.setattr(tools_mod, "_SPECIALISTS_DIR", tmp_path)

        result = scaffold_specialist("test/repo", "my_scaffolded_specialist")
        assert isinstance(result, dict)
        assert "status" in result

    def test_tools_evaluate_score(self) -> None:
        from agents.specialists.repo_scanner.tools import evaluate_score

        result = evaluate_score("test/repo")
        assert isinstance(result, dict)
        assert "estimated_score" in result

    def test_skill_metadata(self) -> None:
        from agents.specialists.repo_scanner.agent import RepoScannerSpecialist

        s = RepoScannerSpecialist()
        meta = s.get_skill_metadata()

        required_fields = {"name", "description", "source_repo", "capabilities", "tools"}
        for field_name in required_fields:
            assert field_name in meta, f"get_skill_metadata() missing field: {field_name!r}"

        assert meta["name"] == "repo_scanner"
        assert len(meta["capabilities"]) >= 1
        assert len(meta["tools"]) >= 1


class TestRepoScannerConsistency:
    """Verify repo_scanner satisfies the full BaseSpecialist contract."""

    REQUIRED_ATTRS: ClassVar[list[str]] = [
        "name",
        "description",
        "source_repo",
        "capabilities",
        "output_formats",
        "tools",
    ]

    def test_all_required_attributes_present(self) -> None:
        from agents.specialists.repo_scanner.agent import RepoScannerSpecialist

        s = RepoScannerSpecialist()
        for attr in self.REQUIRED_ATTRS:
            assert hasattr(s, attr), f"RepoScannerSpecialist missing attribute: {attr!r}"

    def test_output_formats_non_empty(self) -> None:
        from agents.specialists.repo_scanner.agent import RepoScannerSpecialist

        s = RepoScannerSpecialist()
        assert len(s.output_formats) >= 1

    @pytest.mark.asyncio
    async def test_execute_result_contains_scaffold_info(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """execute() result must include scaffolding metadata for the requested repo."""
        import agents.specialists.repo_scanner.tools as tools_mod
        from agents.specialists.repo_scanner.agent import RepoScannerSpecialist

        monkeypatch.setattr(tools_mod, "_SPECIALISTS_DIR", tmp_path)

        s = RepoScannerSpecialist()
        req = make_request(
            "repo_scanner",
            "Scan someowner/someproject",
            action="scan",
            domain="code",
            repo="someowner/someproject",
        )
        resp = await s.execute(req)
        assert isinstance(resp.result, dict)
        # Result should surface the repo that was scanned.
        result_str = str(resp.result)
        assert "someowner" in result_str or "someproject" in result_str or "repo" in result_str
