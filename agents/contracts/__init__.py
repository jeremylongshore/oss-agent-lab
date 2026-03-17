"""Inter-agent contract schemas."""
# Contracts are defined in src/oss_agent_lab/contracts.py
# This module re-exports them for convenience within the agents package.
from oss_agent_lab.contracts import (
    Query,
    Intent,
    SpecialistRequest,
    SpecialistResponse,
    SessionContext,
)

__all__ = ["Query", "Intent", "SpecialistRequest", "SpecialistResponse", "SessionContext"]
