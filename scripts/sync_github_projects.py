#!/usr/bin/env python3
"""Sync beads tasks to GitHub Project board.

Reads .beads/issues.jsonl and creates/updates GitHub Project items
using the GraphQL API (via gh cli).

Usage:
    python scripts/sync_github_projects.py --dry-run   # preview
    python scripts/sync_github_projects.py              # sync all
"""

import argparse
import json
from pathlib import Path

BEADS_FILE = Path(".beads/issues.jsonl")


def load_beads() -> list[dict]:
    """Load beads issues from JSONL file."""
    if not BEADS_FILE.exists():
        print(f"No beads file found at {BEADS_FILE}")
        return []
    issues = []
    for line in BEADS_FILE.read_text().strip().split("\n"):
        if line:
            issues.append(json.loads(line))
    return issues


def sync_to_github(issues: list[dict], dry_run: bool = False) -> None:
    """Sync beads issues to GitHub Project board.

    Args:
        issues: List of beads issue dicts.
        dry_run: If True, print actions without executing.
    """
    raise NotImplementedError("GitHub Projects sync: Epic 0, Task 4")


def main():
    parser = argparse.ArgumentParser(description="Sync beads to GitHub Projects")
    parser.add_argument("--dry-run", action="store_true", help="Preview without syncing")
    args = parser.parse_args()
    issues = load_beads()
    print(f"Found {len(issues)} beads issues")
    sync_to_github(issues, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
