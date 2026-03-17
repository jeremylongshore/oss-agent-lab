"""
Score → action mapping for the Capability Scoring Engine.

Thresholds determine what happens when a repo is scored:
- AUTO_SCAFFOLD (80+): Immediately generate specialist skeleton + PR
- EVALUATE (60-79): Queue for human evaluation
- WATCH (40-59): Add to watch list, re-score weekly
- SKIP (<40): Not ready for wrapping
"""

AUTO_SCAFFOLD_THRESHOLD = 80
EVALUATE_THRESHOLD = 60
WATCH_THRESHOLD = 40

# Weight distribution for composite score
DISCOVERY_WEIGHT = 0.40  # "Is this trending?"
QUALITY_WEIGHT = 0.35  # "Is this production-ready?"
DURABILITY_WEIGHT = 0.25  # "Will this last?"

# Individual signal weights within each category
SIGNAL_WEIGHTS = {
    # Discovery signals (40%)
    "github_star_velocity": 0.15,
    "github_trending_position": 0.10,
    "hn_frontpage_score": 0.08,
    "devhunt_upvotes": 0.04,
    "rundown_mention": 0.03,
    # Quality signals (35%)
    "readme_quality": 0.08,
    "test_coverage": 0.08,
    "api_surface_clarity": 0.07,
    "license_compatibility": 0.05,
    "maintenance_activity": 0.07,
    # Durability signals (25%)
    "contributor_diversity": 0.06,
    "ossinsight_growth_curve": 0.06,
    "trendshift_momentum": 0.05,
    "dependency_health": 0.04,
    "community_depth": 0.04,
}

assert abs(sum(SIGNAL_WEIGHTS.values()) - 1.0) < 0.001, "Signal weights must sum to 1.0"
