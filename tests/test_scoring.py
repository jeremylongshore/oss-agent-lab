"""Tests for scoring engine components."""

from __future__ import annotations

import json

import pytest

from scoring.index import IndexEntry, TemporalIndex
from scoring.scorer import CapabilityScore
from scoring.thresholds import (
    AUTO_SCAFFOLD_THRESHOLD,
    EVALUATE_THRESHOLD,
    SIGNAL_WEIGHTS,
    WATCH_THRESHOLD,
)


class TestCapabilityScore:
    def test_auto_scaffold(self) -> None:
        score = CapabilityScore(
            repo="test/repo", total=85.0, discovery=34.0, quality=30.0,
            durability=21.0, timestamp="2026-03-16", sources={}
        )
        assert score.action == "auto_scaffold"

    def test_evaluate(self) -> None:
        score = CapabilityScore(
            repo="test/repo", total=70.0, discovery=28.0, quality=24.5,
            durability=17.5, timestamp="2026-03-16", sources={}
        )
        assert score.action == "evaluate"

    def test_watch(self) -> None:
        score = CapabilityScore(
            repo="test/repo", total=50.0, discovery=20.0, quality=17.5,
            durability=12.5, timestamp="2026-03-16", sources={}
        )
        assert score.action == "watch"

    def test_skip(self) -> None:
        score = CapabilityScore(
            repo="test/repo", total=30.0, discovery=12.0, quality=10.5,
            durability=7.5, timestamp="2026-03-16", sources={}
        )
        assert score.action == "skip"

    def test_boundary_80(self) -> None:
        score = CapabilityScore(
            repo="x/y", total=80.0, discovery=32.0, quality=28.0,
            durability=20.0, timestamp="2026-03-16", sources={}
        )
        assert score.action == "auto_scaffold"

    def test_boundary_60(self) -> None:
        score = CapabilityScore(
            repo="x/y", total=60.0, discovery=24.0, quality=21.0,
            durability=15.0, timestamp="2026-03-16", sources={}
        )
        assert score.action == "evaluate"

    def test_boundary_40(self) -> None:
        score = CapabilityScore(
            repo="x/y", total=40.0, discovery=16.0, quality=14.0,
            durability=10.0, timestamp="2026-03-16", sources={}
        )
        assert score.action == "watch"


class TestThresholds:
    def test_threshold_values(self) -> None:
        assert AUTO_SCAFFOLD_THRESHOLD == 80
        assert EVALUATE_THRESHOLD == 60
        assert WATCH_THRESHOLD == 40

    def test_signal_weights_sum_to_one(self) -> None:
        assert abs(sum(SIGNAL_WEIGHTS.values()) - 1.0) < 0.001

    def test_all_signals_present(self) -> None:
        assert len(SIGNAL_WEIGHTS) == 15

    def test_discovery_signals(self) -> None:
        discovery_keys = [
            "github_star_velocity", "github_trending_position",
            "hn_frontpage_score", "devhunt_upvotes", "rundown_mention",
        ]
        for key in discovery_keys:
            assert key in SIGNAL_WEIGHTS

    def test_quality_signals(self) -> None:
        quality_keys = [
            "readme_quality", "test_coverage", "api_surface_clarity",
            "license_compatibility", "maintenance_activity",
        ]
        for key in quality_keys:
            assert key in SIGNAL_WEIGHTS

    def test_durability_signals(self) -> None:
        durability_keys = [
            "contributor_diversity", "ossinsight_growth_curve",
            "trendshift_momentum", "dependency_health", "community_depth",
        ]
        for key in durability_keys:
            assert key in SIGNAL_WEIGHTS


# ---------------------------------------------------------------------------
# Temporal Index
# ---------------------------------------------------------------------------


class TestIndexEntry:
    def test_create(self) -> None:
        e = IndexEntry(repo="a/b", score=75.0, timestamp="2026-03-16", trend="rising")
        assert e.repo == "a/b"
        assert e.score == 75.0
        assert e.trend == "rising"


class TestTemporalIndex:
    def test_add_and_get_history(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 70.0, "2026-03-10", "new"))
        idx.add(IndexEntry("a/b", 75.0, "2026-03-17", "rising"))
        history = idx.get_repo_history("a/b")
        assert len(history) == 2

    def test_get_rising(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 75.0, "t1", "rising"))
        idx.add(IndexEntry("c/d", 50.0, "t1", "rising"))
        idx.add(IndexEntry("e/f", 80.0, "t1", "peaked"))
        rising = idx.get_rising(min_score=60.0)
        assert len(rising) == 1
        assert rising[0].repo == "a/b"

    def test_detect_trend_new(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 70.0, "t1", "new"))
        assert idx.detect_trend("a/b") == "new"

    def test_detect_trend_rising(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 60.0, "t1", "new"))
        idx.add(IndexEntry("a/b", 70.0, "t2", "rising"))
        assert idx.detect_trend("a/b") == "rising"

    def test_detect_trend_declining(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 80.0, "t1", "rising"))
        idx.add(IndexEntry("a/b", 50.0, "t2", "declining"))
        assert idx.detect_trend("a/b") == "declining"

    def test_detect_trend_peaked(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 80.0, "t1", "rising"))
        idx.add(IndexEntry("a/b", 78.0, "t2", "peaked"))
        assert idx.detect_trend("a/b") == "peaked"

    def test_add_score(self) -> None:
        idx = TemporalIndex()
        score = CapabilityScore(
            repo="x/y", total=85.0, discovery=34.0, quality=30.0,
            durability=21.0, timestamp="2026-03-16", sources={}
        )
        entry = idx.add_score(score)
        assert entry.repo == "x/y"
        assert entry.score == 85.0
        assert entry.trend == "new"  # first entry
        assert len(idx.entries) == 1

    def test_add_score_detects_rising(self) -> None:
        idx = TemporalIndex()
        s1 = CapabilityScore(
            repo="x/y", total=60.0, discovery=24.0, quality=21.0,
            durability=15.0, timestamp="t1", sources={}
        )
        s2 = CapabilityScore(
            repo="x/y", total=75.0, discovery=30.0, quality=26.0,
            durability=19.0, timestamp="t2", sources={}
        )
        s3 = CapabilityScore(
            repo="x/y", total=85.0, discovery=34.0, quality=30.0,
            durability=21.0, timestamp="t3", sources={}
        )
        idx.add_score(s1)  # trend = "new" (first entry)
        idx.add_score(s2)  # trend = "new" (only 1 prior entry)
        entry3 = idx.add_score(s3)  # now 2 prior entries → can detect trend
        assert entry3.trend == "rising"

    def test_to_json_and_from_json(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 70.0, "2026-03-16", "rising"))
        idx.add(IndexEntry("c/d", 50.0, "2026-03-16", "new"))

        json_str = idx.to_json()
        parsed = json.loads(json_str)
        assert len(parsed["entries"]) == 2

        restored = TemporalIndex.from_json(json_str)
        assert len(restored.entries) == 2
        assert restored.entries[0].repo == "a/b"
        assert restored.entries[1].score == 50.0

    def test_from_json_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid JSON"):
            TemporalIndex.from_json("not json {{{")

    def test_get_actionable(self) -> None:
        idx = TemporalIndex()
        idx.add(IndexEntry("a/b", 75.0, "t1", "rising"))
        idx.add(IndexEntry("c/d", 80.0, "t1", "peaked"))
        idx.add(IndexEntry("e/f", 65.0, "t1", "new"))
        idx.add(IndexEntry("g/h", 50.0, "t1", "rising"))

        actionable = idx.get_actionable(min_score=60.0)
        names = [e.repo for e in actionable]
        assert "a/b" in names  # rising, score >= 60
        assert "e/f" in names  # new, score >= 60
        assert "c/d" not in names  # peaked
        assert "g/h" not in names  # score < 60
