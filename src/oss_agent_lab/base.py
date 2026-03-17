"""Base specialist class and supporting types for OSS Agent Lab."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class OutputFormat(Enum):
    """Supported output formats for specialists."""

    PYTHON_API = "python_api"
    CLI = "cli"
    MCP_SERVER = "mcp_server"
    AGENT_SKILL = "agent_skill"
    REST_API = "rest_api"


@dataclass
class Tool:
    """A tool that a specialist can invoke during execution."""

    name: str
    description: str
    parameters: dict[str, Any] | None = field(default=None)


class BaseSpecialist(ABC):
    """Abstract base class for all specialists.

    Subclasses must define class attributes and implement the execute() method.

    Class Attributes:
        name: Short identifier for the specialist.
        description: Human-readable description of what it does.
        source_repo: GitHub owner/repo that this specialist wraps.
        capabilities: List of capability strings this specialist provides.
        output_formats: List of OutputFormat enums this specialist supports.
        tools: List of Tool instances available to this specialist.
    """

    name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    source_repo: ClassVar[str] = ""
    capabilities: ClassVar[list[str]] = []
    output_formats: ClassVar[list["OutputFormat"]] = []
    tools: ClassVar[list[Tool]] = []

    @abstractmethod
    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Execute the specialist's core capability.

        Args:
            request: The specialist request with intent, query, and parameters.

        Returns:
            SpecialistResponse with results.
        """
        ...

    def get_skill_metadata(self) -> dict[str, Any]:
        """Return SKILL.md-compatible metadata for this specialist.

        Returns:
            Dict with name, description, source_repo, capabilities,
            output_formats, and tools.
        """
        return {
            "name": self.name,
            "description": self.description,
            "source_repo": self.source_repo,
            "capabilities": self.capabilities,
            "output_formats": [fmt.value for fmt in self.output_formats],
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
                for tool in self.tools
            ],
        }

    def supports_format(self, fmt: OutputFormat) -> bool:
        """Check whether this specialist supports a given output format.

        Args:
            fmt: The OutputFormat to check.

        Returns:
            True if the format is supported, False otherwise.
        """
        return fmt in self.output_formats
