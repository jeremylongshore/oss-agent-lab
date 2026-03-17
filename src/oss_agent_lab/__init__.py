"""OSS Agent Lab - Turn trending repos into instant capabilities for any AI framework."""

__version__ = "0.1.0"

from oss_agent_lab.base import BaseSpecialist, Tool, OutputFormat
from oss_agent_lab.contracts import (
    Query,
    Intent,
    SpecialistRequest,
    SpecialistResponse,
    SessionContext,
)

__all__ = [
    "BaseSpecialist",
    "Tool",
    "OutputFormat",
    "Query",
    "Intent",
    "SpecialistRequest",
    "SpecialistResponse",
    "SessionContext",
]
