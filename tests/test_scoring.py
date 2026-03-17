"""Tests for scoring engine components."""
import pytest
from scoring.scorer import CapabilityScore
from scoring.thresholds import (
    AUTO_SCAFFOLD_THRESHOLD,
    EVALUATE_THRESHOLD,
    WATCH_THRESHOLD,
    SIGNAL_WEIGHTS,
)


class TestCapabilityScore:
    def test_auto_scaffold(self):
        score = CapabilityScore(
            repo="test/repo", total=85.0, discovery=34.0, quality=30.0,
            durability=21.0, timestamp="2026-03-16", sources={}
        )
        assert score.action == "auto_scaffold"

    def test_evaluate(self):
        score = CapabilityScore(
            repo="test/repo", total=70.0, discovery=28.0, quality=24.5,
            durability=17.5, timestamp="2026-03-16", sources={}
        )
        assert score.action == "evaluate"

    def test_watch(self):
        score = CapabilityScore(
            repo="test/repo", total=50.0, discovery=20.0, quality=17.5,
            durability=12.5, timestamp="2026-03-16", sources={}
        )
        assert score.action == "watch"

    def test_skip(self):
        score = CapabilityScore(
            repo="test/repo", total=30.0, discovery=12.0, quality=10.5,
            durability=7.5, timestamp="2026-03-16", sources={}
        )
        assert score.action == "skip"


class TestThresholds:
    def test_threshold_values(self):
        assert AUTO_SCAFFOLD_THRESHOLD == 80
        assert EVALUATE_THRESHOLD == 60
        assert WATCH_THRESHOLD == 40

    def test_signal_weights_sum_to_one(self):
        assert abs(sum(SIGNAL_WEIGHTS.values()) - 1.0) < 0.001

    def test_all_signals_present(self):
        assert len(SIGNAL_WEIGHTS) == 15
