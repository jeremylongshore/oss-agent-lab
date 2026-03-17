"""OSS Agent Lab - Turn trending repos into instant capabilities for any AI framework."""

__version__ = "0.1.0"

from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import (
    Intent,
    Query,
    SessionContext,
    SpecialistRequest,
    SpecialistResponse,
)

__all__ = [
    "BaseSpecialist",
    "Intent",
    "OutputFormat",
    "Query",
    "SessionContext",
    "SpecialistRequest",
    "SpecialistResponse",
    "Tool",
]
