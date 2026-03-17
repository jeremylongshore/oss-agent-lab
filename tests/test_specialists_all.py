"""Comprehensive integration tests for all 9 specialists."""

from __future__ import annotations

import pytest
from helpers import make_request

from oss_agent_lab.contracts import SpecialistResponse

# ---------------------------------------------------------------------------
# Browser AI
# ---------------------------------------------------------------------------


class TestBrowserAi:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.browser_ai.agent import BrowserAiSpecialist

        s = BrowserAiSpecialist()
        req = make_request(
            "browser_ai",
            "Scrape example.com",
            action="browse",
            domain="web",
            url="https://example.com",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "browser_ai"

    def test_attributes(self) -> None:
        from agents.specialists.browser_ai.agent import BrowserAiSpecialist

        s = BrowserAiSpecialist()
        assert s.name == "browser_ai"
        assert s.source_repo == "lightpanda-io/browser"
        assert len(s.tools) >= 3
        assert any(t.name == "navigate" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.browser_ai.tools import (
            extract_content,
            navigate,
            take_screenshot,
        )

        nav = navigate("https://example.com")
        assert "status_code" in nav
        assert "title" in nav
        assert "url" in nav

        content = extract_content("https://example.com")
        assert "content" in content
        assert "element_count" in content

        screenshot = take_screenshot("https://example.com")
        assert "screenshot_path" in screenshot
        assert "dimensions" in screenshot


# ---------------------------------------------------------------------------
# Knowledge Graph
# ---------------------------------------------------------------------------


class TestKnowledgeGraph:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.knowledge_graph.agent import KnowledgeGraphSpecialist

        s = KnowledgeGraphSpecialist()
        req = make_request(
            "knowledge_graph",
            "Build graph of repo dependencies",
            action="knowledge_graph",
            domain="code",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "knowledge_graph"

    def test_attributes(self) -> None:
        from agents.specialists.knowledge_graph.agent import KnowledgeGraphSpecialist

        s = KnowledgeGraphSpecialist()
        assert s.name == "knowledge_graph"
        assert len(s.tools) >= 3
        assert any(t.name == "build_graph" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.knowledge_graph.tools import (
            build_graph,
            find_relationships,
            query_graph,
        )

        graph = build_graph("test_source")
        assert "graph_id" in graph
        assert "node_count" in graph

        query_result = query_graph("test query")
        assert "results" in query_result

        rels = find_relationships("entity_a", "entity_b")
        assert "paths" in rels
        assert "relationship_types" in rels


# ---------------------------------------------------------------------------
# Stock Analyst
# ---------------------------------------------------------------------------


class TestStockAnalyst:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.stock_analyst.agent import StockAnalystSpecialist

        s = StockAnalystSpecialist()
        req = make_request(
            "stock_analyst",
            "Analyze AAPL",
            action="analyze",
            domain="finance",
            ticker="AAPL",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "stock_analyst"

    def test_attributes(self) -> None:
        from agents.specialists.stock_analyst.agent import StockAnalystSpecialist

        s = StockAnalystSpecialist()
        assert s.name == "stock_analyst"
        assert "finance" in s.capabilities or "analyze" in s.capabilities
        assert len(s.tools) >= 3
        assert any(t.name == "analyze_ticker" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.stock_analyst.tools import (
            analyze_ticker,
            news_sentiment,
            technical_indicators,
        )

        ticker_result = analyze_ticker("AAPL")
        assert "ticker" in ticker_result
        assert "recommendation" in ticker_result

        indicators = technical_indicators("AAPL")
        assert "ticker" in indicators
        assert "indicators_computed" in indicators

        sentiment = news_sentiment("AAPL")
        assert "ticker" in sentiment
        assert "overall_sentiment" in sentiment


# ---------------------------------------------------------------------------
# Opinion Analyst
# ---------------------------------------------------------------------------


class TestOpinionAnalyst:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.opinion_analyst.agent import OpinionAnalystSpecialist

        s = OpinionAnalystSpecialist()
        req = make_request(
            "opinion_analyst",
            "Analyze sentiment of this review",
            action="sentiment",
            domain="general",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "opinion_analyst"

    def test_attributes(self) -> None:
        from agents.specialists.opinion_analyst.agent import OpinionAnalystSpecialist

        s = OpinionAnalystSpecialist()
        assert s.name == "opinion_analyst"
        assert "sentiment" in s.capabilities
        assert len(s.tools) >= 3
        assert any(t.name == "analyze_sentiment" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.opinion_analyst.tools import (
            analyze_sentiment,
            detect_stance,
            measure_bias,
        )

        sent = analyze_sentiment("This product is great!")
        assert "sentiment" in sent
        assert "confidence" in sent
        assert "overall_score" in sent

        stance = detect_stance("I support this policy", "policy")
        assert "stance" in stance
        assert "confidence" in stance

        bias = measure_bias("This is clearly the best option ever!!!")
        assert "overall_bias_score" in bias
        assert "dimensions" in bias


# ---------------------------------------------------------------------------
# GUI Agent
# ---------------------------------------------------------------------------


class TestGuiAgent:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.gui_agent.agent import GuiAgentSpecialist

        s = GuiAgentSpecialist()
        req = make_request(
            "gui_agent",
            "Click the login button",
            action="gui_automation",
            domain="web",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "gui_agent"

    def test_attributes(self) -> None:
        from agents.specialists.gui_agent.agent import GuiAgentSpecialist

        s = GuiAgentSpecialist()
        assert s.name == "gui_agent"
        assert len(s.tools) >= 3
        assert any(t.name == "detect_elements" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.gui_agent.tools import (
            detect_elements,
            fill_form,
            interact_element,
        )

        elements = detect_elements("https://example.com")
        assert "elements" in elements
        assert "element_count" in elements

        interaction = interact_element("elem_1")
        assert "success" in interaction
        assert "action_performed" in interaction

        form = fill_form("https://example.com", {"username": "test"})
        assert "fields_filled" in form
        assert "success" in form


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------


class TestSandbox:
    @pytest.mark.asyncio
    async def test_execute(self) -> None:
        from agents.specialists.sandbox.agent import SandboxSpecialist

        s = SandboxSpecialist()
        req = make_request(
            "sandbox",
            "Run print('hello')",
            action="execute",
            domain="code",
        )
        resp = await s.execute(req)
        assert resp.status == "success"
        assert resp.specialist_name == "sandbox"

    def test_attributes(self) -> None:
        from agents.specialists.sandbox.agent import SandboxSpecialist

        s = SandboxSpecialist()
        assert s.name == "sandbox"
        assert "execute" in s.capabilities or "code_execution" in s.capabilities
        assert len(s.tools) >= 3
        assert any(t.name == "execute_code" for t in s.tools)

    def test_tools(self) -> None:
        from agents.specialists.sandbox.tools import (
            execute_code,
            list_runtimes,
            validate_code,
        )

        result = execute_code("print('hello')")
        assert "stdout" in result
        assert "exit_code" in result

        validation = validate_code("print('hello')")
        assert "valid" in validation
        assert "errors" in validation

        runtimes = list_runtimes()
        assert "runtimes" in runtimes
        assert "total_count" in runtimes


# ---------------------------------------------------------------------------
# All-specialist consistency checks
# ---------------------------------------------------------------------------

_ALL_SPECIALIST_CLASSES = [
    ("agents.specialists.autoresearch.agent", "AutoresearchSpecialist"),
    ("agents.specialists.swarm_predict.agent", "SwarmPredictSpecialist"),
    ("agents.specialists.deer_flow.agent", "DeerFlowSpecialist"),
    ("agents.specialists.browser_ai.agent", "BrowserAiSpecialist"),
    ("agents.specialists.knowledge_graph.agent", "KnowledgeGraphSpecialist"),
    ("agents.specialists.stock_analyst.agent", "StockAnalystSpecialist"),
    ("agents.specialists.opinion_analyst.agent", "OpinionAnalystSpecialist"),
    ("agents.specialists.gui_agent.agent", "GuiAgentSpecialist"),
    ("agents.specialists.sandbox.agent", "SandboxSpecialist"),
    ("agents.specialists.repo_scanner.agent", "RepoScannerSpecialist"),
]

_ALL_EXECUTE_CASES = [
    (
        "agents.specialists.autoresearch.agent",
        "AutoresearchSpecialist",
        "autoresearch",
        "Research AI safety",
    ),
    (
        "agents.specialists.swarm_predict.agent",
        "SwarmPredictSpecialist",
        "swarm_predict",
        "Predict market trends",
    ),
    ("agents.specialists.deer_flow.agent", "DeerFlowSpecialist", "deer_flow", "Generate a report"),
    (
        "agents.specialists.browser_ai.agent",
        "BrowserAiSpecialist",
        "browser_ai",
        "https://example.com",
    ),
    (
        "agents.specialists.knowledge_graph.agent",
        "KnowledgeGraphSpecialist",
        "knowledge_graph",
        "Build a code graph",
    ),
    (
        "agents.specialists.stock_analyst.agent",
        "StockAnalystSpecialist",
        "stock_analyst",
        "Analyze TSLA",
    ),
    (
        "agents.specialists.opinion_analyst.agent",
        "OpinionAnalystSpecialist",
        "opinion_analyst",
        "Check sentiment",
    ),
    ("agents.specialists.gui_agent.agent", "GuiAgentSpecialist", "gui_agent", "Click login button"),
    ("agents.specialists.sandbox.agent", "SandboxSpecialist", "sandbox", "Run hello world"),
    (
        "agents.specialists.repo_scanner.agent",
        "RepoScannerSpecialist",
        "repo_scanner",
        "test/trending-repo",
    ),
]


def _import_specialist(module_path: str, class_name: str) -> object:
    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)()


class TestAllSpecialistConsistency:
    """Verify all 10 specialists follow the same contract."""

    @pytest.mark.parametrize(
        "mod_path,cls_name",
        _ALL_SPECIALIST_CLASSES,
        ids=[c[1] for c in _ALL_SPECIALIST_CLASSES],
    )
    def test_has_required_attributes(self, mod_path: str, cls_name: str) -> None:
        s = _import_specialist(mod_path, cls_name)
        assert hasattr(s, "name") and len(s.name) > 0, f"{cls_name} missing/empty name"
        assert hasattr(s, "description"), f"{cls_name} missing description"
        assert hasattr(s, "source_repo"), f"{cls_name} missing source_repo"
        assert hasattr(s, "capabilities") and len(s.capabilities) >= 1, (
            f"{cls_name} no capabilities"
        )
        assert hasattr(s, "output_formats"), f"{cls_name} missing output_formats"
        assert hasattr(s, "tools") and len(s.tools) >= 1, f"{cls_name} no tools"

    @pytest.mark.parametrize(
        "mod_path,cls_name",
        _ALL_SPECIALIST_CLASSES,
        ids=[c[1] for c in _ALL_SPECIALIST_CLASSES],
    )
    def test_has_skill_metadata(self, mod_path: str, cls_name: str) -> None:
        s = _import_specialist(mod_path, cls_name)
        meta = s.get_skill_metadata()
        assert "name" in meta, f"{cls_name} metadata missing name"
        assert "source_repo" in meta, f"{cls_name} metadata missing source_repo"
        assert "capabilities" in meta, f"{cls_name} metadata missing capabilities"
        assert "tools" in meta, f"{cls_name} metadata missing tools"

    @pytest.mark.parametrize(
        "mod_path,cls_name,name,query",
        _ALL_EXECUTE_CASES,
        ids=[c[2] for c in _ALL_EXECUTE_CASES],
    )
    @pytest.mark.asyncio
    async def test_execute_successfully(
        self, mod_path: str, cls_name: str, name: str, query: str
    ) -> None:
        s = _import_specialist(mod_path, cls_name)
        req = make_request(name, query)
        resp = await s.execute(req)
        assert isinstance(resp, SpecialistResponse), f"{cls_name} didn't return SpecialistResponse"
        assert resp.status == "success", f"{cls_name} status={resp.status}"
        assert resp.specialist_name == name, (
            f"{cls_name} wrong specialist_name: {resp.specialist_name}"
        )
