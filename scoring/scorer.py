"""
Capability Scorer — weighted composite scoring (0-100) from multi-source signals.

Score = 40% discovery + 35% quality + 25% durability

Thresholds:
    80-100: Auto-scaffold specialist + priority review
    60-79:  Queue for evaluation
    40-59:  Watch list
    < 40:   Skip
"""

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from scoring.sources import (
    devhunt,
    github_trending,
    hackernews,
    ossinsight,
    reddit,
    therundown,
    trendshift,
)
from scoring.thresholds import SIGNAL_WEIGHTS

_GITHUB_API = "https://api.github.com"
_GH_TIMEOUT = 10.0

# Signals that belong to each scoring category (mirrors thresholds.py groupings)
_DISCOVERY_SIGNALS = frozenset(
    {
        "github_star_velocity",
        "github_trending_position",
        "hn_frontpage_score",
        "devhunt_upvotes",
        "rundown_mention",
    }
)
_QUALITY_SIGNALS = frozenset(
    {
        "readme_quality",
        "test_coverage",
        "api_surface_clarity",
        "license_compatibility",
        "maintenance_activity",
    }
)
_DURABILITY_SIGNALS = frozenset(
    {
        "contributor_diversity",
        "ossinsight_growth_curve",
        "trendshift_momentum",
        "dependency_health",
        "community_depth",
    }
)

# Licences that are fully compatible with typical open-source packaging
_PERMISSIVE_LICENSES = frozenset(
    {
        "mit",
        "apache-2.0",
        "bsd-2-clause",
        "bsd-3-clause",
        "isc",
        "unlicense",
        "0bsd",
    }
)
_COPYLEFT_LICENSES = frozenset({"gpl-2.0", "gpl-3.0", "lgpl-2.1", "lgpl-3.0", "agpl-3.0"})


@dataclass
class CapabilityScore:
    """Composite capability score for a GitHub repo."""

    repo: str
    total: float  # 0-100
    discovery: float  # 0-40
    quality: float  # 0-35
    durability: float  # 0-25
    timestamp: str
    sources: dict[str, float]  # source_name → normalized signal (0-1)

    @property
    def action(self) -> str:
        if self.total >= 80:
            return "auto_scaffold"
        elif self.total >= 60:
            return "evaluate"
        elif self.total >= 40:
            return "watch"
        return "skip"


# ---------------------------------------------------------------------------
# GitHub REST helpers
# ---------------------------------------------------------------------------


async def _fetch_github_repo_info(repo: str) -> dict[str, Any]:
    """Fetch the GitHub REST API response for a repo.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        Parsed JSON dict from ``GET /repos/{repo}``, or an empty dict on any
        network/API error so callers never need to guard against None.
    """
    try:
        async with httpx.AsyncClient(timeout=_GH_TIMEOUT) as client:
            response = await client.get(
                f"{_GITHUB_API}/repos/{repo}",
                headers={"Accept": "application/vnd.github+json"},
                follow_redirects=True,
            )
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
    except Exception:
        return {}


async def _fetch_github_contents(repo: str, path: str = "") -> list[dict[str, Any]]:
    """List directory contents via the GitHub Contents API.

    Returns an empty list on any error.
    """
    try:
        async with httpx.AsyncClient(timeout=_GH_TIMEOUT) as client:
            response = await client.get(
                f"{_GITHUB_API}/repos/{repo}/contents/{path}",
                headers={"Accept": "application/vnd.github+json"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
    except Exception:
        return []


async def _fetch_recent_commits(repo: str, since_days: int = 30) -> int:
    """Return the number of commits pushed in the last ``since_days`` days.

    Uses the GitHub commits endpoint with a ``since`` filter.  Returns 0 on
    any error so callers can treat absence as zero activity.
    """
    import datetime as dt_mod

    cutoff = (dt_mod.datetime.now(dt_mod.UTC) - dt_mod.timedelta(days=since_days)).isoformat()

    try:
        async with httpx.AsyncClient(timeout=_GH_TIMEOUT) as client:
            response = await client.get(
                f"{_GITHUB_API}/repos/{repo}/commits",
                params={"since": cutoff, "per_page": 100},
                headers={"Accept": "application/vnd.github+json"},
                follow_redirects=True,
            )
            response.raise_for_status()
            data = response.json()
            return len(data) if isinstance(data, list) else 0
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Quality signal computation
# ---------------------------------------------------------------------------


async def _compute_quality_signals(repo: str, repo_info: dict[str, Any]) -> dict[str, Any]:
    """Derive quality signals from GitHub API data.

    Signals returned (all floats in [0, 1]):
        readme_quality        — README exists and is substantial (>500 chars)
        test_coverage         — tests/ or test/ directory present
        api_surface_clarity   — Python files with type annotations present
        license_compatibility — permissive=1.0, copyleft=0.5, absent=0.0
        maintenance_activity  — commits in last 30 days, normalised
        dependency_health     — requirements.txt or pyproject.toml present
    """
    # Fetch root-level contents and recent commits concurrently
    contents, recent_commit_count = await asyncio.gather(
        _fetch_github_contents(repo),
        _fetch_recent_commits(repo, since_days=30),
    )

    filenames = {item.get("name", "").lower() for item in contents}
    types_by_name = {item.get("name", "").lower(): item.get("type", "") for item in contents}

    # --- readme_quality ---
    readme_names = {"readme.md", "readme.rst", "readme.txt", "readme"}
    readme_present = bool(readme_names & filenames)
    readme_size: int = 0
    for item in contents:
        if item.get("name", "").lower() in readme_names:
            readme_size = item.get("size", 0) or 0
            break
    if readme_present and readme_size > 500:
        readme_quality = min(1.0, readme_size / 5000)
    elif readme_present:
        readme_quality = 0.3
    else:
        readme_quality = 0.0

    # --- test_coverage: tests/ or test/ directory present ---
    test_dirs = {"tests", "test"}
    has_tests = bool(test_dirs & {name for name, t in types_by_name.items() if t == "dir"})
    test_coverage = 0.5 if has_tests else 0.0

    # --- api_surface_clarity: Python files with type hints ---
    # Check if any .py files exist at root; assume type hints if py.typed
    # or mypy.ini / pyrightconfig.json is present
    typed_markers = {"py.typed", "mypy.ini", "pyrightconfig.json", ".mypy.ini"}
    has_typed_markers = bool(typed_markers & filenames)
    has_python = any(name.endswith(".py") for name in filenames)
    if has_typed_markers:
        api_surface_clarity = 0.8
    elif has_python:
        api_surface_clarity = 0.4
    else:
        api_surface_clarity = 0.2  # non-Python repo still gets a floor

    # --- license_compatibility ---
    license_info = repo_info.get("license") or {}
    spdx = (license_info.get("spdx_id") or "").lower()
    if spdx in _PERMISSIVE_LICENSES:
        license_compatibility = 1.0
    elif spdx in _COPYLEFT_LICENSES:
        license_compatibility = 0.5
    elif spdx:
        license_compatibility = 0.3  # known but unusual license
    else:
        license_compatibility = 0.0

    # --- maintenance_activity: commits in last 30 days, cap at 30 ---
    maintenance_activity = min(1.0, recent_commit_count / 30.0)

    # --- dependency_health: requirements.txt or pyproject.toml present ---
    dep_files = {"requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "pipfile"}
    has_deps = bool(dep_files & filenames)
    dependency_health = 0.5 if has_deps else 0.0

    return {
        "readme_quality": round(readme_quality, 4),
        "test_coverage": round(test_coverage, 4),
        "api_surface_clarity": round(api_surface_clarity, 4),
        "license_compatibility": round(license_compatibility, 4),
        "maintenance_activity": round(maintenance_activity, 4),
        "dependency_health": round(dependency_health, 4),
    }


# ---------------------------------------------------------------------------
# Source signal name translation
# ---------------------------------------------------------------------------


def _translate_source_signals(raw: dict[str, Any], prefix: str) -> dict[str, Any]:
    """Apply a simple prefix mapping for source signals.

    Many scrapers return short keys (e.g. ``star_velocity``) while
    ``SIGNAL_WEIGHTS`` uses fully qualified names (e.g. ``github_star_velocity``).
    The caller passes the prefix and this function tries both the bare and
    prefixed key, returning only values that are floats (ignoring metadata).
    """
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if not isinstance(v, (int, float)):
            continue
        qualified = f"{prefix}_{k}" if not k.startswith(prefix) else k
        out[qualified] = float(v)
    return out


def _map_github_trending_signals(raw: dict[str, Any]) -> dict[str, Any]:
    """Translate github_trending.get_signals output to weight-key names."""
    mapping = {
        "star_velocity": "github_star_velocity",
        "trending_position": "github_trending_position",
    }
    return {mapping.get(k, k): float(v) for k, v in raw.items() if isinstance(v, (int, float))}


def _map_ossinsight_signals(raw: dict[str, Any]) -> dict[str, Any]:
    """Translate ossinsight.fetch_signals output to weight-key names."""
    mapping = {
        "growth_curve": "ossinsight_growth_curve",
        "contributor_diversity": "contributor_diversity",
    }
    return {mapping.get(k, k): float(v) for k, v in raw.items() if isinstance(v, (int, float))}


def _map_hackernews_signals(raw: dict[str, Any]) -> dict[str, Any]:
    """Translate hackernews.fetch_signals output to weight-key names."""
    mapping = {
        "frontpage_score": "hn_frontpage_score",
        "upvotes": "hn_frontpage_score",  # fallback alias
    }
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if not isinstance(v, (int, float)):
            continue
        out[mapping.get(k, k)] = float(v)
    return out


def _map_devhunt_signals(raw: dict[str, Any]) -> dict[str, Any]:
    """Translate devhunt.fetch_signals output to weight-key names."""
    mapping = {
        "upvotes": "devhunt_upvotes",
        "dev_tool_relevance": "devhunt_upvotes",  # fallback alias
    }
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if not isinstance(v, (int, float)):
            continue
        out[mapping.get(k, k)] = float(v)
    return out


def _map_therundown_signals(raw: dict[str, Any]) -> dict[str, Any]:
    """Translate therundown.fetch_signals output to weight-key names."""
    mapping = {
        "mention_count": "rundown_mention",
        "editorial_pick": "rundown_mention",
        "ai_relevance_score": "rundown_mention",
    }
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if not isinstance(v, (int, float)):
            continue
        out[mapping.get(k, k)] = float(v)
    return out


def _map_reddit_signals(raw: dict[str, Any]) -> dict[str, Any]:
    """Translate reddit.fetch_signals output to weight-key names."""
    out: dict[str, Any] = {}
    for _k, v in raw.items():
        if not isinstance(v, (int, float)):
            continue
        # take the max of all reddit signals as community_depth
        existing = out.get("community_depth", 0.0)
        out["community_depth"] = max(existing, float(v))
    return out


def _map_trendshift_signals(raw: dict[str, Any]) -> dict[str, Any]:
    """Translate trendshift.fetch_signals output to weight-key names."""
    mapping = {
        "momentum_score": "trendshift_momentum",
        "trending_duration": "trendshift_momentum",
    }
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if not isinstance(v, (int, float)):
            continue
        out[mapping.get(k, k)] = float(v)
    return out


# ---------------------------------------------------------------------------
# Safe source fetching
# ---------------------------------------------------------------------------


async def _safe_fetch(coro: Any) -> dict[str, Any]:
    """Await a source coroutine, returning {} on any exception."""
    try:
        result = await coro
        return result if isinstance(result, dict) else {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


async def score_repo(repo: str) -> CapabilityScore:
    """Score a GitHub repo using all available sources.

    Calls all discovery scrapers and the GitHub API concurrently, then
    computes a weighted composite score split into three sub-scores.

    Args:
        repo: GitHub repo in "owner/name" format.

    Returns:
        CapabilityScore with weighted composite total and category breakdown.
    """
    # Fetch everything in parallel
    (
        gh_trending_raw,
        ossinsight_raw,
        hn_raw,
        trendshift_raw,
        devhunt_raw,
        rundown_raw,
        reddit_raw,
        repo_info,
    ) = await asyncio.gather(
        _safe_fetch(github_trending.get_signals(repo)),
        _safe_fetch(ossinsight.fetch_signals(repo)),
        _safe_fetch(hackernews.fetch_signals(repo)),
        _safe_fetch(trendshift.fetch_signals(repo)),
        _safe_fetch(devhunt.fetch_signals(repo)),
        _safe_fetch(therundown.fetch_signals(repo)),
        _safe_fetch(reddit.fetch_signals(repo)),
        _fetch_github_repo_info(repo),
    )

    # Compute quality signals (needs repo_info and its own async I/O)
    quality_raw = await _compute_quality_signals(repo, repo_info)

    # Translate each source's keys to SIGNAL_WEIGHTS keys
    all_signals: dict[str, float] = {}
    all_signals.update(_map_github_trending_signals(gh_trending_raw))
    all_signals.update(_map_ossinsight_signals(ossinsight_raw))
    all_signals.update(_map_hackernews_signals(hn_raw))
    all_signals.update(_map_trendshift_signals(trendshift_raw))
    all_signals.update(_map_devhunt_signals(devhunt_raw))
    all_signals.update(_map_therundown_signals(rundown_raw))
    all_signals.update(_map_reddit_signals(reddit_raw))
    all_signals.update(quality_raw)  # keys already match SIGNAL_WEIGHTS

    # Default missing signals to 0.0
    for signal in SIGNAL_WEIGHTS:
        all_signals.setdefault(signal, 0.0)

    # Compute weighted total (0-100) and sub-totals
    total = sum(
        all_signals.get(signal, 0.0) * weight * 100 for signal, weight in SIGNAL_WEIGHTS.items()
    )
    discovery = sum(
        all_signals.get(signal, 0.0) * weight * 100
        for signal, weight in SIGNAL_WEIGHTS.items()
        if signal in _DISCOVERY_SIGNALS
    )
    quality = sum(
        all_signals.get(signal, 0.0) * weight * 100
        for signal, weight in SIGNAL_WEIGHTS.items()
        if signal in _QUALITY_SIGNALS
    )
    durability = sum(
        all_signals.get(signal, 0.0) * weight * 100
        for signal, weight in SIGNAL_WEIGHTS.items()
        if signal in _DURABILITY_SIGNALS
    )

    return CapabilityScore(
        repo=repo,
        total=round(total, 2),
        discovery=round(discovery, 2),
        quality=round(quality, 2),
        durability=round(durability, 2),
        timestamp=datetime.now(UTC).isoformat(),
        sources={k: round(v, 4) for k, v in all_signals.items()},
    )
