"""
Tools for the RepoScanner specialist.

Implements repo analysis, capability scoring, and specialist scaffolding
patterns used by the meta-specialist pipeline. All three tools are designed
to operate without live network access: scan_repo and evaluate_score produce
deterministic mock data derived from the repo name, while scaffold_specialist
performs real file-system I/O against the _template directory when it exists.

Side effects:
    scaffold_specialist: Creates directories and files on the local file system.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SPECIALISTS_DIR = Path(__file__).resolve().parents[1]  # agents/specialists/
_AUTO_SCAFFOLD_THRESHOLD = 80.0


# ---------------------------------------------------------------------------
# Public tools
# ---------------------------------------------------------------------------


def scan_repo(repo: str) -> dict[str, Any]:
    """Analyse a GitHub repo for specialist-wrapping potential.

    Produces a realistic assessment of the repo's suitability for wrapping as
    an OSS Agent Lab specialist. In production this function would call the
    GitHub REST API; here the outputs are derived deterministically from the
    repo string so the full pipeline can be exercised without network access.

    Args:
        repo: GitHub repo in ``"owner/name"`` format. Case-insensitive;
            normalised to lowercase internally.

    Returns:
        A dict with:
            - ``repo``: The normalised repo slug.
            - ``name_suggestion``: Snake-case specialist name derived from the
              repo's project component.
            - ``capabilities_detected``: List of inferred capability strings.
            - ``has_python``: Whether Python source files appear likely present.
            - ``has_tests``: Whether a test suite appears likely present.
            - ``has_readme``: Whether a README appears likely present.
            - ``recommendation``: One of ``"auto_scaffold"``, ``"evaluate"``,
              ``"watch"``, or ``"skip"``.

    Raises:
        ValueError: If ``repo`` is empty or does not contain a ``"/"`` separator.
    """
    if not repo:
        raise ValueError("repo must not be empty")
    if "/" not in repo:
        raise ValueError(f"repo must be in 'owner/name' format, got: {repo!r}")

    slug = repo.lower().strip()
    _owner, name = slug.split("/", 1)

    # Derive a stable integer seed for deterministic simulation.
    seed = sum(ord(c) for c in slug)

    # Suggest a snake_case specialist name from the repo's project component.
    name_suggestion = name.replace("-", "_").replace(".", "_")

    # Infer capabilities from common keywords in the repo name.
    capability_keywords: dict[str, str] = {
        "agent": "agent_orchestration",
        "llm": "llm_integration",
        "research": "research_automation",
        "browser": "browser_control",
        "graph": "knowledge_graph",
        "stock": "financial_analysis",
        "predict": "prediction",
        "scan": "repo_analysis",
        "scaffold": "auto_scaffold",
        "search": "semantic_search",
        "vision": "computer_vision",
        "code": "code_generation",
        "chat": "conversational_ai",
        "data": "data_pipeline",
        "test": "test_generation",
    }
    capabilities_detected: list[str] = [
        cap for kw, cap in capability_keywords.items() if kw in name
    ]
    if not capabilities_detected:
        # Fallback: derive two generic capabilities from seed.
        fallbacks = [
            "api_wrapping",
            "workflow_automation",
            "tool_integration",
            "data_processing",
            "model_serving",
        ]
        capabilities_detected = [
            fallbacks[seed % len(fallbacks)],
            fallbacks[(seed + 3) % len(fallbacks)],
        ]

    # Simulate structural presence signals from seed.
    has_python = (seed % 5) != 0  # ~80% of repos
    has_tests = (seed % 3) != 0  # ~67% of repos
    has_readme = (seed % 7) != 0  # ~86% of repos

    # Simple recommendation derived from simulated score.
    estimated = _estimate_score_from_seed(seed)
    if estimated >= 80:
        recommendation = "auto_scaffold"
    elif estimated >= 60:
        recommendation = "evaluate"
    elif estimated >= 40:
        recommendation = "watch"
    else:
        recommendation = "skip"

    return {
        "repo": slug,
        "name_suggestion": name_suggestion,
        "capabilities_detected": capabilities_detected,
        "has_python": has_python,
        "has_tests": has_tests,
        "has_readme": has_readme,
        "recommendation": recommendation,
    }


def scaffold_specialist(repo: str, name: str) -> dict[str, Any]:
    """Generate a new specialist directory by copying the _template skeleton.

    Copies ``agents/specialists/_template/`` into a new directory named
    ``agents/specialists/<name>/``. If the template directory does not exist
    (e.g. in test environments) the function returns a simulated result rather
    than raising so that the pipeline remains unblocked.

    Args:
        repo: GitHub repo in ``"owner/name"`` format. Recorded in the result
            for provenance but not used for file-system operations.
        name: Snake-case name for the new specialist directory and class.
            Must be a valid Python identifier after normalisation.

    Returns:
        A dict with:
            - ``status``: ``"created"`` when files were written to disk,
              ``"simulated"`` when the template was absent.
            - ``path``: Absolute path to the new specialist directory.
            - ``files``: List of file names written (or that would be written).

    Raises:
        ValueError: If ``name`` is empty.
        FileExistsError: If the target directory already exists.
    """
    if not name:
        raise ValueError("name must not be empty")

    safe_name = name.replace("-", "_").replace(".", "_")
    template_dir = _SPECIALISTS_DIR / "_template"
    target_dir = _SPECIALISTS_DIR / safe_name

    expected_files = ["__init__.py", "agent.py", "tools.py", "SKILL.md"]

    if target_dir.exists():
        raise FileExistsError(f"Specialist directory already exists: {target_dir}")

    if template_dir.exists() and template_dir.is_dir():
        shutil.copytree(str(template_dir), str(target_dir))
        files = [entry.name for entry in sorted(target_dir.iterdir()) if entry.is_file()]
        status = "created"
    else:
        # Template absent — return a simulated result so the pipeline proceeds.
        files = expected_files
        status = "simulated"

    return {
        "status": status,
        "path": str(target_dir),
        "files": files,
    }


def evaluate_score(repo: str) -> dict[str, Any]:
    """Quickly evaluate a repo's composite capability score.

    Produces a capability score compatible with the Capability Scoring Engine's
    0-100 scale and threshold semantics (auto_scaffold >= 80, evaluate >= 60,
    watch >= 40, skip < 40). In production this would delegate to
    ``scoring.scorer.score_repo``; here the score is derived deterministically
    from the repo name to avoid network dependencies during pipeline testing.

    Args:
        repo: GitHub repo in ``"owner/name"`` format.

    Returns:
        A dict with:
            - ``repo``: The normalised repo slug.
            - ``estimated_score``: Float in [0.0, 100.0].
            - ``action``: One of ``"auto_scaffold"``, ``"evaluate"``,
              ``"watch"``, or ``"skip"``.
            - ``signals``: Dict of simulated sub-scores used in scoring.

    Raises:
        ValueError: If ``repo`` is empty or lacks a ``"/"`` separator.
    """
    if not repo:
        raise ValueError("repo must not be empty")
    if "/" not in repo:
        raise ValueError(f"repo must be in 'owner/name' format, got: {repo!r}")

    slug = repo.lower().strip()
    seed = sum(ord(c) for c in slug)

    estimated_score = _estimate_score_from_seed(seed)

    # Simulate the three sub-score categories from scorer.py.
    # Discovery: 0-40, Quality: 0-35, Durability: 0-25
    discovery = round((seed % 41) * (estimated_score / 100.0), 2)
    quality = round((seed % 36) * (estimated_score / 100.0), 2)
    durability = round(max(0.0, estimated_score - discovery - quality), 2)

    if estimated_score >= 80:
        action = "auto_scaffold"
    elif estimated_score >= 60:
        action = "evaluate"
    elif estimated_score >= 40:
        action = "watch"
    else:
        action = "skip"

    signals: dict[str, float] = {
        "discovery": discovery,
        "quality": quality,
        "durability": durability,
        "github_star_velocity": round(min(1.0, (seed % 100) / 100.0), 4),
        "readme_quality": round(min(1.0, (seed % 80) / 80.0), 4),
        "test_coverage": round(min(1.0, (seed % 60) / 60.0), 4),
        "maintenance_activity": round(min(1.0, (seed % 30) / 30.0), 4),
        "community_depth": round(min(1.0, (seed % 50) / 50.0), 4),
    }

    return {
        "repo": slug,
        "estimated_score": estimated_score,
        "action": action,
        "signals": signals,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _estimate_score_from_seed(seed: int) -> float:
    """Derive a deterministic score in [0.0, 100.0] from an integer seed.

    The function maps the seed into the full score range while giving a
    realistic distribution: most repos land in the 40-80 range, with tails
    for exceptional and poor performers.

    Args:
        seed: Non-negative integer derived from the repo slug.

    Returns:
        Float score in [0.0, 100.0] rounded to two decimal places.
    """
    # Map seed into [20, 100] via modulo — gives a realistic spread.
    base = 20.0 + (seed % 81)  # range: [20, 100]
    # Apply a small fractional component for sub-integer variation.
    fraction = ((seed * 7) % 100) / 1000.0  # range: [0.000, 0.099]
    return round(min(100.0, base + fraction), 2)
