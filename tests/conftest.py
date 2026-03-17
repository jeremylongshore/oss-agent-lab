"""Shared test configuration — adds tests/ to import path for helpers."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure tests/ is importable so test modules can do `from helpers import make_request`
sys.path.insert(0, str(Path(__file__).parent))
