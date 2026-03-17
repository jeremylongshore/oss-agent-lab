"""
Tools for the DeerFlow specialist.

Implements the research → code generation → artifact creation pipeline inspired by
the bytedance/deer-flow SuperAgent pattern. Each tool is a pure function that can be
composed into the full pipeline or called independently.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any


def research_topic(
    topic: str,
    depth: str = "standard",
    sources: list[str] | None = None,
) -> dict[str, Any]:
    """Research a topic and return structured findings.

    Simulates the deer-flow research stage: gathers information, identifies key
    sources, and produces a structured summary with a confidence score.

    Args:
        topic: The subject to research.
        depth: Research depth — one of "shallow", "standard", or "deep".
            Deeper searches yield more findings but take longer.
        sources: Optional list of source URLs or identifiers to consult.
            When None the tool selects sources automatically.

    Returns:
        Dict with the following keys:
            findings (list[str]): Key findings from the research.
            sources_used (list[str]): Sources that were consulted.
            summary (str): A concise summary of the research.
            confidence (float): Confidence score in [0.0, 1.0].
    """
    if depth not in {"shallow", "standard", "deep"}:
        raise ValueError(f"depth must be 'shallow', 'standard', or 'deep'; got {depth!r}")

    depth_config: dict[str, dict[str, Any]] = {
        "shallow": {"finding_count": 2, "confidence": 0.65},
        "standard": {"finding_count": 4, "confidence": 0.80},
        "deep": {"finding_count": 7, "confidence": 0.92},
    }
    cfg = depth_config[depth]
    finding_count: int = cfg["finding_count"]
    base_confidence: float = cfg["confidence"]

    effective_sources = sources if sources else [f"auto-source-{i}" for i in range(1, 4)]
    findings = [f"Finding {i + 1} on '{topic}' (depth={depth})" for i in range(finding_count)]
    summary = (
        f"Research on '{topic}' completed at {depth!r} depth. "
        f"{len(findings)} findings identified across {len(effective_sources)} sources."
    )
    confidence = min(1.0, base_confidence + 0.01 * len(effective_sources))

    return {
        "findings": findings,
        "sources_used": effective_sources,
        "summary": summary,
        "confidence": round(confidence, 4),
    }


def generate_code(
    specification: str,
    language: str = "python",
    style: str = "clean",
) -> dict[str, Any]:
    """Generate code from a natural-language specification.

    Simulates the deer-flow code-generation stage: produces an implementation,
    matching tests, and an explanatory comment for a given specification.

    Args:
        specification: Natural-language description of the code to produce.
        language: Target programming language (e.g. "python", "typescript").
        style: Coding style guide — one of "clean", "verbose", or "minimal".

    Returns:
        Dict with the following keys:
            code (str): The generated implementation.
            language (str): The language used (echoed from input).
            tests (str): A skeleton test suite for the generated code.
            explanation (str): Short explanation of the generated code.
    """
    if not specification.strip():
        raise ValueError("specification must not be empty")

    known_styles = {"clean", "verbose", "minimal"}
    if style not in known_styles:
        raise ValueError(f"style must be one of {sorted(known_styles)!r}; got {style!r}")

    slug = specification[:40].strip().replace(" ", "_").lower()
    func_name = "".join(ch if ch.isalnum() or ch == "_" else "" for ch in slug) or "generated"

    if language == "python":
        code = (
            f"def {func_name}(*args, **kwargs):\n"
            f'    """Auto-generated: {specification[:60]}"""\n'
            f"    # TODO: implement based on specification\n"
            f"    raise NotImplementedError\n"
        )
        tests = (
            f"import pytest\n\n\n"
            f"def test_{func_name}_not_implemented():\n"
            f"    with pytest.raises(NotImplementedError):\n"
            f"        {func_name}()\n"
        )
    else:
        code = f"// Generated {language} stub for: {specification[:60]}\n// TODO: implement\n"
        tests = f"// Tests for {language} stub\n// TODO: add tests\n"

    explanation = (
        f"Generated a {style!r}-style {language} implementation for: {specification[:80]}. "
        "The stub raises NotImplementedError and is ready for real logic."
    )

    return {
        "code": code,
        "language": language,
        "tests": tests,
        "explanation": explanation,
    }


def create_artifact(
    content: dict[str, Any],
    artifact_type: str = "report",
    format: str = "markdown",
) -> dict[str, Any]:
    """Create a final deliverable artifact from pipeline outputs.

    Simulates the deer-flow creation stage: packages research findings and
    generated code into a versioned artifact ready for downstream consumption.

    Args:
        content: Dict containing pipeline outputs to embed in the artifact
            (e.g. research findings, generated code, summaries).
        artifact_type: Logical type of the artifact — e.g. "report",
            "notebook", "package", or "summary".
        format: Output format — e.g. "markdown", "json", "html".

    Returns:
        Dict with the following keys:
            artifact_id (str): Stable hash-based identifier for this artifact.
            content (dict[str, Any]): The packaged artifact body.
            format (str): The format used (echoed from input).
            metadata (dict[str, Any]): Creation timestamp, type, and size info.
    """
    if not content:
        raise ValueError("content must not be empty")

    known_types = {"report", "notebook", "package", "summary"}
    known_formats = {"markdown", "json", "html"}
    if artifact_type not in known_types:
        raise ValueError(
            f"artifact_type must be one of {sorted(known_types)!r}; got {artifact_type!r}"
        )
    if format not in known_formats:
        raise ValueError(f"format must be one of {sorted(known_formats)!r}; got {format!r}")

    raw = str(sorted(content.items())) + artifact_type + format
    artifact_id = "artifact-" + hashlib.sha1(raw.encode()).hexdigest()[:12]

    packaged: dict[str, Any] = {
        "type": artifact_type,
        "format": format,
        "body": content,
    }

    metadata: dict[str, Any] = {
        "artifact_type": artifact_type,
        "format": format,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "content_keys": list(content.keys()),
        "size_hint": len(str(content)),
    }

    return {
        "artifact_id": artifact_id,
        "content": packaged,
        "format": format,
        "metadata": metadata,
    }
