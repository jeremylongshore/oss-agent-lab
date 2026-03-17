"""
Specialist Template — copy this directory to create a new specialist.

Usage:
    1. Copy _template/ to agents/specialists/your_specialist_name/
    2. Rename this class and update all attributes
    3. Implement the execute() method
    4. Write tools in tools.py
    5. Update SKILL.md with capabilities and allowed-tools
    6. Add tests in tests/test_your_specialist_name.py
"""
from typing import ClassVar

from oss_agent_lab import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import SpecialistRequest, SpecialistResponse


class TemplateSpecialist(BaseSpecialist):
    """Replace with your specialist description."""

    name = "template"
    description = "Template specialist — replace with actual description"
    source_repo = "owner/repo"
    capabilities: ClassVar[list[str]] = ["capability_1", "capability_2"]

    output_formats: ClassVar[list[OutputFormat]] = [
        OutputFormat.PYTHON_API,
        OutputFormat.CLI,
        OutputFormat.MCP_SERVER,
        OutputFormat.AGENT_SKILL,
        OutputFormat.REST_API,
    ]

    tools: ClassVar[list[Tool]] = [
        Tool(name="example_tool", description="Replace with actual tool description"),
    ]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        """Execute the specialist's core capability.

        Args:
            request: The specialist request with intent, query, and parameters.

        Returns:
            SpecialistResponse with results.
        """
        raise NotImplementedError("Implement this method in your specialist")
