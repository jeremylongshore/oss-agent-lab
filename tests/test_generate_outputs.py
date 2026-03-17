"""Tests for multi-format output generation."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestGenerateOutputs:
    def test_generate_outputs_creates_files(self, tmp_path: Path) -> None:
        """generate_outputs() returns a dict of 5 format keys, each pointing to an existing file."""
        from scripts.generate_outputs import generate_outputs

        specialist_dir = Path("agents/specialists/autoresearch")
        result = generate_outputs(specialist_dir, output_dir=tmp_path)

        assert isinstance(result, dict)
        assert len(result) == 5, f"Expected 5 output paths, got {len(result)}: {list(result)}"

        for fmt_name, output_path in result.items():
            assert isinstance(output_path, Path), (
                f"Value for {fmt_name!r} should be a Path, got {type(output_path)}"
            )
            assert output_path.exists(), (
                f"Output file for {fmt_name!r} does not exist: {output_path}"
            )

    def test_generate_outputs_python_api(self, tmp_path: Path) -> None:
        """Generated Python API file must be syntactically valid Python."""
        from scripts.generate_outputs import generate_outputs

        specialist_dir = Path("agents/specialists/autoresearch")
        result = generate_outputs(specialist_dir, output_dir=tmp_path)

        assert "python_api" in result, f"'python_api' key missing. Got: {list(result)}"
        python_file = result["python_api"]
        source = python_file.read_text(encoding="utf-8")
        try:
            compile(source, str(python_file), "exec")
        except SyntaxError as exc:
            pytest.fail(f"Generated Python API file has invalid syntax: {exc}")

    def test_generate_outputs_cli(self, tmp_path: Path) -> None:
        """Generated CLI file must be syntactically valid Python."""
        from scripts.generate_outputs import generate_outputs

        specialist_dir = Path("agents/specialists/autoresearch")
        result = generate_outputs(specialist_dir, output_dir=tmp_path)

        assert "cli" in result, f"'cli' key missing. Got: {list(result)}"
        cli_file = result["cli"]
        source = cli_file.read_text(encoding="utf-8")
        try:
            compile(source, str(cli_file), "exec")
        except SyntaxError as exc:
            pytest.fail(f"Generated CLI file has invalid syntax: {exc}")

    def test_generate_outputs_all_formats(self, tmp_path: Path) -> None:
        """All 5 canonical output formats must be present in the result."""
        from scripts.generate_outputs import generate_outputs

        specialist_dir = Path("agents/specialists/autoresearch")
        result = generate_outputs(specialist_dir, output_dir=tmp_path)

        expected_formats = {"python_api", "cli", "mcp_server", "agent_skill", "rest_api"}
        missing = expected_formats - set(result.keys())
        assert not missing, f"Missing output formats: {missing}"

        for fmt in expected_formats:
            assert result[fmt].exists(), f"File for format {fmt!r} does not exist: {result[fmt]}"

    def test_generate_outputs_invalid_dir(self, tmp_path: Path) -> None:
        """generate_outputs() must raise an error when given a nonexistent specialist dir."""
        from scripts.generate_outputs import generate_outputs

        nonexistent = tmp_path / "does_not_exist"
        with pytest.raises((FileNotFoundError, ValueError, NotADirectoryError)):
            generate_outputs(nonexistent, output_dir=tmp_path)
