"""Tests for BaseSpecialist, Tool, and OutputFormat."""

from typing import ClassVar

import pytest

from oss_agent_lab.base import BaseSpecialist, OutputFormat, Tool
from oss_agent_lab.contracts import Intent, Query, SpecialistRequest, SpecialistResponse


class TestOutputFormat:
    def test_all_formats(self):
        assert len(OutputFormat) == 5
        expected = {"PYTHON_API", "CLI", "MCP_SERVER", "AGENT_SKILL", "REST_API"}
        assert {f.name for f in OutputFormat} == expected


class TestTool:
    def test_create(self):
        t = Tool(name="search", description="Search the web")
        assert t.name == "search"
        assert t.description == "Search the web"

    def test_with_parameters(self):
        t = Tool(name="search", description="Search", parameters={"query": "string"})
        assert t.parameters == {"query": "string"}


class ConcreteSpecialist(BaseSpecialist):
    """Test specialist implementation."""

    name = "test"
    description = "Test specialist"
    source_repo = "test/repo"
    capabilities: ClassVar[list[str]] = ["test_cap"]
    output_formats: ClassVar[list[OutputFormat]] = [OutputFormat.PYTHON_API]
    tools: ClassVar[list[Tool]] = [Tool(name="test_tool", description="A test tool")]

    async def execute(self, request: SpecialistRequest) -> SpecialistResponse:
        return SpecialistResponse(
            specialist_name=self.name,
            status="success",
            result={"test": True},
        )


class TestBaseSpecialist:
    def test_concrete_instantiation(self):
        s = ConcreteSpecialist()
        assert s.name == "test"
        assert len(s.capabilities) == 1

    def test_supports_format(self):
        s = ConcreteSpecialist()
        assert s.supports_format(OutputFormat.PYTHON_API)
        assert not s.supports_format(OutputFormat.MCP_SERVER)

    def test_get_skill_metadata(self):
        s = ConcreteSpecialist()
        meta = s.get_skill_metadata()
        assert meta["name"] == "test"
        assert meta["source_repo"] == "test/repo"

    @pytest.mark.asyncio
    async def test_execute(self):
        s = ConcreteSpecialist()
        intent = Intent(action="test", domain="test", confidence=1.0, parameters={})
        query = Query(user_input="test")
        req = SpecialistRequest(intent=intent, query=query, specialist_name="test")
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.result == {"test": True}
