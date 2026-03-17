"""Inter-agent contract schemas."""
# Contracts are defined in src/oss_agent_lab/contracts.py
# This module re-exports them for convenience within the agents package.
from oss_agent_lab.contracts import (
    Intent,
    Query,
    SessionContext,
    SpecialistRequest,
    SpecialistResponse,
)

__all__ = ["Intent", "Query", "SessionContext", "SpecialistRequest", "SpecialistResponse"]
