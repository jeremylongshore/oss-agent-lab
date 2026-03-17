#!/usr/bin/env python3
"""Auto-scaffold a new specialist from a scored GitHub repo.

Usage:
    python scripts/generate_specialist.py owner/repo --name specialist_name

Copies _template/, populates from repo README/metadata, generates stubs.
"""

import argparse
import shutil
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "agents" / "specialists" / "_template"
SPECIALISTS_DIR = Path(__file__).parent.parent / "agents" / "specialists"


def scaffold_specialist(repo: str, name: str) -> Path:
    """Scaffold a new specialist directory from the template.

    Args:
        repo: GitHub repo in "owner/name" format.
        name: Specialist directory name (snake_case).

    Returns:
        Path to the new specialist directory.
    """
    target = SPECIALISTS_DIR / name
    if target.exists():
        raise FileExistsError(f"Specialist {name} already exists at {target}")

    shutil.copytree(TEMPLATE_DIR, target)
    print(f"Scaffolded {name} from template at {target}")
    print(f"Source repo: {repo}")
    print("Next steps:")
    print(f"  1. Edit {target}/agent.py — implement specialist class")
    print(f"  2. Edit {target}/tools.py — implement tools")
    print(f"  3. Edit {target}/SKILL.md — update metadata")
    print(f"  4. Add tests: tests/test_{name}.py")
    return target


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new specialist")
    parser.add_argument("repo", help="GitHub repo (owner/name)")
    parser.add_argument("--name", required=True, help="Specialist name (snake_case)")
    args = parser.parse_args()
    scaffold_specialist(args.repo, args.name)


if __name__ == "__main__":
    main()
